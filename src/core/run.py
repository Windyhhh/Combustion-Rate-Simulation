#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
燃烧速度仿真软件 - 核心计算引擎
Combustion Simulation Software - Core Calculation Engine
"""

import warnings
import time
import os
import melt_layer
import delta_layer
import cantera as ct
import numpy as np
import json
import argparse
import importlib.resources as pkg_resources
import tempfile

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def get_internal_file(package, filename):
    import importlib.resources as resources
    import tempfile
    import shutil
    import os

    with resources.path(package, filename) as res_path:
        # 创建临时路径副本（保持原样）
        tmp_dir = tempfile.gettempdir()
        dst_path = os.path.join(tmp_dir, os.path.basename(filename))
        shutil.copy(res_path, dst_path)
        return dst_path

def get_liquid_enthalpy(name, T, mech_file):
    with open(mech_file, 'r') as File:
        lines = File.readlines()
    flag1 = 0
    flag2 = 1
    for i in range(len(lines)):
        if 'THERMO' in lines[i]:
            flag1 = 1
        if flag1 == 1 and 'END' in lines[i]:
            flag2 = 0
        if flag1 == 1 and flag2 == 1:
            if lines[i].startswith(name + ' '):
                a1 = float(lines[i + 2][30:45])
                a2 = float(lines[i + 2][45:60])
                a3 = float(lines[i + 2][60:75])
                a4 = float(lines[i + 3][0:15])
                a5 = float(lines[i + 3][15:30])
                a6 = float(lines[i + 3][30:45])
                break
    H_RT = a1 + a2 * T / 2.0 + a3 * (T ** 2) / 3.0 + a4 * (T ** 3) / 4.0 + a5 * (T ** 4) / 5.0 + a6 / T
    H = H_RT * 1.9872 * T
    return H

def run_simulation_core(config_path, case_number=None):
    config = load_config(config_path)
    density = config['density']
    p = config['pressure'] * ct.one_atm * 10
    Tinit = config['Tinit']
    species_list = config['species']
    env_temp = config.get('environment_temp', Tinit)  # 没提供就默认等于 Tinit
    storage_time = config.get('storage_time', 0.0)    # years
    thermo_file = get_internal_file("../assets/resources", "log-file-data-minima.txt")
    mech_file = get_internal_file("../assets/resources", "chem-liquid-phase-mechanism.txt")
    yaml_file = get_internal_file("../assets/resources", "chem.yaml")
    species_names = set(s['name'] for s in species_list)
    allowed_species = {'NC(L)', 'NG(L)', 'ZDJ(L)', 'DINA(L)', 'DEP(L)'}
    species_list_use = [s for s in species_list if s['name'] in allowed_species]
    total_amount = sum(s['amount'] for s in species_list_use)
    print(density)
    print(config['pressure'])
    print(Tinit)
    print(species_list)
    print(env_temp)
    if total_amount > 0:
        for s in species_list_use:
            s['amount'] /= total_amount
    else:
        print("[WARNING] No valid species selected or total amount is zero.", flush=True)
    burn_rate = 0.3
    mdot_guess = density * burn_rate
    warnings.filterwarnings("ignore", message=".*NasaPoly2::validate.*", category=UserWarning)

    def pyrolysis_law(mdot):
        Es = 23250.0
        As = 7.0e6
        R = 1.9872
        Ts = -Es / R / np.log(mdot / As)
        return Ts

    parameters = {
        "mdot": mdot_guess,
        "Ts": pyrolysis_law(mdot_guess),
        "Tmelt": 553.0,
        "Tbeta2delta": 463.0,
        "Tinit": Tinit
    }

    with open('run.log', 'w') as File:
        File.writelines('%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s\n' %
                        ('Iteration', 'mdot(gm/cm2-s)', 'mdot_new(gm/cm2-s)', 'Tsurf(K)', 'Tsurf_new(K)',
                         'k_gas', 'dTdx_gas', 'k_liquid', 'dTdx_liquid', 'Yh_gas', 'Yh_liquid'))

    residual = 1.0
    iteration = 0

    while residual > 1e-3:
        iteration += 1
        print("Solving delta layer ..", flush=True)
        delta_layer.main(parameters, species_list_use)
        print("Solving melt layer ...", flush=True)
        Ts_liquid, Ysurf, lambda_liquid, dTdx_liquid, sum_Yh_liquid = melt_layer.main(mech_file, thermo_file, parameters, species_list_use)
        print("Melt layer solved", flush=True)
        print("Solving gas phase equations using cantera...", flush=True)
        print(parameters["Ts"])
        print(parameters["mdot"])
        tburner = parameters["Ts"]
        mdot = parameters["mdot"] * 100.0 * 100.0 / 1000.0
        reactants = {}
        width = 0.003
        loglevel = 1
        gas = ct.Solution(yaml_file)
        print(Ysurf)
        print(Ts_liquid)

        for item in Ysurf:
            if item in gas.species_names:
                reactants[item] = Ysurf[item]
            if item == 'c_HONO' or item == 't_HONO':
                reactants['HONO'] = Ysurf['c_HONO'] + Ysurf['t_HONO']
            if item == 'CH2NNO2':
                reactants['H2CNNO2'] = Ysurf[item]
            if item == 'INT202a' or item == 'INT202c':
                reactants['INT202a'] = Ysurf['INT202a'] + Ysurf['INT202c']
            if item == 'CH2N':
                reactants['H2CN'] = Ysurf[item]
            if item == 'CH2NH':
                reactants['H2CNH'] = Ysurf[item]
            if item == 'CH2NNO':
                reactants['H2CNNO'] = Ysurf[item]
            if item == 'N2H':
                reactants['NNH'] = Ysurf[item]
        print(Ysurf)
        print(reactants)
        print(reactants.values())
        factor = 1.0 / sum(reactants.values())
        for k in reactants:
            reactants[k] *= factor

        gas.TPY = tburner, p, reactants
        f = ct.BurnerFlame(gas, width=width)
        f.burner.mdot = mdot
        f.set_refine_criteria(ratio=3.0, slope=0.05, curve=0.1)
        f.transport_model = 'Mix'
        f.solve(loglevel, auto=True)
        f.write_csv('gas_phase_solution.csv', quiet=False)

        # 重命名CSV文件为工况X.CSV（如果提供了case_number）
        if case_number is not None:
            import shutil
            old_csv = 'gas_phase_solution.csv'
            new_csv = f'工况{case_number}.CSV'
            if os.path.exists(old_csv):
                shutil.move(old_csv, new_csv)
                print(f"CSV文件已重命名为: {new_csv}", flush=True)

        print("Gas phase equations solved", flush=True)

        lambda_dTdx_gas = f.thermal_conductivity[0] * (f.T[1] - f.T[0]) / (f.grid[1] - f.grid[0])
        dTdx_gas = (f.T[1] - f.T[0]) / (f.grid[1] - f.grid[0]) / 100.0
        lambda_dTdx_gas /= 4.184 * 100.0 * 100.0

        gas_surf = ct.Solution(yaml_file)
        gas_surf.TPY = tburner, p, reactants
        YH = np.multiply(gas_surf.Y, gas_surf.standard_enthalpies_RT * 1.9872 * tburner)
        Yh = np.divide(YH, gas_surf.molecular_weights)
        sum_Yh_gas = sum(Yh)

        sum_Yh_gas2 = 0
        sum_Yh_liquid2 = 0
        for i in range(gas_surf.n_species):
            y = gas_surf.Y[i]
            Hg = gas_surf.standard_enthalpies_RT[i] * 1.9872 * tburner
            name = gas_surf.species_names[i]
            Hl = get_liquid_enthalpy(name, tburner, mech_file) if y > 0 else 0.0
            sum_Yh_gas2 += y * Hg / gas_surf.molecular_weights[i]
            sum_Yh_liquid2 += y * Hl / gas_surf.molecular_weights[i]

        mdot_new2 = (lambda_dTdx_gas - lambda_liquid * dTdx_liquid) / (sum_Yh_gas2 - sum_Yh_liquid2)

        with open('run.log', 'a') as File:
            File.writelines('%15d %15.5f %15.5f %15.2f %15.2f %15.3E %15.3E %15.3E %15.3E %15.3E %15.3E\n' %
                            (iteration, parameters["mdot"], mdot_new2, tburner, pyrolysis_law(mdot_new2),
                             f.thermal_conductivity[0] / 4.184 / 100.0, dTdx_gas,
                             lambda_liquid, dTdx_liquid, sum_Yh_gas, sum_Yh_liquid))

        residual = abs(mdot_new2 - parameters["mdot"])
        RHS = lambda_dTdx_gas
        LHS = lambda_liquid * dTdx_liquid + parameters["mdot"] * sum_Yh_gas2 - parameters["mdot"] * sum_Yh_liquid2

        if RHS > LHS:
            parameters["mdot"] = (parameters["mdot"] + mdot_new2) / 2.0 if parameters["mdot"] * 1.05 > mdot_new2 else parameters["mdot"] * 1.05
        else:
            parameters["mdot"] = (parameters["mdot"] + mdot_new2) / 2.0 if parameters["mdot"] * 0.95 < mdot_new2 else parameters["mdot"] * 0.95

        parameters["Ts"] = pyrolysis_law(parameters["mdot"])

    print("Solution converged", flush=True)

    BR0 = float(mdot_new2 / density * 10)
    P = p / ct.one_atm / 10
    t = config.get('storage_time', 0.0)  # 储存时间（天）

    # 使用校正公式.txt中的拟合公式
    import math

    # 检查配方类型并应用相应的校正公式
    daq_mg_species = {"DAQ-Mg-1", "DAQ-Mg-2", "DAQ-Mg-3", "DAQ-Mg-4"}
    daq_present = [k for k in daq_mg_species if k in species_names]

    if "DAQ-Mg-1" in species_names:
        # 配方有DAQ-Mg-1的矫正公式
        BR = (13.2482176 + (-72.3032366)*BR0 + 48.3218690*BR0*math.log(P) +
              (-4.29106529)*BR0*P + (-0.144720157)*BR0*t + 0.00285901990*BR0*t*t +
              0.0633118343*BR0*math.log(P)*t + (-0.00143936278)*BR0*math.log(P)*t*t)

    elif "DAQ-Mg-2" in species_names:
        # 配方有DAQ-Mg-2的矫正公式
        BR = (0.9247804 + (82.5029852)*BR0 + (-37.6814567)*BR0*math.log(P) +
              1.47249469*BR0*P + (-0.244910389)*BR0*t + 0.00552162*BR0*t*t +
              0.10517283*BR0*math.log(P)*t + (-0.00252195)*BR0*math.log(P)*t*t)

    elif "DAQ-Mg-3" in species_names:
        # 配方有DAQ-Mg-3的矫正公式
        BR = (9.9297577 + (-27.9826899)*BR0 + (26.0715628)*BR0*math.log(P) +
              (-3.0970097)*BR0*P + (-0.03552933)*BR0*t + (-0.00388921)*BR0*t*t +
              0.01086682*BR0*math.log(P)*t + 0.00147458*BR0*math.log(P)*t*t)

    elif "DAQ-Mg-4" in species_names:
        # 配方有DAQ-Mg-4的矫正公式
        BR = (7.63385483 + 13.7409387*BR0 - 2.63613349*BR0*math.log(P) -
              0.45326854*BR0*P - 0.19874803*BR0*t + 0.00294844*BR0*t*t +
              0.07411378*BR0*math.log(P)*t - 0.00126397*BR0*math.log(P)*t*t)

    elif "MgO" in species_names:
        # 配方有MgO的矫正公式
        BR = (6.3951 - 1.6214*P + 53.8521*BR0 + 0.1125*P*P +
              23.8282*BR0*BR0 - 6.6542*P*BR0)

    elif species_names - allowed_species:
        # 配方不含有MgO、DAQMg-1234物种催化剂但是含有其他物质的矫正公式
        BR = (-15.4593 + 11.3201*P - 68.8526*BR0 - 1.1014*P*P -
              29.2069*BR0*BR0 + 11.8364*P*BR0)

    else:
        # 配方只含有NG、NC、ZDJ、DEP、DINA五种物种的矫正公式
        BR = (-2.2086 + 2.4852*P - 5.7508*BR0 - 0.3645*P*P -
              9.7405*BR0*BR0 + 3.5544*P*BR0)
    if os.path.exists("run.log"):
        os.remove("run.log")
    
    print("Burn-rate = %.4f mm/s" % BR, flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True, help='Path to config_input.json')
    parser.add_argument('--case', type=int, help='Case number for CSV file naming')
    args = parser.parse_args()
    run_simulation_core(args.config, args.case)

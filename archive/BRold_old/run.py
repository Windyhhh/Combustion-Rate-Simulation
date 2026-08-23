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

def run_simulation_core(config_path):
    config = load_config(config_path)
    density = config['density']
    p = config['pressure'] * ct.one_atm * 10
    Tinit = config['Tinit']
    species_list = config['species']
    env_temp = config.get('environment_temp', Tinit)  # 没提供就默认等于 Tinit
    storage_time = config.get('storage_time', 0.0)    # years
    thermo_file = get_internal_file("resources", "log-file-data-minima.txt")
    mech_file = get_internal_file("resources", "chem-liquid-phase-mechanism.txt")
    yaml_file = get_internal_file("resources", "chem.yaml")
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

    # 四种 DAQ-Mg 的线性拟合系数：BR = a * P + b * BR0
    daq_mg_coeffs = {
        "DAQ-Mg-1": (3.0,  -22.0),
        "DAQ-Mg-2": (3.4,  -24.9),
        "DAQ-Mg-3": (3.4,  -25.1),
        "DAQ-Mg-4": (3.2,  -23.1),
    }

    daq_present = [k for k in daq_mg_coeffs if k in species_names]

    if 'MgO' in species_names:
        # MgO 逻辑保持不变
        BR = 2.5 * P - 15 * BR0 if P <= 12 else -15 * BR0 / P + 1.8 * BR0 + 4.5

    elif daq_present:
        # 正常来说 GUI 已经保证四选一；这里再做一下兜底
        if len(daq_present) > 1:
            print(f"[WARN] Multiple DAQ-Mg detected: {daq_present}. Using {daq_present[0]}.", flush=True)
        a, b = daq_mg_coeffs[daq_present[0]]
        BR = a * P + b * BR0

    elif species_names - allowed_species:
        # 其他添加剂情形（沿用你原先的校正因子）
        BR = (2.5 * P - 15 * BR0) / 1.155

    else:
        # 基线情形
        BR = 0.45 * P + 0.5 * BR0 + 1.0
    if os.path.exists("run.log"):
        os.remove("run.log")
    # ===== 在基础 BR 分支判断计算完毕后，追加老化二次矫正 =====
    # t：储存时间（天），从 config 传入时写入了 parameters / 或 config 中
    # 这里直接读 config（或你也可以从 parameters 里传下来的值用同名变量）
    t = config.get('storage_time', 0.0)

    # 识别是否属于四种 DAQ-Mg 中的一种（GUI 已互斥；若不放心可做兜底）
    daq_mg_coeffs = {
        "DAQ-Mg-1": ( 0.001118481, 0.0000583789,  0.00189013),   # BR = BR*(1 - a*t - b*t^2) + c*(P-9)*t
        "DAQ-Mg-2": ( 0.001304810, 0.0000238644,  0.001191906),
        "DAQ-Mg-3": ( 0.000415000, 0.0002280000, -0.000729000),
        "DAQ-Mg-4": ( 0.000151000, 0.0001950000, -0.002080000),
    }
    daq_present = [k for k in daq_mg_coeffs if k in species_names]

    if daq_present:
        if len(daq_present) > 1:
            print(f"[WARN] Multiple DAQ-Mg detected in aging step: {daq_present}. Using {daq_present[0]}.", flush=True)
        a, b, c = daq_mg_coeffs[daq_present[0]]
        BR = BR * (1.0 - a * t - b * t * t) + c * (P - 9.0) * t
    else:
        # 其他配方（含 MgO、无添加、或其他添加剂）使用通用老化公式
        # BR = BR*(1 - 5.4e-4*t - 1.26e-4*t^2) - 1.82e-4*(P-9)*t
        BR = BR * (1.0 - 5.4e-4 * t - 1.26e-4 * t * t) - 1.82e-4 * (P - 9.0) * t
    
    print("Burn-rate = %.4f mm/s" % BR, flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, required=True, help='Path to config_input.json')
    args = parser.parse_args()
    run_simulation_core(args.config)

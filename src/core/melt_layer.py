from typing import List

import numpy as np
import scipy.integrate
from Phase import Phase


class Pyphase:
    def __init__(self, file1, file2):
        self.liquidphase = Phase(file1, file2)

    @property
    def get_T(self):
        return self.liquidphase.get_T

    @get_T.setter
    def set_T(self, value):
        self.liquidphase.set_T = value
        self.liquidphase.set_density = self.get_density
        self.liquidphase.set_viscosity = self.get_viscosity
        self.liquidphase.set_conductivity = self.get_conductivity

    @property
    def get_P(self):
        return self.liquidphase.get_P

    @get_P.setter
    def set_P(self, value):
        self.liquidphase.set_P = value

    @property
    def get_density(self):
        T = [550.0, 600.0, 650.0, 700.0, 750.0, 800.0]
        rho = [1.6509, 1.6144, 1.5869, 1.5545, 1.5201, 1.4882]
        return np.interp(self.get_T, T, rho)

    @get_density.setter
    def set_density(self, value):
        self.liquidphase.set_density = value

    @property
    def get_viscosity(self):
        T = [550.0, 600.0, 650.0, 700.0, 750.0, 800.0]
        eta = [0.45, 0.12, 0.04, 0.0220, 0.01, 0.0055]
        # viscosity in g/cm-s
        return 10.0 * np.interp(self.get_T, T, eta)

    @get_viscosity.setter
    def set_viscosity(self, value):
        self.liquidphase.set_viscosity = value

    @property
    def get_conductivity(self):
        self.conductivity = 1.5e-3 - 0.115e-5 * self.get_T
        return self.conductivity

    @get_conductivity.setter
    def set_conductivity(self, value):
        self.liquidphase.set_conductivity = value

    @property
    def n_species(self):
        return self.liquidphase.get_n_species()

    @property
    def n_reactions(self):
        return self.liquidphase.get_n_reactions()

    def species_name(self, k):
        return self.liquidphase.species_name(k)

    def reaction_name(self, k):
        return self.liquidphase.reaction_name(k)

    def species_index(self, name):
        return self.liquidphase.species_index(name)

    @property
    def Eaf(self):
        return self.liquidphase.get_Eaf

    """    
    @property
    def Eab(self):
        return self.liquidphase.get_Eab()
    """

    @property
    def get_X(self):
        return self.liquidphase.getX()

    @get_X.setter
    def set_X(self, values):
        self.liquidphase.setX(values)

    @property
    def get_Y(self):
        return self.liquidphase.getY()

    @get_Y.setter
    def set_Y(self, values):
        self.liquidphase.setY(values)

    @property
    def molecular_weights(self):
        return self.liquidphase.get_molecular_weight()

    @property
    def mean_molecular_weight(self):
        return self.liquidphase.get_mean_molecular_weight()

    @property
    def concentrations(self):
        return self.liquidphase.get_concentrations()

    @property
    def forward_rate_constants(self):
        return self.liquidphase.get_forward_rate_constants()

    @property
    def backward_rate_constants(self):
        return self.liquidphase.get_backward_rate_constants()

    """
    @property
    def kdiff_f(self):
        return self.liquidphase.get_kdiff_f()
    
    @property
    def kdiff_b(self):
        return self.liquidphase.get_kdiff_b()
    
    @property
    def kdiff(self):
        return np.asarray(self.liquidphase.get_kdiff())
    """

    @property
    def net_forward_rate_constants(self):
        return self.liquidphase.get_net_forward_rate_constants()

    @property
    def net_backward_rate_constants(self):
        return self.liquidphase.get_net_backward_rate_constants()

    def reactants_list(self, k):
        return [item for item in list(self.liquidphase.get_reactants_list(k))]

    def products_list(self, k):
        return [item for item in list(self.liquidphase.get_products_list(k))]

    @property
    def net_rates_of_production(self):
        return self.liquidphase.get_net_rates_of_production()

    @property
    def Cp(self):
        return self.liquidphase.get_Cps()

    @property
    def H(self):
        return self.liquidphase.get_enthalpies()

    @property
    def mean_Cp(self):
        return self.liquidphase.get_Cpbar()


#########################################################################################################
class ReactorOde:
    def __init__(self, liquid, mass_flux):
        self.liquid = liquid
        self.mass_flux = mass_flux

    def __call__(self, x, y):
        """
        the ODE function, y' = f(t,y)
        y[0]                = T                 # temperature
        y[1]                = dT/dx             # temperature gradient
        y[2:2+self.liquid.n_species]    = Y     # Species mass fractions
        """

        mdot = self.mass_flux
        n_species = self.liquid.n_species
        self.liquid.set_T = y[0]

        y = np.asarray([max([y_i, 0.0]) for y_i in y])
        y[2:2 + n_species] = y[2:2 + n_species] / sum(y[2:2 + n_species])
        self.liquid.set_Y = y[2:2 + n_species]
        wdot = np.asarray(self.liquid.net_rates_of_production)

        # governing equations
        dTdx = y[1]
        d2Tdx2 = (mdot * self.liquid.mean_Cp * y[1] / self.liquid.mean_molecular_weight +
                 np.sum(np.multiply(wdot, self.liquid.H))) / self.liquid.conductivity
        dYdx = np.multiply(wdot, self.liquid.molecular_weights) / mdot
        return np.hstack((dTdx, d2Tdx2, dYdx))

def main(file1, file2, parameters, species_list_use):

    liquid = Pyphase(file1, file2)

    mdot = parameters["mdot"]
    Ts = parameters["Ts"]
    Tmelt = parameters["Tmelt"]
    Tinit = parameters["Tinit"]

    liquid.set_T = Tmelt
    n_species = liquid.n_species

    x: list[float] = []
    amount_dict = {s['name']: s['amount'] for s in species_list_use}
    for i in range(n_species):
        name = liquid.species_name(i)
        x.append(amount_dict.get(name, 0.0))
        print(x)


    liquid.set_X = x
    # print('get_Y output is', liquid.get_Y)
    # print('get_Y output is', liquid.get_Y)
    # dTdx from energy balance of solid phase

    # Specific heat of solid HMX in cal/g-K
    # Reference: Beckstead et al. Progress in energy science and combustion 33 (2007) 497-551
    # Cp_solid = 4.980e-2 + 0.660e-3*T
    # integral_Cp_dt = 4.980e-2*(Tmelt-Tinit) + 0.660e-3*((Tmelt**2)-(Tinit**2))/2.0

    # Enthalpy of melting of HMX in kcal/mol plus enthalpy of phase change for integral enegery balance in solid phase
    # Reference: Beckstead et al. Progress in energy science and combustion 33 (2007) 497-551
    dHmelting = 16.7 + 2.35        # kcal/mol
    integral_Cp_dt = 4.920e-2 * (Tmelt - Tinit) + 0.660e-3 * (
            (Tmelt ** 2) - (Tinit ** 2)) / 2.0
    for s in species_list_use:
        MW = s['molecular_weight']  # 请确保 species_list_use 中包含 'MW' 字段
#        integral_Cp_dt += dHmelting * 1000 / MW * s['normalized_content']
        integral_Cp_dt += dHmelting * 1000 / MW
    print(MW)

    dTdx = mdot * integral_Cp_dt / liquid.get_conductivity

    y0 = np.hstack((liquid.get_T, dTdx, liquid.get_Y))
    # for i in range(n_species + 2):
    #     if i == 0:
    #         y0.append(liquid.get_T)
    #     elif i == 1:
    #         y0.append(dTdx)
    #     else:
    #         y0.append(liquid.get_Y[i - 2])

    # Set up objects representing the ODE and the solver
    ode = ReactorOde(liquid, mdot)
    solver = scipy.integrate.ode(ode)
    solver.set_integrator('vode', method='bdf', with_jacobian=True, atol=1e-12, rtol=1e-6, nsteps=10000)
    solver.set_initial_value(y0, 0.0)

    # Integrate the equations, keeping T(t) and Y(k,t)
    dx = 0.00001

    mass_fractions_liquid = []

    iNC = liquid.species_index('NG(L)')
    header = '%15s %15s %15s' % ('x(cm)', 'Temp(K)', 'dT/dx')
    for i in range(n_species):
        header = header + '%15s' % (liquid.species_name(i))
    header = header + '\n'

    # print(mdot)
    # print(liquid.mean_Cp)
    # print(solver.y[0])
    # print(liquid.mean_molecular_weight)
    # print(np.asarray(liquid.net_rates_of_production))
    # print(liquid.H)
    # print(liquid.conductivity)

    with open('mass_fractions_liquid.txt', 'w') as File:
        File.writelines(header)

    while solver.successful() and solver.y[0] < Ts - 0.05:
        liquid.T = solver.y[0]
        Ts_liquid = solver.y[0]
        dTdx = solver.y[1]

        Yjc = np.asarray([max([solver.y[i], 0.0]) for i in range(len(solver.y))])
        liquid.Y = Yjc[2:2 + n_species] / sum(Yjc[2:2 + n_species])

        line_liquid = '%15.6f %15.3f %15.3E' % (solver.t, solver.y[0], dTdx)
        h = np.divide(liquid.H, liquid.molecular_weights)

        for i in range(n_species):

            line_liquid = line_liquid + '%15.3E' % (liquid.get_Y[i])

        line_liquid = line_liquid + '\n'

        with open('mass_fractions_liquid.txt', 'a') as File:
            File.writelines(line_liquid)

        solver.integrate(solver.t + dx)

    Ysurf = {}

    for i in range(n_species):
        Ysurf[liquid.species_name(i)] = Yjc[i + 2] / sum(Yjc[2:2 + n_species])

    return Ts_liquid, Ysurf, liquid.conductivity, dTdx, sum(np.multiply(Yjc[2:2 + n_species] / sum(Yjc[2:2 + n_species]), h))

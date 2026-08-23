from Species import Species
from Reactions import Reactions
import math
import numpy as np


class Phase:
	def __init__(self, file1, file2):
		# Default initialization, CGS unit is used
		self.T = 298.15
		self.P = 1013250.0
		self.density = 1.0
		self.viscosity = 1.0
		self.elements = []
		self.species = []
		self.reactions = []

		# read elements, species and reactions
		with open(file1, 'r', ) as infile1:
			flag_elements, flag_species, flag_reactions = 0, 0, 0
			line_number = 1
			line1, line2, line3, line4 = '', '', '', ''

			for line in infile1:
				# print(line)
				sline = line.strip()
				if sline == 'ELEMENTS':
					flag_elements = 1
				if sline == 'THERMO':
					flag_species = 1
				if sline == 'REACTIONS':
					flag_reactions = 1
				if flag_elements and sline not in ["ELEMENTS", "END"]:
					self.elements.append(sline)
				if flag_species and sline not in ["THERMO", "END"]:
					if line_number == 1:
						line1 = sline
					elif line_number == 2:
						line2 = line
					elif line_number == 3:
						line3 = line
					elif line_number == 4:
						line4 = line
						self.species.append(Species(line1, line2, line3, line4))
					line_number += 1
					if line_number == 5:
						line_number = 1

				if flag_reactions and sline not in ["REACTIONS", "END"]:
					if sline[0] != '!':
						self.reactions.append(Reactions(sline))

				if sline == 'END':
					flag_elements, flag_species, flag_reactions = 0, 0, 0

		# check for duplicate species and reactions (rude),and unused species or missing species
		for i, spec_i in enumerate(self.species):
			for j, spec_j in enumerate(self.species):
				if j != i and spec_j.name == spec_i.name:
					errmsg = f"Duplicate species found: {spec_j.name}"
					raise ValueError(errmsg)

		for i, react_i in enumerate(self.reactions):
			for j, react_j in enumerate(self.reactions):
				if j != i and react_j.name == react_i.name:
					errmsg = f"Duplicate reaction found: {react_j.name}"
					raise ValueError(errmsg)

		for spec in self.species:
			sfound = 0
			for react in self.reactions:
				if spec.name in react.reactants_list or spec.name in react.products_list:
					sfound = 1
					break

			if sfound == 0 and spec.name not in ['N2', 'NO2', 'CH2O']:
				errmsg = f"Redundant/unused species found: {spec.name}"
				raise ValueError(errmsg)

		# create a list of molecular weights
		self.molecular_weights = [spec.molecular_weight for spec in self.species]

		# create vectors for conversion factors, symmetry factors, imaginary frequencies and activation barriers of reactions
		kcal = 1000.0
		self.All_img_freq = []
		self.All_for_sym = []
		self.All_for_conv = []
		self.All_back_sym = []
		self.All_back_conv = []
		self.Eaf = []
		self.Eab = []

		for react in self.reactions:
			self.All_img_freq.append(react.img_freq)

			self.All_for_sym.append(react.for_sym)
			self.All_for_conv.append(react.for_conv)

			self.All_back_sym.append(react.back_sym)
			self.All_back_conv.append(react.back_conv)

		# use dHf and dHb for bond breaking reactions
		# which are identified using (dGf < 1e-10 or dGb < 1e-10) and (frequency of TS < 15 cm-1)
			if ((react.dGf < 1e-10 or react.dGb < 1e-10)) and react.img_freq < 15.0:
				if len(react.reactants_list) == 1 or len(react.products_list) == 1:
					self.Eaf.append(react.dHf + react.ff*kcal)
					self.Eab.append(react.dHb + react.fb*kcal)
				else:
					if react.dGf < 1e-10:
						self.Eaf.append(react.ff*kcal)
						self.Eab.append(react.dGb + react.fb*kcal)
					elif react.dGb < 1e-10:
						self.Eaf.append(react.dGf + react.ff*kcal)
						self.Eab.append(react.fb*kcal)
			else:
				self.Eaf.append(react.dGf + react.ff*kcal)
				self.Eab.append(react.dGb + react.fb*kcal)

		# create vectors for reactants and products stoichiometric coeffs
		self.reactants_stoic_coeffs = []
		self.products_stoic_coeffs = []
		for i in range(len(self.reactions)):
			self.reactants_stoic_coeffs.append([0] * len(self.species))
			self.products_stoic_coeffs.append([0] * len(self.species))
			for reactant in self.reactions[i].reactants_list:
				index = self.species_index(reactant)
				self.reactants_stoic_coeffs[i][index] += 1

			for product in self.reactions[i].products_list:
				index = self.species_index(product)
				self.products_stoic_coeffs[i][index] += 1

		# read species radius
		# read in as angstrom and converted to cm
		with open(file2, 'r') as infile2:
			temp_names = []
			temp_radius = []
			line_number = 1

			for line in infile2:
				if line_number > 2:
					parts = line.strip().split()
					name = parts[0]
					rad_str = [s for s in parts if "mol)" in s][0]
					index = parts.index(rad_str)
					rad = float(parts[index+1])

					temp_names.append(name)
					temp_radius.append(rad)

				line_number += 1

		for spec in self.species:
			for name, radius in zip(temp_names, temp_radius):
				if spec.name == name:
					spec.radius = 1.0e-8*radius

		# create matrix for diffusion rate constants coefficients
		# each element of kmat is kdiff divided by T/viscosity.
		# The T/viscosity factor is multiplied to kmat in calculating kdiff
		kmat_reactant = []
		kmat_product = []

		# Boltzmann constant KB in CGS and Avagadro number NA
		kB = 1.38064852e-16
		NA = 6.022140857e23
		Rsum = 0.0

		max_reactants = max(len(reaction.reactants_list) for reaction in self.reactions)
		max_products = max(len(reaction.products_list) for reaction in self.reactions)

		if max_reactants > 2 or max_products > 3:
			errmsg = "Maxinum number of reactants > 2 or products > 3: check Warnings"
			raise ValueError(errmsg)

		for reaction in self.reactions:
			if len(reaction.reactants_list) > 1:
				Rsum = 0.0
				reactant_values = []
				for j in range(len(reaction.reactants_list)-1):
					reactant_values.append([0.0, 0.0])	# initialize with two zeros
					Rsum += self.species[self.species_index(reaction.reactants_list[j])].radius
					reactant_values[j][0] = (2.0 * NA * kB / 3.0) * (
								Rsum + self.species[self.species_index(reaction.reactants_list[j + 1])].radius) * (1.0 / Rsum + 1.0 /
										  self.species[self.species_index(reaction.reactants_list[j + 1])].radius)
					reactant_values[j][1] = (kB / 2.0 / 3.14) * (
								1.0 / Rsum + 1.0 / self.species[self.species_index(reaction.reactants_list[j + 1])].radius) / (Rsum + self.species[self.species_index(reaction.reactants_list[j + 1])].radius) ** 2
				kmat_reactant.append(reactant_values)
			else:
				kmat_reactant.append([])

			if len(reaction.products_list) > 1:
				Rsum = 0.0
				product_values = []
				for j in range(len(reaction.products_list) - 1):
					product_values.append([0.0, 0.0])
					Rsum += self.species[self.species_index(reaction.products_list[j])].radius
					product_values[j][1] = (2.0 * NA * kB / 3.0) * (
								Rsum + self.species[self.species_index(reaction.products_list[j + 1])].radius) * (
													   1.0 / Rsum + 1.0 / self.species[ self.species_index(reaction.products_list[j + 1])].radius)
					product_values[j][0] = (kB / 2.0 / 3.14) * (
								1.0 / Rsum + 1.0 / self.species[self.species_index(reaction.products_list[j + 1])].radius) / (Rsum + self.species[self.species_index(reaction.products_list[j + 1])].radius) ** 2
				kmat_product.append(product_values)
			else:
				kmat_product.append([])

		self.kmat_reactant = kmat_reactant
		self.kmat_product = kmat_product

		kcal = 1000.0

		for i in range(len(self.reactions)-1):
			self.Eaf[i] += 0.0 * kcal
			self.Eab[i] += 0.0 * kcal


	# Getter and setter for T, P, density and viscosity
	@property
	def get_T(self):
		return self.T

	@get_T.setter
	def set_T(self, value):
		self.T = value

	@property
	def get_P(self):
		return self.P

	@get_P.setter
	def set_P(self, value):
		self.P = value

	@property
	def get_density(self):
		return self.density

	@get_density.setter
	def set_density(self, value):
		self.density = value

	@property
	def get_viscosity(self):
		return self.viscosity

	@get_viscosity.setter
	def set_viscosity(self, value):
		self.viscosity = value

	@property
	def get_conductivity(self):
		return self.conductivity

	@get_conductivity.setter
	def set_conductivity(self, value):
		self.conductivity = value

	def get_n_species(self):
		return len(self.species)

	def get_n_reactions(self):
		return len(self.reactions)

	def species_name(self, k):
		return self.species[k].name

	def reaction_name(self, k):
		return self.reactions[k].name

	def species_index(self, inputname):
		for idx, s in enumerate(self.species):
			if s.name == inputname:
				return idx

		errmsg = f"Species missing: {inputname}"
		raise ValueError(errmsg)

	def reaction_index(self, inputname):
		for idx, s in enumerate(self.reactions):
			if s.name == inputname:
				return idx

		errmsg = f"Reaction missing: {inputname}"
		raise ValueError(errmsg)

	def get_molecular_weight(self):
		return self.molecular_weights

	def get_reactants_list(self, k):
		return self.reactions[k].reactants_list

	def get_products_list(self, k):
		return self.reactions[k].products_list

	def get_Eaf(self):
		return self.Eaf

	def get_Eab(self):
		return self.Eab

	def setX(self, values):
		self.X = values
		self.mean_molecular_weight = sum(x*mw for x, mw in zip(self.X, self.molecular_weights))
		self.Y = [x*mw/self.mean_molecular_weight for x, mw in zip(self.X, self.molecular_weights)]
		self.concentrations = [x*self.density/self.mean_molecular_weight for x in self.X]

	def getX(self):
		return self.X

	def setY(self, values):
		self.Y = values
		sum_value = sum(y/mw for y, mw in zip(self.Y, self.molecular_weights))
		self.mean_molecular_weight = 1.0/sum_value
		self.X = [y*self.mean_molecular_weight/mw for y, mw in zip(self.Y, self.molecular_weights)]
		self.concentrations = [x*self.density/self.mean_molecular_weight for x in self.X]

	def getY(self):
		return self.Y

	def get_mean_molecular_weight(self):
		return self.mean_molecular_weight

	def get_concentrations(self):
		return self.concentrations

	# Getter setter for temperature dependent data members
	def get_forward_rate_constants(self):

		self.forward_rate_constants = []

		h_planck = 6.626e-27
		kB = 1.38064852e-16
		R = 1.9872036

		for i in range(len(self.reactions)):
			wigner = 1.0 + (1.0/24.0)*math.pow((h_planck*self.All_img_freq[i]*2.99792458e10/kB/self.T), 2.0)
			self.forward_rate_constants.append(
				(self.All_for_conv[i]*self.All_for_sym[i]*wigner*kB*self.T/h_planck)*math.exp(-self.Eaf[i]/(R*self.T))
			)
		return self.forward_rate_constants

	def get_backward_rate_constants(self):
		self.backward_rate_constants = []

		h_planck = 6.626e-27
		kB = 1.38064852e-16
		R = 1.9872036

		for i in range(len(self.reactions)):
			wigner = 1.0 + (1.0/24.0)*math.pow((h_planck*self.All_img_freq[i]*2.99792458e10/kB/self.T), 2.0)
			self.backward_rate_constants.append(
				(self.All_back_conv[i]*self.All_back_sym[i]*wigner*kB*self.T/h_planck)*math.exp(-self.Eab[i]/(R*self.T)))

		return self.backward_rate_constants

	# def get_kdiff_f(self):
	# 	return self.kdiff_f
	#
	# def get_kidff_b(self):
	# 	return self.kdiff_b

	def get_kdiff(self):
		# Only handles 2 reactants and 3 products
		# Need modifications to handle more reactants and products
		# make sure mechanism file has maximum of 2 reactants and 3 products
		self.kdiff = [[] for _ in self.reactions]
		k_prod = [[] for _ in self.reactions]
		k_reac = [[] for _ in self.reactions]

		for i in range(len(self.reactions)):
			k_prod[i] = [0, 0]
			num_products = len(self.reactions[i].products_list)
			if num_products == 1:
				k_prod[i][0] = 1e30
				k_prod[i][1] = 1e30
			elif num_products == 2:
				k_prod[i][0] = self.kmat_product[i][0][0] * self.T / self.viscosity
				k_prod[i][1] = self.kmat_product[i][0][1] * self.T / self.viscosity
			else:
				conc_E = self.concentrations[self.species_index(self.reactions[i].products_list[2])]
				k_prod[i][0] = (self.T / self.viscosity) * self.kmat_product[i][0][0] * self.kmat_product[i][1][0] /\
							   (self.kmat_product[i][1][0] + self.kmat_product[i][0][1] * conc_E)
				k_prod[i][1] = (self.T / self.viscosity) * self.kmat_product[i][0][1] * self.kmat_product[i][1][1] /\
							   (self.kmat_product[i][1][0] + self.kmat_product[i][0][1] * conc_E)

		for i in range(len(self.reactions)):
			k_reac[i] = [0, 0]
			num_reactant = len(self.reactions[i].reactants_list)
			if num_reactant == 1:
				k_reac[i][0] = 1e30
				k_reac[i][1] = 1e30
			else:
				k_reac[i][0] = self.kmat_reactant[i][0][0] * self.T / self.viscosity
				k_reac[i][1] = self.kmat_reactant[i][0][1] * self.T / self.viscosity

		for i in range(len(self.reactions)):
			self.kdiff[i] = [0, 0]
			num_reactant = len(self.reactions[i].reactants_list)
			num_products = len(self.reactions[i].products_list)
			if num_reactant == 1 and num_products == 1:
				self.kdiff[i][0] = 1e30
				self.kdiff[i][1] = 1e30
			elif num_reactant == 1 and num_products > 1:
				self.kdiff[i][0] = k_prod[i][0]
				self.kdiff[i][1] = k_prod[i][1]
			elif num_reactant > 1 and num_products == 1:
				self.kdiff[i][0] = k_reac[i][0]
				self.kdiff[i][1] = k_reac[i][1]
			else:
				self.kdiff[i][0] = k_reac[i][0] * k_prod[i][0] / (k_prod[i][0] + k_reac[i][1])
				self.kdiff[i][1] = k_reac[i][1] * k_prod[i][1] / (k_prod[i][0] + k_reac[i][1])

		return self.kdiff

	def get_net_forward_rate_constants(self):
		limit_high = 1e18
		limit_low = 1e-18

		kd = self.get_kdiff()
		frk = self.get_forward_rate_constants()

		self.net_forward_rate_constants = []

		for i in range(len(self.reactions)):
			kf_net = 1.0 / ((1.0 / kd[i][0]) + (1.0 / frk[i]))
			if kf_net > limit_high:
				self.net_forward_rate_constants.append(limit_high)
			elif kf_net < limit_low:
				self.net_forward_rate_constants.append(limit_low)
			else:
				self.net_forward_rate_constants.append(kf_net)

		return self.net_forward_rate_constants

	def get_net_backward_rate_constants(self):
		limit_high = 1e18
		limit_low = 1e-18

		brk = self.get_backward_rate_constants()
		kd = self.get_kdiff()

		self.net_backward_rate_constants = []

		for i in range(len(self.reactions)):
			kb_net = 1.0 / ((1.0 / kd[i][1]) + (1.0 / brk[i]))
			if kb_net > limit_high:
				self.net_backward_rate_constants.append(limit_high)
			elif kb_net < limit_low:
				self.net_backward_rate_constants.append(limit_low)
			else:
				self.net_backward_rate_constants.append(kb_net)

		return self.net_backward_rate_constants

	def get_net_rates_of_progress(self):
		self.net_rates_of_progress = []

		nfrk = self.get_net_forward_rate_constants()
		nbrk = self.get_net_backward_rate_constants()

		for i in range(len(self.reactions)):
			prodr = 1.0
			prodp = 1.0
			for j in range(len(self.species)):
				prodr = prodr * math.pow(self.concentrations[j], self.reactants_stoic_coeffs[i][j])
				prodp = prodp * math.pow(self.concentrations[j], self.products_stoic_coeffs[i][j])
			self.net_rates_of_progress.append(nfrk[i] * prodr - nbrk[i] * prodp)

		return self.net_rates_of_progress

	def get_net_rates_of_production(self):
		# self.net_rates_of_production = []
		#
		# vpr = [[] for _ in range(len(self.reactions))]
		# for i in range(len(self.reactions)):
		# 	vpr[i] = [[] for _ in range(len(self.species))]
		# 	for j in range(len(self.species)):
		# 		vpr[i][j] = self.products_stoic_coeffs[i][j] - self.reactants_stoic_coeffs[i][j]
		#
		# q = self.get_net_rates_of_progress()
		#
		# for j in range(len(self.species)):
		# 	sum = 0.0
		# 	for i in range(len(self.reactions)):
		# 		sum += vpr[i][j]*q[i]
		# 	self.net_rates_of_production.append(sum)
		#
		# return self.net_rates_of_production
		self.net_rates_of_production = []
		self.net_rates_of_production.clear()
		vpr = [[0 for _ in range(len(self.species))] for _ in range(len(self.reactions))]
		for i in range(len(self.reactions)):
			for j in range(len(self.species)):
				vpr[i][j] = (self.products_stoic_coeffs[i][j] - self.reactants_stoic_coeffs[i][j])

		q = self.get_net_rates_of_progress()

		for j in range(len(self.species)):
			sum = 0.0
			for i in range(len(self.reactions)):
				sum += vpr[i][j] * q[i]
			self.net_rates_of_production.append(sum)

		return self.net_rates_of_production

	def get_Cps(self):
		self.Cps = [species.Cp(self.T) for species in self.species]
		return self.Cps

	def get_enthalpies(self):
		enthalpies = [species.Hf(self.T) for species in self.species]
		return enthalpies

	def get_Cpbar(self):
		return sum(Cp * y for Cp, y in zip(self.get_Cps(), self.Y))


if __name__ == '__main__':
	file1 = 'chem-liquid-phase-mechanism.txt'
	file2 = 'log-file-data-minima.txt'
	phase = Phase(file1, file2)
	phase.set_T = 610.0
	phase.setX(np.asarray([1.0 if phase.species_name(i) == 'HMX' else 0.5 for i in range(phase.get_n_species())]))

	# print(phase.Eaf)

	# for Eab in phase.Eab:
	# 	print(Eab)

	# forward_rate_constants = phase.get_forward_rate_constants()
	# for i in range(len(forward_rate_constants)):
	# 	print("{:8E}".format(forward_rate_constants[i]))

	# backward_rate_constants = phase.get_backward_rate_constants()
	# for i in range(len(backward_rate_constants)):
	# 	print("{:8E}".format(backward_rate_constants[i]))

	# kdiffs = phase.get_kdiff()
	# for i in range(len(kdiffs)):
	# 	print("{:E} {:E}".format(kdiffs[i][0], kdiffs[i][1]))

	# net_forward_rate_constants = phase.get_net_forward_rate_constants()
	# for i in range(len(net_forward_rate_constants)):
	# 	print("{:8E}".format(net_forward_rate_constants[i]))

	# net_backward_rate_constants = phase.get_net_backward_rate_constants()
	# for i in range(len(net_backward_rate_constants)):
	# 	print("{:8E}".format(net_backward_rate_constants[i]))

	# net_rates_of_progress = phase.get_net_rates_of_progress()
	# for net_rate_of_progress in net_rates_of_progress:
	# 	print("{:8E}".format(net_rate_of_progress))

	net_rates_of_production = phase.get_net_rates_of_production()
	for i in range(len(net_rates_of_production)):
		print("{:8E}".format(net_rates_of_production[i]))

	# Cps_test = phase.get_Cps()
	# print(Cps_test)

	# Enthalpies_test = phase.get_enthalpies()
	# print(Enthalpies_test)

	# Cpbar_test = phase.get_Cpbar()
	# print(Cpbar_test)
class Species:
	def __init__(self, line1, line2, line3, line4):
		# print(line3)
		vline1 = [item for item in line1.split() if item]

		self.radius = 0.0

		self.name = vline1[0]
		self.nC = int(vline1[2][:-1])
		self.nH = int(vline1[3][:-1])
		self.nN = int(vline1[4][:-1])
		self.nO = int(vline1[5][:-2])
		self.nCL = int(vline1[6][:-1])

		self.composition = {"C": self.nC, "H": self.nH, "N": self.nN, "O": self.nO, "CL": self.nCL}
		self.molecular_weight = 12.0107*self.nC + 1.0079*self.nH + 14.0067*self.nN + 15.9994*self.nO + 35.453*self.nCL

		self.T_low = float(vline1[7])
		self.T_high = float(vline1[8])
		self.T_mid = float(vline1[9])

		self.coeffs_low = [0] * 7

		self.coeffs_high = [float(line2[i:i+15]) for i in range(0, 75, 15)]
		self.coeffs_high.extend([float(line3[i:i+15]) for i in range(0, 30, 15)])

		self.coeffs_low[0] = float(line3[30:45])
		self.coeffs_low[1] = float(line3[45:60])
		self.coeffs_low[2] = float(line3[60:75])
		self.coeffs_low[3] = float(line4[0:15])
		self.coeffs_low[4] = float(line4[15:30])
		self.coeffs_low[5] = float(line4[30:45])
		self.coeffs_low[6] = float(line4[45:60])

		# self.coeffs_low = [float(line3[i:i+15]) for i in range(30, 75, 15)]
		# self.coeffs_low.extend([float(line4[i:i+15]) for i in range(0, 60, 15)])

	def Cp(self, T):
		R = 1.9872
		if T < self.T_mid:
			# return R*sum([self.coeffs_low[i]*T**i for i in range(5)])
			return R * (
					self.coeffs_low[0]
					+ self.coeffs_low[1] * T
					+ self.coeffs_low[2] * T ** 2
					+ self.coeffs_low[3] * T ** 3
					+ self.coeffs_low[4] * T ** 4 )
		else:
			return R*sum(self.coeffs_high[i]*T**i for i in range(5))

	def Hf(self, T):
		R = 1.9872
		if T < self.T_mid:
			return R*T*(sum([self.coeffs_low[i]*T**i/(i+1) for i in range(5)]) + self.coeffs_low[5]/T)
		else:
			return R*(sum(self.coeffs_high[i]*T**(i+1)/(i+1) for i in range(5)) + self.coeffs_high[5]/T)

if __name__ == '__main__':
	species_1 = Species("NG                      C  3H  5N  3O  9CL 0G     298.15   5000.00 1500.00     1",
						" 3.18697629E+01 2.48196202E-02-9.68915252E-06 1.73038005E-09-1.16330260E-13    2",
						"-4.82263177E+04-1.30010551E+02 1.74934097E+00 1.04264158E-01-8.82571027E-05    3",
						" 3.62598746E-08-5.80631361E-12-3.90915750E+04 2.78445740E+01                   4")

	print(species_1.name)
	print(species_1.composition)
	print(species_1.molecular_weight)
	print(species_1.coeffs_high)
	print(species_1.coeffs_low)
	print(species_1.Cp(900))
	print(species_1.Hf(900))

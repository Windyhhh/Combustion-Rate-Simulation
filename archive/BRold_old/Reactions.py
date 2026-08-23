class Reactions:
	def __init__(self, line):
		x = line.split()

		self.name = x[0]
		self.for_sym = float(x[1])
		self.for_conv = float(x[2])
		self.back_sym = float(x[3])
		self.back_conv = float(x[4])
		self.img_freq = float(x[5])
		self.dHf = max(0.0, float(x[8]))
		self.dHb = max(0.0, float(x[9]))
		self.dGf = max(0.0, float(x[10]))
		self.dGb = max(0.0, float(x[11]))
		self.ff = max(0.0, float(x[14]))
		self.fb = max(0.0, float(x[15]))

		reactants_products = x[0].split('=')
		self.reactants_list = [item.strip() for item in reactants_products[0].split('+')]
		self.products_list = [item.strip() for item in reactants_products[1].split('+')]

		if len(self.reactants_list) > 2:
			print(f"Warning: More than 2 reactants in the following reaction: {self.name}")
		if len(self.products_list) > 3:
			print(f"Warning: More than 3 products in the following reaction: {self.name}")

if __name__ == '__main__':

	liquid_reaction = Reactions("NG(L)=NG                                       2.00E+00  1.00E+00  2.00E+00  1.00E+03  4.51E+02  -4.0900E-01 -4.1325E+01  3.0215E+03  2.3640E+04  3.1375E+03  3.5956E+04 -2.0619E+04 -3.2819E+04     0.0   0.0")

	print("Name:", liquid_reaction.name)
	print("For_sym:", liquid_reaction.for_sym)
	print("For_conv:", liquid_reaction.for_conv)
	print("Back_sym:", liquid_reaction.back_sym)
	print("Back_conv:", liquid_reaction.back_conv)
	print("Img_freq:", liquid_reaction.img_freq)
	print("dHf:", liquid_reaction.dHf)
	print("dHb:", liquid_reaction.dHb)
	print("dGf:", liquid_reaction.dGf)
	print("dGb:", liquid_reaction.dGb)
	print("ff:", liquid_reaction.ff)
	print("fb:", liquid_reaction.fb)
	print("Reactants list:", liquid_reaction.reactants_list)
	print("Products list:", liquid_reaction.products_list)
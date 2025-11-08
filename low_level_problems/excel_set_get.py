#excel_set_get.py

# Implement setter and getter where the values of excel can be anything
# set(“A”, 1, “5”)
# get(“A”, 1)
# Now the setter can also take formulas like “=5+3”. They can be of four types below, but should evaluate to the correct value every time. Note the formula will only have a “+” symbol for simplicity. You can assume that the user will always provide valid inputs
# set(“A”, 1, “2”)
# set(“A”, 1, “=5+3”)
# set(“A”, 1, “=A2+3”)
# set(“A”, 1, “=A3+B5+4”)


class excel:
	def __init__(self,row,col):
		self.row=row
		self.col=col
		self.cache={}
		self.graph={}
		self.matrix=[["" for _ in range(col+1)] for _ in range(row+1)]

	def get_row_num(self,string):
		if len(string)==1:
			row=ord(string)-ord('A')+1
		else:
			j=0
			row=0
			for i in range(len(string)-1,-1,-1):
				row+=(26**j)*(ord(string[i])-ord('A')+1)
				j+=1
		return row

	def set(self,string,num,val):
		col=num
		row=self.get_row_num(string)
		self.matrix[row][col]=val


	def get(self,string,num):
		if (string,num) in self.cache:
			return self.cache[(string,num)]
		col=num
		row=self.get_row_num(string)
		val=str(self.matrix[row][col])

		my_sum=0
		if "=" in val:
			val=val[1:]
			val=val.split("+")
			for inp in val:
				if inp.isdigit():
					my_sum+=int(inp)
				else:
					my_string=""
					my_val=""
					for i in range(len(inp)):
						if inp[i].isdigit():
							my_val+=inp[i]
						else:
							my_string+=inp[i]
					my_sum+=int(self.get(my_string,int(my_val)))

			self.cache[(string,num)]=my_sum
		else:
			self.cache[(string,num)]=self.matrix[row][col]

		return self.cache[(string,num)]
	


ex=excel(1000,1000)

ex.set("A",1,"5")
ex.set("A",2,"=A1+5")
print(ex.get("A",2))
ex.set("A",1,"7")
print(ex.get("A",2))
ex.set("A", 3, "=A2+4")
ex.set("A", 4, "=A2+5")
ex.set("A", 5, "=A2+6")
ex.set("B", 1, "=A3+A4+A5")
print(ex.get("B", 1))

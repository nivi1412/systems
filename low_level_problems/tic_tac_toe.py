#tic_tac_toe.py

class TicTacToe:

	def __init__(self, n=3):
		self.size = n
		self.matrix=[["" for _ in range(self.size)] for _ in range(self.size)]

	def insert(self, i: int, j: int, val: str):
		self.matrix[i][j]+=val

	def game_over(self):
		c1,c2,c3,c4=True,True,True,True
		result=False

		for i in range(self.size):
			local=self.matrix[i][0]
			for j in range(self.size-1):
				if local != "" and local == self.matrix[i][j+1]:
					c1=c1 and True
				else: c1=False
			result= result or c1
			c1=True
			if result: return result

		for j in range(self.size):
			local=self.matrix[0][j]
			for i in range(self.size-1):
				if local!="" and local==self.matrix[i+1][j]:
					c2=c2 and True
				else:
					c2=False
			result=result or c2
			c2=True
			if result: return result

		local=self.matrix[0][0]

		for i in range(1,self.size):
			if local!="" and local==self.matrix[i][i]:
				c3=c3 and True
			else:
				c3=False
		result=result or c3
		if result: return result

		local=self.matrix[0][self.size-1]

		for i in range(1,self.size):
			if local!="" and local==self.matrix[i][self.size-1-i]:
				c4=c4 and True
			else:
				c4=False
		result=result or c4
		if result: return result

		return result

	def print(self):
		for i in range(self.size):
			print(self.matrix[i])


class Player:

	def __init__(self, player_name: str, player_id: int):
		self.player_name=player_name
		self.player_id=player_id
		self.symbol='X' if player_id == 1 else 'O'

	def play(self, i: int, j: int, t: TicTacToe):
		t.insert(i, j, self.symbol)
		t.print()


ttt=TicTacToe()
rahul=Player('rahul',1)
chinnulu=Player('chinnulu',2)
count=0

while(1):
	i,j=map(int,input("enter the location i,j of matrix: ").split(","))
	if ttt.matrix[i][j]=="":
		if count%2==0:
			rahul.play(i,j,ttt)
		else:
			chinnulu.play(i,j,ttt)
		count+=1
	else:
		print("row,col is already entered ")
	if ttt.game_over():
		if count%2!=0:
			print("rahul won")
		else:
			print("chinnulu won")
		break
	if count==9:
		print('draw')
		break
		
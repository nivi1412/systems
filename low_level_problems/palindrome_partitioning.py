#palindrome_partitioning.py

s=input("enter the string: ")
dp=[]

for i in range(s):
	if i==0:
		dp.append([s[i]])
	else:
		

#destination_reached.py
import ast

def is_destination_reached(grid,i,j,dst,visited):
	if i>=len(grid) or j>=len(grid[0]) or i<0 or j<0:
		return False
	if (i,j)==dst:
		return True

	visited[i][j]=True
	if grid[i][j]=="up":
		return is_destination_reached(grid,i-1,j,dst,visited)
	elif grid[i][j]=="down":
		return is_destination_reached(grid,i+1,j,dst,visited)
	elif grid[i][j]=="right":
		return is_destination_reached(grid,i,j+1,dst,visited)
	else:
		return is_destination_reached(grid,i,j-1,dst,visited)

	return False

grid=input("enter the grid matrix with directions: ")
grid=ast.literal_eval(grid)
src=input("enter the source row col tuple:")
src=ast.literal_eval(src)
dst=input("enter the destination node row,col tuple: ")
dst=ast.literal_eval(dst)

i=src[0]
j=src[1]
visited=[[False for _ in range(len(grid[0]))] for _ in range(len(grid))]
print(is_destination_reached(grid,i,j,dst,visited))
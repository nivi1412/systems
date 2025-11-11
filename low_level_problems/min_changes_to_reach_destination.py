#min_changes_to_reach_destination.py
from collections import deque
import ast

grid=input("enter the grid matrix with directions: ")
grid=ast.literal_eval(grid)
src=input("enter the source row col tuple:")
src=ast.literal_eval(src)
dst=input("enter the destination node row,col tuple: ")
dst=ast.literal_eval(dst)

i=src[0]
j=src[1]
visited=[[False for _ in range(len(grid[0]))] for _ in range(len(grid))]
q=deque()

q.append((i,j,0))

def in_range(i, j):
	return 0 <= i and i < len(grid) and 0 <= j and j < len(grid)

def weight_for_direction(i_dir, j_dir, val):
	if val == "U":
		return 0 if i_dir == -1 and j_dir == 0 else 1
	if val == "D":
		return 0 if i_dir == 1 and j_dir == 0 else 1
	if val == "L":
		return 0 if i_dir == 0 and j_dir == 1 else 1
	if val == "R":
		return 0 if i_dir == 0 and j_dir == 1 else 1

while q:
	i,j,weight=q.popleft()
	visited[i][j]=True

	print("i,j:",i,j)
	if (i,j)==dst:
		print(weight)
		break
	for k in [-1, 1]:
		if in_range(i + k, j) and visited[i+k][j]==False:
			w = weight_for_direction(k, 0, grid[i][j])
			if w == 0 :
				q.appendleft((i + k, j, weight + w))
				
			else:
				q.append((i + k, j, weight + w))
			visited[i+k][j]=True

	for k in [-1, 1]:
		if in_range(i, j + k) and visited[i][j+k]==False:
			w = weight_for_direction(0, k, grid[i][j])
			if w == 0:
				q.appendleft((i, j + k, weight + w))
			else:
				q.append((i, j + k, weight + w))
			visited[i][j+k]=True








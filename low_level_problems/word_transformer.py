#word_transformer.py
import ast
from collections import deque

class WordTransformer:
	def __init__(self,word_list:list[str]):
		self.word_list=word_list

	def shortest_transformation(self, begin: str, end: str) -> int:
		s1=begin
		q=deque()
		q.append((begin,0))
		length=0
		while q:
			s1,depth=q.popleft()
			if s1==end:
				length=depth+1
				break
			for i in range(len(self.word_list)):
				s2=self.word_list[i]
				count=sum(a!=b for a,b in zip(s1,s2))
				if count==1:
					q.append((s2,depth+1))
		return length


wordlist= input("enter the words list:")
wordlist=ast.literal_eval(wordlist)
begin=input("enter the start string:")
end=input("enter the end string")

transformer=WordTransformer(wordlist)
print(transformer.shortest_transformation(begin,end))
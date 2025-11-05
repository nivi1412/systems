#parking_lot_stats.py

class ParkingStat:

	def __init__(self,n):
		self.total_spots=n
		self.filled_spots=0
		self.my_dict={}
		for i in range(self.total_spots):
			self.my_dict[i]=None

	def print(self):
		print("total lots:", self.total_spots)
		print("filled spots:",self.filled_spots)
		print("free spots:", self.total_spots-self.filled_spots)

	def bill(self,park_slot,exit_time):

		time_diff=exit_time-self.my_dict[park_slot][1]
		self.filled_spots-=1
		self.my_dict[park_slot]=None
		print("total_bill:",time_diff*30)


class Entry_Exit:

	def __init__(self,parking_stat,):
		self.parking_stat=parking_stat

	def entry(self,car_id,entry_time):
		print("........ entry .......",car_id)

		if self.parking_stat.total_spots-self.parking_stat.filled_spots==0:
			print("no empty spots, please visit again")
		else:
			for key in self.parking_stat.my_dict:
				if self.parking_stat.my_dict[key] is None:
					self.parking_stat.my_dict[key]=(car_id,entry_time)
					break

			if self.parking_stat.filled_spots < self.parking_stat.total_spots:
				self.parking_stat.filled_spots+=1
			
		self.parking_stat.print()

	def exit(self,car_id,exit_time):
		car_found=False
		print("........ exit .......",car_id)

		for park_slot,values in self.parking_stat.my_dict.items():
			if values[0]==car_id:
				self.parking_stat.bill(park_slot,exit_time)
				car_found=True
				break
		
		if not car_found:
			print("car_id doesnt exist,please enter again")

		self.parking_stat.print()

p=ParkingStat(3)
ee=Entry_Exit(p)

ee.entry(1,1)
ee.entry(2,1)
ee.entry(3,1)
ee.entry(4,1)
ee.exit(2,3)
ee.entry(4,3)
ee.entry(6,3)
ee.exit(1,5)






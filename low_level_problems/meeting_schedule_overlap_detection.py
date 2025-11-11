#meeting_schedule_overlap_detection.py

class MeetingScheduler:

	def __init__(self):
		self.calender={}

	def add_meeting(self,start,end,title):

		if title not in self.calender:
			self.calender[title]=(start,end)
			print(self.calender)
			return True

		else:
			return False

	def remove_meeting(self,title):

		if title in self.calender:
			self.calender.pop(title)
			print(self.calender)

		else:print("title does not exist")

	def get_next_meeting(self,current_time):

		next_meet_found=False
		for title,time in self.calender.items():
			if time[0]>current_time:
				next_meet_found=True
				return (title,time[0],time[1])
		return next_meet_found

meet=MeetingScheduler()
print(meet.add_meeting(9,10,"introduction"))
print(meet.add_meeting(10,11,"topic1"))
print(meet.add_meeting(11,12,"break"))
print(meet.add_meeting(12,13,"lunch"))
print(meet.add_meeting(13,14,"topic3"))

meet.remove_meeting("break")
print("next meeting:",meet.get_next_meeting(12))
print("next_meeting:",meet.get_next_meeting(15))

				












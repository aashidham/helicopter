TASK = 1
SPLIT_TASK = 2
EVENT = 3

from feed.date.rfc3339 import *

def startDate(thing):
	return thing.start

def endDate(thing):
	return thing.end

class Thing(object):	
	def __init__(self, taskOrEvent, isSplitTask=None):
		self.name = taskOrEvent["summary"]
		if "end" in taskOrEvent:
			self.end = taskOrEvent["end"]
			self.start = taskOrEvent["start"]
			if isSplitTask:
				self.type = SPLIT_TASK
			else:
				self.type = EVENT
		else:
			self.end = taskOrEvent["deadline"]
			self.start = taskOrEvent["deadline"] - taskOrEvent["duration"] * 1000
			self.type = TASK
	
	

	def conflictsWith(self,other):
		if(self.end > other.start and self.start < other.end):
			return True
		else:
			return False
		
	def isEvent(self):
		return self.type == EVENT
	def isSplitTask(self):
		return self.type == SPLIT_TASK
	def isTask(self):
		return self.type == TASK or self.type == SPLIT_TASK
			
	def __repr__(self):
		return self.name + " | start:" + timestamp_from_tf(self.start/1000) + " | end:" + timestamp_from_tf(self.end/1000) + " | type:" +str(self.type)

def movePrevUp(curr,prev):
	prevDuration = prev.end - prev.start
	prev.end = curr.start
	prev.start = prev.end - prevDuration
	
def moveCurrUp(curr,prev):
	currDuration = curr.end - curr.start
	curr.end = prev.start
	curr.start = curr.end - currDuration	

def combine(events,tasks):
	currCounter = len(tasks)-1
	while(currCounter >= 0):
		while True:
			curr = tasks[currCounter]
			intersect_events = []
			for event in events:
				if event.conflictsWith(curr):
					intersect_events.append(event)
			if len(intersect_events) == 0:
				break
			else:
				intersect_events.sort(key=endDate,reverse=True)
				event = intersect_events[0]
				if event.start < curr.end and curr.end < event.end:
					moveCurrUp(curr,event)
				else:
					firstBlockDuration = event.end - curr.start
					curr.start = event.end
					curr.type = 2
					split = Thing({"summary":curr.name,"start":event.start-firstBlockDuration,"end":event.start},True)
					print "created split task"
					tasks.insert(currCounter,split)
		if currCounter != 0:
			tempCurr = currCounter
			while(tempCurr > 0):
				tempPrev = tempCurr - 1
				while(tempPrev >= 0):
					prev = tasks[tempPrev]
					curr = tasks[tempCurr]
					if prev.conflictsWith(curr):
						movePrevUp(curr,prev)
					tempPrev = tempPrev-1
				tempCurr = tempCurr-1		
		currCounter = currCounter-1
	
	#do final merging
	eventsAndTasks = events
	for t in tasks:
		eventsAndTasks.append(t)
	eventsAndTasks.sort(key=startDate)
	return eventsAndTasks
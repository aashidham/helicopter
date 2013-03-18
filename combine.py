TASK = 1
SPLIT_TASK = 2
EVENT = 3


def startDate(thing):
	return thing.start

class Thing(object):	
	def __init__(self, taskOrEvent, isTask=None):
		self.name = taskOrEvent["summary"]
		if "end" in taskOrEvent:
			self.end = taskOrEvent["end"]
			self.start = taskOrEvent["start"]
			if isTask:
				self.type = TASK
			else:
				self.type = EVENT
		else:
			self.end = taskOrEvent["deadline"]
			self.start = taskOrEvent["deadline"] - taskOrEvent["duration"] * 1000
			self.type = TASK
	
	

	def conflictsWith(self,other):
		if(self.end > other.start):
			return True
		else:
			return False
		
	def isEvent(self):
		return self.type == EVENT
	def isSplitTask(self):
		return self.type == SPLIT_TASK
	def isTask(self):
		return self.type == TASK
			
	def __repr__(self):
		return self.name + " | start:" + str(self.start) + " | end:" + str(self.end) + " | type:" +str(self.type)

def combine(events,tasks):
	eventsAndTasks = []
	# merge events and tasks
	taskCounter = 0;
	eventCounter = 0;
	while(taskCounter < len(tasks) and eventCounter < len(events)):
		currTask = tasks[taskCounter]
		currEvent = events[eventCounter]
		if currTask.start < currEvent.start:
			eventsAndTasks.append(currTask)
			taskCounter = taskCounter+1
		else:
			eventsAndTasks.append(currEvent)
			eventCounter = eventCounter+1
	while(taskCounter < len(tasks)):
		currTask = tasks[taskCounter]
		eventsAndTasks.append(currTask)
		taskCounter = taskCounter+1
	while(eventCounter < len(events)):
		currEvent = events[eventCounter]
		eventsAndTasks.append(currEvent)
		eventCounter = eventCounter+1
	#adjust tasks
	currCounter = len(eventsAndTasks)-1
	while(currCounter > 0):
		prevCounter = currCounter-1
		while(prevCounter >= 0):
			curr = eventsAndTasks[currCounter]
			prev = eventsAndTasks[prevCounter]
			if prev.conflictsWith(curr):
				if prev.isEvent() and curr.isEvent():
					prevCounter = prevCounter-1
				elif prev.isEvent():
					if curr.end > prev.end:
						firstBlockDuration = prev.end - curr.start
						curr.start = prev.end
						curr.type = 2
						split = Thing({"summary":curr.name,"start":prev.start-firstBlockDuration,"end":prev.start},True)
						eventsAndTasks.append(split)
					else:
						currDuration = curr.end - curr.start
						curr.end = prev.start
						curr.start = curr.end - currDuration					
				elif prev.isSplitTask() and curr.isTask():
					currDuration = curr.end - curr.start
					curr.end = prev.start
					curr.start = curr.end - currDuration
				#elif prev.isTask() and curr.isEvent() and prev.end > curr.end:				
				else:
					prevDuration = prev.end - prev.start
					prev.end = curr.start
					prev.start = prev.end - prevDuration
				eventsAndTasks.sort(key=startDate)
			else:
				prevCounter = prevCounter-1
		currCounter = currCounter-1				
		
	return eventsAndTasks
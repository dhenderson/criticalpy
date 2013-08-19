import csv

def load_tasks_from_csv(path_to_csv):
	"""Loads tasks from a csv file and returns a map of tasks
	The CSV file must have the first row be a header row, wich the columsn in the following order:
	* task_id
	* name
	* duration
	* predecessor ids (with each predecessor ID separated by a comma)
	Args:
		path_to_csv: [string] path to the csv file
	Returns:
		Returns a dictionary in the from form {task_id, task}
	"""
	csv_file = open(path_to_csv, 'r')
	csv_file_reader = csv.reader(csv_file, delimiter=',')
	
	# dictionary in form {task_id, task}
	tasks = {}
	
	first_row = True
	for row in csv_file_reader:
		if not first_row:
			task_id = int(row[0])
			name = row[1]
			duration = int(row[2])
			predecessor_ids = parse_predecessor_ids(row[3])
			task = Task(task_id, name, duration, predecessor_ids)
			tasks[task_id] = task
		else:
			first_row = False
	
	return tasks
	
def load_project_from_csv(path_to_csv):
	project = Project(load_tasks_from_csv(path_to_csv))
	return project
			
def parse_predecessor_ids(predecessor_ids_string):
	"""Parses a comma seperated list of task IDs
		Args: 
			predecessor_ids_string: [string] comma separated task IDs
		Returns:
			List of task IDs as integers
	"""
	predecessor_ids = []
	predecessor_ids_strings = predecessor_ids_string.split(',')
	for predecessor_id_string in predecessor_ids_strings:
		if predecessor_id_string != '':
			predecessor_ids.append(int(predecessor_id_string))
	return predecessor_ids
	
class Task():
	"""Represents a task in a project
		Attributes:
			id: [int] unique task ID
			name: [string] task name
			duration: [float] 
			predecessor_ids: [list] list of unique task IDs for the tasks that precedes this one
			early_start: [float]
			early_finish: [float]
			late_start: [float]
			late_finish: [float]
			slack: [float]
			is_critical: [boolean] indicates if this task is on the critical path
	"""
	def __init__(self, id, name, duration, predecessor_ids):
		self.id = id
		self.name = name
		self.duration = duration
		self.predecessor_ids = predecessor_ids
		self.early_start = None
		self.early_finish = None
		self.late_start = None
		self.late_finish = None
		self.slack = None
		self.predecessors = {} # {task_id : task}
		self.is_critical = False
		
	def set_predecessors(self, tasks):
		for predecessor_id in self.predecessor_ids:
			self.predecessors[predecessor_id] = tasks[predecessor_id]

	def calculate_early_start(self):
		if len(self.predecessors) == 0:
			self.early_start = 1
			self.calculate_early_finish()
		else:
			max_predecessor_early_finish = 0
			for predecessor_id in self.predecessors:
				predecessor = self.predecessors[predecessor_id]
				if predecessor.early_finish > max_predecessor_early_finish:
					max_predecessor_early_finish = predecessor.early_finish + 1
			self.early_start = max_predecessor_early_finish

	def calculate_early_finish(self):
		self.early_finish = self.early_start + self.duration - 1

	def calculate_late_finish(self):
		for predecessor_id in self.predecessors:
			predecessor = self.predecessors[predecessor_id]
			if predecessor.late_finish == None:
				predecessor.late_finish = self.late_start - 1
			if predecessor.late_finish >= self.late_start :
				predecessor.late_finish = self.late_start - 1

	def calculate_late_start(self):
		self.late_start = self.late_finish - self.duration + 1

	def calculate_slack(self):
		self.slack = self.late_start - self.early_start
		
	def calculate_is_critical(self):
		if self.slack == 0:
			self.is_critical = True
		else:
			self.is_critical = False

class Project():
	def __init__(self, tasks):
		self.tasks = tasks # ordered list of tasks
		self.set_task_predicessors()
		self.forward_pass()
		self.backward_pass()
		
	def set_task_predicessors(self):
		for task in self.order_tasks(self.tasks):
			task.set_predecessors(self.tasks)

	def forward_pass(self):
		for task in self.order_tasks(self.tasks):
			task.calculate_early_start()
			task.calculate_early_finish()

	def backward_pass(self):
		is_end_task = True

		for task in self.order_tasks(self.tasks, True):
			if is_end_task:
				task.late_finish = task.early_finish
				is_end_task = False
				
			task.calculate_late_start()
			task.calculate_late_finish()
			task.calculate_slack()
			task.calculate_is_critical()
			
			
	def order_tasks(self, tasks, is_reverse=False):
		""" Returns a list of tasks ordered by task_id
		"""
		ordered_tasks = []
		ordered_keys = sorted(tasks, reverse=is_reverse)
		
		for key in ordered_keys:
			ordered_tasks.append(tasks[key])
			
		return ordered_tasks
		
	def write_csv(self, path_to_csv):
		
		# clear out the csv file
		csv_file = open(path_to_csv, 'w', newline='')
		csv_file.close()
		
		# open the csv file in append mode
		csv_file = open(path_to_csv, 'a', newline='')
		csv_writer = csv.writer(csv_file)
		
		# write the headers
		csv_writer.writerow(["Task ID", 
			"Name", "Duration", "Early start", 
			"Early finish", "Late start", "Late finish", 
			"Slack", "Critical"])
		
		for task in self.order_tasks(self.tasks):
			row = [task.id, 
				task.name, 
				task.duration, 
				task.early_start,
				task.early_finish, 
				task.late_start, 
				task.late_finish,
				task.slack, 
				task.is_critical]
			
			csv_writer.writerow(row)

		csv_file.close()
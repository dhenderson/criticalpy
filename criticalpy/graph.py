from criticalpy import criticalpy

def project_to_graphviz(project, critical_path_color = "#FFFFFF"):

	dot = "digraph G {\n"
	dot = add_graphviz_line(dot, "node [shape=record]")
	tasks = project.order_tasks(project.tasks, False)
	
	# nodes
	for task in tasks:
		# label
		column_one = '{' + str(task.early_start) + '|' + str(task.late_start) + '}'
		column_two = '{' + str(task.duration) + '|' + line_breaks(task.name) + '|' + str(task.slack) + '}'
		column_three = '{' + str(task.early_finish) + '|' + str(task.late_finish) + '}'
		label = column_one + "|" + column_two + "|" + column_three
		
		# critcal path color
		critical_color="#FFFFFF"
		if task.is_critical:
			critical_color = critical_path_color
		
		node_args = '[label="' + label + '", color="#000000", style=filled, fillcolor="' + critical_color + '"]'
		dot = add_graphviz_line(dot, "node" + str(task.id) + ' ' + node_args)

	# edges
	for task in tasks:
		for predecessor_id in task.predecessor_ids:
			dot = add_graphviz_line(dot, "node" + str(predecessor_id) + " -> node" + str(task.id))
	dot = dot + "}"
	
	return dot
	
def add_graphviz_line(dot, content):
	dot = dot + "    " + content + "; \n"
	return dot
	
def line_breaks(text, break_every = 3):
	text_with_breaks = ""
	
	word_counter = 0
	for word in text.split(" "):
		if word_counter == break_every:
			text_with_breaks = text_with_breaks + r"\n"
			word_counter = 0
		text_with_breaks = text_with_breaks + word + " "
		word_counter = word_counter + 1
		
	return text_with_breaks

from criticalpy import criticalpy

def test_load_project_from_csv():
	project = criticalpy.load_project_from_csv('test.csv')
	project.write_csv('critical_path_ouptut.csv')
	
test_load_project_from_csv()
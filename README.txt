Canvas Student Info Export
Configure User Access Token (not “Developer Key”) from Canvas for script API access.
Install Python on workstation 
    1. Download canvas-syllabus-scripts from https://github.com/Josiah-Cloninger/Canvas-API-Student-Success-Query
    2. Modify “scrape_config.ini” and “query_config.ini” with the desired values.
Note: TERM should be in the format FA-25, SP-26, SU-26, etc.
    3. Install Python 3.14
    4. Create a virtual environment
	python3 -m venv .venv
    5. Activate the virtual environment
	.\.venv\Scripts\Activate.ps1
    6. Install requirements. Navigate to project folder.
	pip install -r requirements.txt
    7. Run scrape.py
       python3 scrape.py
    8. Run student_info_query.py
	python3 student_info_query.py
    9. The output of student_info_query will be in 	“troubled_students.csv” by default

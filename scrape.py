import csv
from canvasapi import Canvas
from configparser import ConfigParser, Error
    

config = ConfigParser()
try:
    config.read('canvas-student-information-script/scrape_config.ini')
    API_URL = config.get('DEFAULT', 'api_url')
    API_KEY = config.get('DEFAULT', 'api_key')
    TERM = config.get('DEFAULT', 'term')
    OUTPUT_FILE = config.get('DEFAULT', 'output_file')
except (Error, KeyError) as e:
    print(f"Error reading config file: {e}")
    quit()

CANVAS = Canvas(API_URL, API_KEY)
ACCOUNT = CANVAS.get_account('1')

TERM = "FA-26"
OUTPUT_FILE = "student_info.csv"
FIELDNAMES = ["student_id",
                "student_name",
                "course_id",
                "course_name",
                "current_score",
                "current_grade",
                "final_score",
                "final_grade",
                "last_activity_at",
                "last_attended_at",
                "days_since_last_attendance",
                "late_assignments"
                ]



def get_term_id(term_name):
    account = CANVAS.get_account('1')
    term_id = ""

    for term in account.get_enrollment_terms():
        if term.name == term_name:
            term_id = term.id

    if term_id == "":
        print(f"Error: Term ID for \"{term_name}\" not found. Make sure the term name is in the format SP-25, FA-26, etc.")
        quit()

    return term_id

def student_info_report():
    term_id = get_term_id(TERM)
    rows = []
    
    print(f"Generating student information report for term: {TERM} (ID: {term_id})")
    users = ACCOUNT.get_users(enrollment_type=["student"], include=["enrollments"])
    courses_raw = ACCOUNT.get_courses(enrollment_term_id=term_id)

    print(f"Building course dictionary...")
    courses_dict = {course.id: course for course in courses_raw}

    print(f"Building assignment dictionary...")
    assignments_dict = {course.id: course.get_assignments() for course in courses_raw}

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as output_csv:
        writer = csv.DictWriter(output_csv, fieldnames=FIELDNAMES)
        writer.writeheader()
        for student in users:
            print (f"Processing student: {student.name} (ID: {student.id})")
            enrollments = student.get_enrollments(enrollment_term_id=term_id)
            for enrollment in [x for x in enrollments if x.type == "StudentEnrollment"]:
                course = courses_dict.get(enrollment.course_id)
                
                late_assignments = -1

                # Fetch late assignments. Takes a very long time to run.
                """
                assignments = assignments_dict.get(course.id, [])
                late_assignments = 0
                for assignment in assignments:
                    submission = assignment.get_submission(student.id)
                    if submission.late:
                        late_assignments += 1
                """

                writer.writerows([{
                    "student_id": student.id,
                    "student_name": student.name,
                    "course_id": course.id,
                    "course_name": course.name,
                    "current_score": enrollment.grades.get("current_score", ""),
                    "current_grade": enrollment.grades.get("current_grade", ""),
                    "final_score": enrollment.grades.get("final_score", ""),
                    "final_grade": enrollment.grades.get("final_grade", ""),
                    "last_activity_at": enrollment.last_activity_at,
                    "last_attended_at": enrollment.last_attended_at,
                    "late_assignments": late_assignments
                }])


def main():
    student_info_report()
            
if __name__ == "__main__":
    main()
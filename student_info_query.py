import csv, datetime
from configparser import ConfigParser, Error


class Enrollment:
    def __init__(self, student_id, student_name, course_id, course_name, current_score, current_grade, final_score, final_grade, last_activity_at, last_attended_at, days_since_last_attendance, late_assignments=-1):
        self.student_id = student_id
        self.student_name = student_name
        self.course_id = course_id
        self.course_name = course_name
        self.current_score = current_score
        self.current_grade = current_grade
        self.final_score = final_score
        self.final_grade = final_grade
        self.last_activity_at = last_activity_at
        self.last_attended_at = last_attended_at
        self.days_since_last_attendance = days_since_last_attendance
        self.late_assignments = late_assignments

    def __str__(self):
        return f"Student Name: {self.student_name}, Course Name: {self.course_name}, Final Grade: {self.final_grade}"
    
    def __repr__(self):
        return f"Enrollment(student_name={self.student_name}, course_name={self.course_name}, current_score={self.current_score}, current_grade={self.current_grade}, final_score={self.final_score}, final_grade={self.final_grade}, last_activity_at={self.last_activity_at}, last_attended_at={self.last_attended_at}, days_since_last_attendance={self.days_since_last_attendance}, late_assignments={self.late_assignments})"
    
class Student:
    def __init__(self, student_id, student_name, failed_enrollments=None, inactive_enrollments=None, failed_count=0, inactive_count=0):
        self.student_id = student_id
        self.student_name = student_name
        self.failed_enrollments = failed_enrollments if failed_enrollments is not None else []
        self.failed_count = failed_count
        self.inactive_enrollments = inactive_enrollments if inactive_enrollments is not None else []
        self.inactive_count = inactive_count

    def add_failed_enrollment(self, enrollment):
        self.failed_enrollments.append(enrollment)

    def add_inactive_enrollment(self, enrollment):
        self.inactive_enrollments.append(enrollment)

    def __str__(self):
        return f"Student Name: {self.student_name}, Failed Enrollments: {len(self.failed_enrollments)}, Inactive Enrollments: {len(self.inactive_enrollments)}"
    
    def __repr__(self):
        return f"Student(student_name={self.student_name}, failed_enrollments={len(self.failed_enrollments)}, inactive_enrollments={len(self.inactive_enrollments)})"


def read_csv(file_path):
    enrollments = []
    with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            enrollment = Enrollment(
                student_id=row["student_id"],
                student_name=row["student_name"],
                course_id=row["course_id"],
                course_name=row["course_name"],
                current_score=row["current_score"],
                current_grade=row["current_grade"],
                final_score=row["final_score"],
                final_grade=row["final_grade"],
                last_activity_at=row["last_activity_at"],
                last_attended_at=row["last_attended_at"],
                days_since_last_attendance=row["days_since_last_attendance"],
                late_assignments=row.get("late_assignments", -1)
            )
            enrollments.append(enrollment)
    return enrollments

def get_failed_enrollments(enrollments, threshold=["F", "D"]):
    troubled_students = []

    for enrollment in enrollments:
        if enrollment.current_grade in threshold and enrollment.course_name not in ["Work Program"]:
            troubled_students.append(enrollment)

    return troubled_students

def get_inactive_enrollments(enrollments, threshold=7):
    inactive_students = []
    threshold_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=threshold)

    for enrollment in enrollments:
        last_activity = enrollment.last_activity_at
        if not last_activity:
            continue

        last_activity_date = datetime.datetime.fromisoformat(last_activity.replace("Z", "+00:00"))

        if last_activity_date < threshold_date:
            inactive_students.append(enrollment)                    

    return inactive_students


def main():
    config = ConfigParser()
    try:
        config.read('canvas-student-information-script/query_config.ini')
        FAILED_COURSE_THRESHOLD = config.get('DEFAULT', 'failed_course_threshold')
        INACTIVE_DAYS_THRESHOLD = config.get('DEFAULT', 'inactive_days_threshold')
        ENROLLMENTS_FILE = config.get('DEFAULT', 'enrollments')
        OUTPUT_FILE = config.get('DEFAULT', 'output')
    except (Error, KeyError) as e:
        print(f"Error reading config file: {e}")
        quit()

    students = []
    enrollments = read_csv(ENROLLMENTS_FILE)
    failed_enrollments = get_failed_enrollments(enrollments, threshold=FAILED_COURSE_THRESHOLD.strip("[]").replace(" ", "").split(","))
    inactive_enrollments = get_inactive_enrollments(enrollments, threshold=int(INACTIVE_DAYS_THRESHOLD))

    for enrollment in failed_enrollments:
        if enrollment.student_id not in [student.student_id for student in students]:
            student = Student(student_id=enrollment.student_id, student_name=enrollment.student_name)
            students.append(student)
        for student in students:
            if student.student_id == enrollment.student_id:
                student.failed_enrollments.append(enrollment)
                student.failed_count += 1

    for enrollment in inactive_enrollments:
        if enrollment.student_id not in [student.student_id for student in students]:
            student = Student(student_id=enrollment.student_id, student_name=enrollment.student_name)
            students.append(student)
        for student in students:
            if student.student_id == enrollment.student_id:
                student.inactive_enrollments.append(enrollment)
                student.inactive_count += 1
    
    with open(OUTPUT_FILE, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "student_id",
            "student_name",
            "failed_count",
            "inactive_count" ,
             "failed_enrollments",
             "inactive_enrollments"
        ])
        for student in students:
            writer.writerow([
                student.student_id,
                student.student_name,
                student.failed_count,
                student.inactive_count,
                "; ".join([f"{enrollment.course_name} (Grade: {enrollment.final_grade})" for enrollment in student.failed_enrollments]),
                "; ".join([f"{enrollment.course_name} (Last Activity: {enrollment.last_activity_at})" for enrollment in student.inactive_enrollments])
            ])


if __name__ == "__main__":    main()

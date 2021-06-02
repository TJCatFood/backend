from course.models import Course, Teach
from course.serializers import CourseSerializers, TeachSerializers
from user.models import TakeCourse
from user.serializers import TakeCourseSerializer


def generate_response(data, isSuccess):
    return {
        "isSuccess": isSuccess,
        "data": data
    }


def is_teacher_teach_course(teacher_id, course_id) -> bool:
    teaches = Teach.objects.filter(teacher_id=teacher_id)
    teaches_serializer = TeachSerializers(teaches, many=True)
    course_id_list = []
    for teach in teaches_serializer.data:
        course_id_list.append(teach['course_id'])
    if course_id not in course_id_list:
        return False
    return True


def is_student_within_course(student_id, course_id) -> bool:
    takes = TakeCourse.objects.filter(student_id=student_id)
    takes_serializer = TakeCourseSerializer(takes, many=True)
    course_id_list = []
    for take in takes_serializer.data:
        course_id_list.append(take['course_id'])
    if course_id not in course_id_list:
        return False
    return True

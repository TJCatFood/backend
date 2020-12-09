from rest_framework.response import Response
from rest_framework.views import APIView

# Templates starts here


class AliveView(APIView):

    def get(self, request, format=None):
        response = 'alive'
        content = {
            "response": f"{response}"
        }
        return Response(content)


class CourseIdTemplate(APIView):

    def get(self, request, course_id, format=None):
        content = {
            "course_id": course_id,
        }
        return Response(content)


class CourseIdFileIdTemplate(APIView):

    def get(self, request, course_id, file_id, format=None):
        content = {
            "course_id": course_id,
            "file_id": file_id
        }
        return Response(content)


class ExperimentIdTemplate(APIView):

    def get(self, request, experiment_id, format=None):
        content = {
            "experiment_id": experiment_id,
        }
        return Response(content)


class ExperimentIdFileIdTemplate(APIView):

    def get(self, request, experiment_id, file_id, format=None):
        content = {
            "experiment_id": experiment_id,
            "file_id": file_id
        }
        return Response(content)


class QuestionTypeQuestionId(APIView):

    def get(self, request, question_type, question_id, format=None):
        content = {
            "question_type": question_type,
            "question_id": question_id
        }
        return Response(content)

# Templates ends here

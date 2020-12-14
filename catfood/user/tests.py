from django.test import TestCase
from rest_framework.test import APIClient
from .models import University, School
from course.models import Course
from django.utils import timezone as datetime
import json


class UserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.myUniversity = University.objects.create(university_name="Tongji",
                                                     official_id="201804")
        cls.university_id = cls.myUniversity.university_id
        cls.mySchool = School.objects.create(school_name="SSE",
                                             university_id=cls.myUniversity)
        cls.school_id = cls.mySchool.school_id
        cls.myCourseA = Course.objects.create(course_creator_school_id="魔法学院", course_name="卖弱心理学",
                                              course_start_time=datetime.now(), course_end_time=datetime.now(),
                                              course_description="", course_type="必修", course_avatar="")
        cls.course_id_a = cls.myCourseA.course_id
        cls.myCourseB = Course.objects.create(course_creator_school_id="魔法学院", course_name="恋爱心理学",
                                              course_start_time=datetime.now(), course_end_time=datetime.now(),
                                              course_description="", course_type="必修", course_avatar="")
        cls.course_id_b = cls.myCourseB.course_id

    def testUser(self):
        # FIXME: This DOES NOT guarantee the normal running of user module.
        client = APIClient()
        testApiPrefix = '/api/v1/user/'
        testUserPassword = '123456'
        responseRegister = client.post(testApiPrefix + 'register/',
                                       {'password': testUserPassword, 'university_id': self.university_id, 'school_id': self.school_id,
                                        'realname': 'Never', 'personal_id': 1888888, "character": 4})
        self.assertEqual(responseRegister.status_code, 201)
        testUserID = responseRegister.data["data"]["user_id"]
        responseLogin = client.post(testApiPrefix + 'login/',
                                    {'password': testUserPassword, 'user_id': testUserID})
        self.assertEqual(responseLogin.status_code, 200)
        responseGetAvatar = client.patch(testApiPrefix + 'account/',
                                         {'avatar': "www.baidu.com"})
        self.assertEqual(responseGetAvatar.status_code, 200)
        responseGetAccount = client.get(testApiPrefix + 'account/')
        self.assertEqual(responseGetAccount.data["data"]["university_name"], "Tongji")
        self.assertEqual(responseGetAccount.data["data"]["school_name"], "SSE")
        self.assertEqual(responseGetAccount.data["data"]["avatar"], "www.baidu.com")
        responseLogout = client.post(testApiPrefix + 'logout/')
        self.assertEqual(responseLogout.status_code, 201)

    def testTeacher(self):
        client = APIClient()
        testApiPrefix = '/api/v1/user/'
        testUserPassword = '123456'
        responseRegister = client.post(testApiPrefix + 'register/',
                                       {'password': testUserPassword, 'university_id': self.university_id, 'school_id': self.school_id,
                                        'realname': 'Rika', 'personal_id': 1888885, "character": 1})
        self.assertEqual(responseRegister.status_code, 201)
        testUserID = responseRegister.data["data"]["user_id"]
        responseLogin = client.post(testApiPrefix + 'login/',
                                    {'password': testUserPassword, 'user_id': testUserID})
        self.assertEqual(responseLogin.status_code, 200)
        responseGetAccount = client.get(testApiPrefix + 'account/')
        self.assertEqual(responseGetAccount.data["data"]["character"], 1)
        CoursesData = [
            {"student_id": testUserID, "course_id": self.course_id_a, "active": True},
            {"student_id": testUserID, "course_id": self.course_id_b, "active": False}
        ]
        responseCourses = client.post(
            testApiPrefix + 'courses/', data=json.dumps(CoursesData), content_type='application/json')
        self.assertEqual(responseCourses.status_code, 201)

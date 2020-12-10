from django.test import TestCase, Client
from .models import University, School


class UserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.myUniversity = University.objects.create(university_name="Tongji",
                                                     official_id="201804")
        cls.university_id = cls.myUniversity.university_id
        cls.mySchool = School.objects.create(school_name="SSE",
                                             university_id=cls.myUniversity)
        cls.school_id = cls.mySchool.school_id

    def testUser(self):
        # FIXME: This DOES NOT guarantee the normal running of user module.
        testApiPrefix = '/api/v1/user/'
        testUserPassword = '123456'
        responseRegister = self.client.post(testApiPrefix + 'register/',
                                            {'password': testUserPassword, 'university_id': self.university_id, 'school_id': self.school_id})
        self.assertEqual(responseRegister.status_code, 201)
        testUserID = responseRegister.data["data"]["user_id"]
        responseLogin = self.client.post(testApiPrefix + 'login/',
                                         {'password': testUserPassword, 'user_id': testUserID})
        self.assertEqual(responseLogin.status_code, 200)
        responseGetAccount = self.client.get(testApiPrefix + 'account/')
        self.assertEqual(responseGetAccount.data["data"]["university_name"], "Tongji")
        self.assertEqual(responseGetAccount.data["data"]["school_name"], "SSE")
        responseLogout = self.client.post(testApiPrefix + 'logout/')
        self.assertEqual(responseLogout.status_code, 201)

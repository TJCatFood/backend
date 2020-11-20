from django.db import models

# Create your models here.


class Announcement(models.Model):
    announcement_id = models.AutoField(primary_key=True)
    course_id = models.ForeignKey('class.Course', on_delete=models.CASCADE)
    announcement_title = models.CharField(max_length=50)
    announcement_contents = models.CharField(max_length=1024, null=True)
    announcement_is_pinned = models.BooleanField(default=False)
    announcement_publish_time = models.DateTimeField(auto_now=True)
    announcement_sender_id = models.ForeignKey('user.User', on_delete=models.CASCADE)

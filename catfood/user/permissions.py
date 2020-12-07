from rest_framework.permissions import BasePermission

class IsChargingTeacher(BasePermission):
    """
    Allows access only to charging teachers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.character and request.user.character==1)
    def has_object_permission(self, request, view, obj):
        return True

class IsTeacher(BasePermission):
    """
    Allows access only to teachers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.character and request.user.character==2)
    def has_object_permission(self, request, view, obj):
        return True

class IsTeachingAssistant(BasePermission):
    """
    Allows access only to charging teaching assistants.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.character and request.user.character==3)
    def has_object_permission(self, request, view, obj):
        return True

class IsStudent(BasePermission):
    """
    Allows access only to students.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.character and request.user.character==4)
    def has_object_permission(self, request, view, obj):
        return True

from rest_framework.permissions import BasePermission

class IsChargingTeacher(BasePermission):
    """
    Allows access only to charging teachers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_charging_teacher)
    def has_object_permission(self, request, view, obj):
        return True

class IsTeacher(BasePermission):
    """
    Allows access only to teachers.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_teacher)
    def has_object_permission(self, request, view, obj):
        return True

class IsTeachingAssistant(BasePermission):
    """
    Allows access only to charging teaching assistants.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_teaching_assistant)
    def has_object_permission(self, request, view, obj):
        return True

class IsStudent(BasePermission):
    """
    Allows access only to students.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_student)
    def has_object_permission(self, request, view, obj):
        return True

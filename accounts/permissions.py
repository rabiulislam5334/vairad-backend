from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Allows access only to the owner of the object.
    Assumes the model instance has a `user` attribute
    (or `image.user` for nested objects like Polygon).
    """

    def has_object_permission(self, request, view, obj):
        owner = getattr(obj, 'user', None)
        if owner is None and hasattr(obj, 'image'):
            owner = obj.image.user
        return owner == request.user
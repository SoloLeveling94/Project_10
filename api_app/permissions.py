from django.shortcuts import get_object_or_404
from rest_framework import permissions

from api_app.models import Project


class IsProjectAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if not view.kwargs:
            return True
        else:
            project = get_object_or_404(Project, pk=view.kwargs['pk'])
            user = request.user
            if user in project.users.all() or project.author_user_id == request.user:
                return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Check permissions for read-only request
            return True
        else:
            # Check permissions for write request
            return obj.author_user_id == request.user


class IsIssueAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.kwargs['project__pk']:
            project = get_object_or_404(Project, pk=view.kwargs['project__pk'])
            user = request.user
            if user in project.users.all() or project.author_user_id == request.user:
                return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Check permissions for read-only request
            return True
        else:
            # Check permissions for write request
            return obj.author_user_id == request.user


class IsCommentAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if view.kwargs['project__pk']:
            project = get_object_or_404(Project, pk=view.kwargs['project__pk'])
            user = request.user
            if user in project.users.all() or project.author_user_id == request.user:
                return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Check permissions for read-only request
            return True
        else:
            # Check permissions for write request
            return obj.author_user_id == request.user

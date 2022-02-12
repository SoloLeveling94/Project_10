from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from api_app.models import Project, Issue, Comment
from api_app.permissions import IsProjectAuthorOrReadOnly, IsIssueAuthorOrReadOnly, \
    IsCommentAuthorOrReadOnly
from api_app.serializers import RegistrationSerializer, ProjectSerializer, UserSerializer, \
    IssueSerializer, CommentSerializer


@api_view(['POST'])
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return Response(status=status.HTTP_200_OK)


class RegistrationAV(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            account = serializer.save()
            data['response'] = "Registration Successfull!"
            data['email'] = account.email
            data['first_name'] = account.first_name
            data['last_name'] = account.last_name

            refresh = RefreshToken.for_user(account)
            data['token'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }

        else:
            data = serializer.errors

        return Response(data)


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectAuthorOrReadOnly]

    def get_queryset(self):
        return Project.objects.filter(Q(users=self.request.user.id) |
                                      Q(author_user_id=self.request.user.id))


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, project_pk):
        queryset = User.objects.filter(project_user=project_pk)
        if queryset == queryset.none():
            raise ValidationError("Il n'y a pas d'utilisateurs dans ce projet")
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

    def destroy(self, request, project_pk, user_pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_pk)
        user = User.objects.filter(id=user_pk).first()
        if user is None:
            raise ValidationError("L'utilisateur n'existe pas.")
        project.users.remove(user_pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=HTTP_200_OK)

    def create(self, request, project_pk, *args, **kwargs):
        # Copy and manipulate the request
        data = self.request.data.copy()
        if not User.objects.filter(username=data['username']).exists():
            raise ValidationError("L'utilisateur demandé n'existe pas.")

        add_user = get_object_or_404(User, username=data['username'])
        project = get_object_or_404(Project, pk=project_pk)

        if add_user in project.users.all():
            raise ValidationError("L'utilisateur est déjà inscrit.")

        project.users.add(add_user.pk)
        serializer = UserSerializer(add_user)
        return Response(serializer.data, status=HTTP_200_OK)


class IssueViewSet(ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsIssueAuthorOrReadOnly]

    def create(self, request, *args, **kwargs):
        # Copy and manipulate the request
        data = self.request.data.copy()
        if not User.objects.filter(username=data['assignee_user']).exists():
            raise ValidationError("L'utilisateur demandé n'existe pas.")
        assignee_user = get_object_or_404(User, username=data['assignee_user'])
        data['assignee_user_id'] = assignee_user.pk
        project = Project.objects.get(pk=self.kwargs['project__pk'])
        if not assignee_user in project.users.all():
            raise ValidationError("L'utilisateur assigné n'appartient pas au projet.")
        serializer = self.get_serializer(data=data)

        # if not serializer.is_valid():
        #      raise ValidationError(serializer.errors)
        #
        # A cleaner way for writing the code above
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=HTTP_200_OK)

    def get_queryset(self):
        return Issue.objects.filter(project_id=self.kwargs['project__pk'])


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsCommentAuthorOrReadOnly]

    def get_queryset(self):
        print(f"queryset comment {self.kwargs}")
        return Comment.objects.filter(issue_id=self.kwargs['issue__pk'])

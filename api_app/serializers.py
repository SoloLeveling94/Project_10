from django.contrib.auth.models import User
from rest_framework import serializers

from api_app.models import Project, Issue, Comment


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password', 'password2']

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'error', 'Password should be same ! '})

        if User.objects.filter(email=self.validated_data['email']).exists():
            raise serializers.ValidationError({'error', 'Email already exists !'})

        if User.objects.filter(username=self.validated_data['username']).exists():
            raise serializers.ValidationError({'error', 'Username already exists !'})

        account = User(username=self.validated_data['username'],
                       email=self.validated_data['email'],
                       first_name=self.validated_data['first_name'],
                       last_name=self.validated_data['last_name'])

        account.set_password(password)
        account.save()

        return account


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', ]


class ProjectSerializer(serializers.ModelSerializer):
    users = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Project
        fields = ['id', 'title', 'description', 'type', 'users']
        # fields = "__all__"

    def validate(self, data):
        author = User.objects.get(pk=self.context['request'].user.id)
        data['author_user_id'] = author
        return data


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ('id','title', 'description', 'tag', 'priority', 'status', 'assignee_user_id',
                  'created_time',)

    def validate(self, data):
        project = Project.objects.get(pk=self.context.get('request').parser_context.get('kwargs')['project__pk'])
        author = User.objects.get(pk=self.context['request'].user.id)
        data['project_id'] = project
        data['author_user_id'] = author
        return data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'description', 'created_time',)

    def validate(self, data):
        issue = Issue.objects.get(pk=self.context.get('request').parser_context.get('kwargs')['issue__pk'])
        author = User.objects.get(pk=self.context['request'].user.id)
        data['issue_id'] = issue
        data['author_user_id'] = author
        return data

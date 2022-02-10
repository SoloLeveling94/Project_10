from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)  # change password to hash
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs["is_staff"] = True
        kwargs["is_superuser"] = True
        kwargs["is_active"] = True

        return self.create_user(email=email, password=password, **kwargs)


class Project(models.Model):
    BACKEND = 'BACKEND'
    FRONTEND = 'FRONTEND'
    IOS = 'IOS'
    ANDROID = 'ANDROID'

    TYPE_CHOICES = [
        (BACKEND, 'Back_End'),
        (FRONTEND, 'Front_End'),
        (IOS, 'iOS'),
        (ANDROID, 'Android'),
    ]

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='project_author')
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='project_user', blank=True)

    def __str__(self):
        return self.title


class Issue(models.Model):
    BUG = 'BUG'
    TASK = 'TASK'
    IMPROVEMENT = 'IMPROVEMENT'

    TAG_CHOICES = [
        (BUG, 'Bug'),
        (TASK, 'Tâche'),
        (IMPROVEMENT, 'Amélioration'),
    ]

    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'

    PRIORITY_CHOICES = [
        (HIGH, 'Haute'),
        (MEDIUM, 'Moyenne'),
        (LOW, 'Faible'),
    ]

    ONHOLD = 'ONHOLD'
    WORKINPROGRESS = 'WORKINPROGRESS'
    TODO = 'TODO'
    DONE = 'DONE'

    STATUS_CHOICES = [
        (WORKINPROGRESS, 'En Cours'),
        (TODO, 'A Faire'),
        (DONE, 'Terminé'),
        (ONHOLD, 'En pause'),
    ]

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    tag = models.CharField(max_length=11, choices=TAG_CHOICES)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='issues')
    status = models.CharField(max_length=14, choices=STATUS_CHOICES)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='issue_author')
    assignee_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                         related_name='issue_assignee')
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} from {self.project_id}"


class Comment(models.Model):
    description = models.CharField(max_length=2000)
    author_user_id = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='comment_author')
    issue_id = models.ForeignKey(Issue, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} for {self.issue_id}"
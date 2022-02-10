from django.contrib import admin

from api_app.models import Project, Issue, Comment


admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Comment)

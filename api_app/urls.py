from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from api_app.views import RegistrationAV, logout_view, ProjectViewSet, UserViewSet, IssueViewSet, CommentViewSet

router = routers.SimpleRouter()
router.register('projects', ProjectViewSet, basename='projects')
projects_router = routers.NestedSimpleRouter(router, 'projects', lookup='project')
projects_router.register('issues', IssueViewSet, basename='project_issues')
issues_router = routers.NestedSimpleRouter(projects_router, 'issues', lookup='issue')
issues_router.register('comments', CommentViewSet, basename='issue_comments')

urlpatterns = [
    path('signup/', RegistrationAV.as_view(), name='signup'),
    path('logout/', logout_view, name='logout'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('projects/<int:project_pk>/users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='listcreate_users'),
    path('projects/<int:project_pk>/users/<int:user_pk>/',
         UserViewSet.as_view({'delete': 'destroy'}), name='delete_user')
    ]
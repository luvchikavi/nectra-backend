from django.urls import path
from apps.users.views import (
    login_view, logout_view, user_settings_view, register_view,
    UserManagementView, UserDetailView, RoleChoicesView, CurrentUserView
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('settings/', user_settings_view, name='user-settings'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('users/', UserManagementView.as_view(), name='user-management'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('roles/', RoleChoicesView.as_view(), name='role-choices'),
]

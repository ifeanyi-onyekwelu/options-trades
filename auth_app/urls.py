from django.urls import path
from .views import *

app_name = 'auth'

urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('sign-up/', Signup.as_view(), name='signup'),
    
    path('handle-login/', handle_login, name='handle_login'),
    path('handle-signup/', handle_signup, name='handle_signup'),
    path('logout/', handle_logout, name='handle_logout'),
]
from django.urls import path
from .views import CustomLoginView, SignupView, CustomLogoutView

app_name = 'auth'

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
]

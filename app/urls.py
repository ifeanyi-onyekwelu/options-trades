from django.urls import path
from .views import *

app_name = "app"

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("about-us/", About.as_view(), name="about"),
    path("team/", Team.as_view(), name="team"),
    path("faqs/", FAQs.as_view(), name="faqs"),
    path("contact/", Contact.as_view(), name="contact"),
    path("privacy/", Privacy.as_view(), name="privacy"),
    path(
        "handle-subscribe-to-newsletter/",
        handle_subscribe_newsletter,
        name="handle_subscribe_newsletter",
    ),
]

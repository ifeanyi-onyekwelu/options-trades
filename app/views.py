from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from users.models import User
from django.contrib.auth.models import Group


class Home(TemplateView):
    template_name = "index.html"


class About(TemplateView):
    template_name = "about.html"


class Team(TemplateView):
    template_name = "team.html"


class FAQs(TemplateView):
    template_name = "faq.html"


class Contact(TemplateView):
    template_name = "contact.html"


class Privacy(TemplateView):
    template_name = "privacy.html"


@csrf_exempt
@require_POST
def handle_subscribe_newsletter(request):
    email = request.POST.get("email")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({"status": "error"})

    group, created = Group.objects.get_or_create(name="registered_for_newsletter")

    if user is not None:
        user.groups.add(group)

    return JsonResponse({"status": "success", "message": "Registered to newsletter"})


def custom_error_404(request, e):
    return render(request, "404.html", status=404)


def custom_error_500(request):
    return render(request, "500.html", status=500)

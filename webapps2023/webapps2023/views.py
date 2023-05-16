from django.shortcuts import redirect
from django.views.generic import TemplateView

def redirect_to_webapps(request):
    return redirect('/webapps2023/')
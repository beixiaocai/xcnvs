from app.views.ViewsBase import *
from app.models import *
from django.shortcuts import render


def index(request):
    context = {
        "settings": f_settingsReadData()
    }
    return render(request, 'app/index.html', context)
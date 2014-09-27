import logging
from django.shortcuts import render


def index(request):
    return render(request, "mobile1/index.html")

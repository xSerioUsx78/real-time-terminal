from django.shortcuts import render, HttpResponse


def index(request) -> HttpResponse:
    return render(request, "index.html")

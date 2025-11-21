from django.shortcuts import render
import datetime as dt
from .models import Book

def index(request):
    books = Book.objects.all()
    return render(request, 'library/index.html', {"books": books, "now": dt.datetime.now()})





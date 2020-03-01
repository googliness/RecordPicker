from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Movie
from django.db import connection
import requests


@login_required
def index(request, sync_resp=None):
    movies = {'movies': Movie.objects.order_by('id'), 'sync_resp': sync_resp}
    return render(request, 'index.html', movies)


def syncData(request):
    try:
        resp = requests.get('https://download.data.world/s/l6icehb6kyqewflijey2wysqssbhwx')
        if resp.text:
            resp_text = resp.text.replace('\r', '').replace('"', '').split('\n', 1)[1]
            movies = Movie.objects.order_by('id')
            db_text = '\n'.join([m.title + ',' + str(m.year) + ',' + m.rated + ',' + m.poster for m in movies]) + '\n'
            if resp_text != db_text:
                truncate_custom_sql()
                new_entries = resp_text.split('\n')[:-1]
                for entry in new_entries:
                    cols = entry.split(',')
                    i = 0
                    title = ''
                    while len(cols) - i != 3:
                        title = cols[i]+','
                        i += 1
                    new_movie = Movie(title=title[:-2], year=int(cols[i]), rated=cols[i+1], poster=cols[i+2])
                    new_movie.save()
    except Exception:
        return render(request, 'index.html', {'movies': Movie.objects.order_by('id'), 'sync_resp': 'Oops, sync failed. Please try again later.'})
    return render(request, 'index.html',
                  {'movies': Movie.objects.order_by('id'), 'sync_resp': 'Sync completed Successfully.'})


def truncate_custom_sql():
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE movie;")


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
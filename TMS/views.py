from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as log_out
import json
import secureCred
from django.conf import settings
from django.http import HttpResponseRedirect
from urllib.parse import urlencode
from TMS.models import *
from pymongo import MongoClient

client = MongoClient(secureCred.HOST_URL)
db = client['Lalit']


def home(request):
    return render(request, 'home.html')


@login_required
def myTables(request):
    #collection_name = db["medicinedetails"]
    user_id = request.user.social_auth.get(provider='auth0').uid
    data = UserTables.objects.filter(user_id=user_id).order_by('-id')
    print(data)
    return render(request, 'myTable.html', {'data': data, 'myTables': 'active'})


@login_required
def createTable(request):
    # user_id = request.user.social_auth.get(provider='auth0').uid
    if request.method == 'POST':
        print(request.POST)
        columns = int(request.POST['num_column'])
        if columns == 0:
            return render(request, 'createTable.html', {
                'msg': 'Add At least one column', 'createNew': 'active'})
        for i in range(1, columns+1):
            if request.POST['primary'] == request.POST['name'+str(i)]:
                break
        else:
            return render(request, 'createTable.html', {
                'msg': 'primary key name should be a one column name', 'createNew': 'active'})

        schema = {}
        for i in range(1, columns+1):
            schema[request.POST['name' +
                                str(i)]] = request.POST['type'+str(i)]
        schema['__primary'] = request.POST['primary']

        user_id = request.user.social_auth.get(provider='auth0').uid
        user_email = request.user.social_auth.get(
            provider='auth0').extra_data['email']
        count = UserTables.objects.filter(user_email=user_email).count()
        ref_table_name = user_email+str(count+1)
        UserTables(user_id=user_id, user_email=user_email, table_name=ref_table_name,
                   actual_table_name=request.POST['table_name'], table_schema=schema).save()

        return myTables(request)
    return render(request, 'createTable.html', {'createNew': 'active', })


@login_required
def dashboard(request):
    user = request.user
    auth0user = user.social_auth.get(provider='auth0')
    userdata = {
        'user_id': auth0user.uid,
        'name': user.first_name,
        'picture': auth0user.extra_data['picture'],
        'email': auth0user.extra_data['email'],
    }

    return render(request, 'dashboard.html', {
        'auth0User': auth0user,
        'userdata': json.dumps(userdata, indent=4)
    })


def logout(request):
    log_out(request)
    return_to = urlencode({'returnTo': request.build_absolute_uri('/')})
    logout_url = 'https://%s/v2/logout?client_id=%s&%s' % \
                 (settings.SOCIAL_AUTH_AUTH0_DOMAIN,
                  settings.SOCIAL_AUTH_AUTH0_KEY, return_to)
    return HttpResponseRedirect(logout_url)


def index(request):
    user = request.user
    if user.is_authenticated:
        return redirect(dashboard)
    else:
        return render(request, 'index.html')

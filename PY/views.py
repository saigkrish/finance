from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.html import escape
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
import json

# Create your views here.
@ensure_csrf_cookie
def index(request):
        return render(request, 'fin/index.html', {})

def table(request,ticker):
	template_name='fin/table_'+ticker+'.html'
# Fill the type of user programmatically - TBD
	return render(request, template_name, {'user_profile':'anonymous'})
	#return render(request, template_name, {'user_profile':'nameduser'})
	#return render(request, template_name, {'user_profile':'premiumuser'})
def jspractice(request):
	return render(request, 'fin/js.html', {})

def dfcf_input_modify(request):
        txt=""
        for key in request.POST:
	    value = request.POST[key]           
            txt += str(key) + "::" + str(value) + "<br>"

        txt += "<br><br>"
        dat = request.POST['dfcf_ip_params']
        jdat = json.loads(dat)

        for key in jdat:
	    value = jdat[key]
	    txt += str(key) + "::" + str(value) + "<br>"

        txt += "<br><br>"
        for key in jdat:
	    rev_growth = float(jdat[key]['rev_growth'])
	    ear_growth = float(jdat[key]['earnings_growth'])
	    txt += str(key) + "::" + "revenue grows at" + str(100*rev_growth) + "% <br>"
	    txt += str(key) + "::" + "Earnings grow at" + str(100*ear_growth) + "% <br>"


        txt += "<br><br>Changeset details<br><br>"

        changeset = request.POST['dfcf_ip_changeset']
        jchangeset = json.loads(changeset)

        for key in jchangeset:
	    value = jchangeset[key]
	    txt += str(key) + "::" + str(value) + "<br>"

        txt += "<br><br>"
        txt += escape(repr(request))
    	return HttpResponse(txt)
#	return HttpResponse(request.POST['fname'])

# caller should ensure it is a POST etc.
def fin_auth (request):
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user) 
            return True

    return False

@ensure_csrf_cookie
def dfcf_input(request, action="none"):
    template_name='fin/dfcf_input_parameters.html'
    u = request.user

    if action == "logout":
        logout(request)
        return render(request, template_name, {'user_profile':'anonymous'})
        
    if u.is_authenticated():
        template_name = 'fin/'+u.username+'/dfcf_input_parameters.html'
        return render(request, template_name, {'user_profile':'anonymous'})

    if (request.method != 'POST'):
        return render(request, template_name, {'user_profile':'anonymous'})

    if (fin_auth(request)):
        template_name='fin/'+request.POST.get('username')+'/dfcf_input_parameters.html'

    return render(request, template_name, {'user_profile':'anonymous'})
	#return render(request, template_name, {'user_profile':'nameduser'})
	#return render(request, template_name, {'user_profile':'premiumuser'})

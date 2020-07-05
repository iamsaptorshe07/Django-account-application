from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.conf import settings
from django.contrib import messages
from .models import *
from django.core.mail import send_mail 
from django.core.mail import EmailMultiAlternatives 
from django.template.loader import get_template 
from django.template import Context 
from django.contrib.sites.shortcuts import get_current_site  
from django.utils.encoding import force_bytes, force_text  
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.core.mail import send_mail
from .tokens import activation_token 


# Create your views here.
def userSignup(request):
    if request.method == 'POST':
        try:
            user = User()
            user.name=request.POST['name']
            user.email=request.POST['email']
            user.gender=request.POST['gender']
            if User.objects.filter(email=user.email).exists():
                user = User.objects.get(email=user.email)
                if user.is_active is True:
                    messages.warning(request,'Account is already created')
                    return redirect('login')
                elif user.is_active is False:
                    messages.warning(request,'Check the mail sent on {} to activate your account'.format(user.creationTime))
                    return redirect('/')
            else:
                user.set_password(request.POST['password'])
                user.is_active = False
                user.save()
                site = get_current_site(request)
                mail_subject = 'Site Activation Link'
                message = render_to_string('email.html', {
                    'user': user,
                    'domain': site,
                    'uid':user.id,
                    'token':activation_token.make_token(user)
                })
                to_email=user.email
                to_list=[to_email]
                from_email=settings.EMAIL_HOST_USER
                send_mail(mail_subject,message,from_email,to_list,fail_silently=True)
                messages.success(request,'Check your mail to activate your account')
                return redirect('/')  
        except  Exception as problem:
            messages.error(request,'{}'.format(problem))
            return redirect('signup')
    else:
        return render(request,'signup.html')

def userLogin(request):
    if request.method=='POST':
        try:        
            email=request.POST['email']
            password = request.POST['password']
            if User.objects.filter(email=email).exists():
                user = auth.authenticate(email=email,password=password)
                print(user)
                if user is not None:
                    auth.login(request,user)
                    messages.success(request,'Successfully Loggedin')
                    return redirect('/')
                else:
                    messages.warning(request,'Password does not match')
                    return redirect('login')
            else:
                messages.error(request,'No Account registered with this mail')
                return redirect('login')
        except Exception as problem:
            messages.error(request,problem)
            return redirect('login')
    return render(request,'login.html')


def userLogout(request):
    try:
        auth.logout(request)
        messages.success(request,'Successfully Logged Out')
        return redirect('/')
    except Exception as problem:
        print(problem)
        messages.success(request,'Sorry, Internal Problem Occured')
        return redirect('/')
    
def activate(request, uid, token):
    user = User.objects.get(id=uid)
    if user is not None and activation_token.check_token(user,token):
        user.is_active=True
        user.save()
        return HttpResponse("Account Created Successfully")
    else:
        return HttpResponse("Not created")
   

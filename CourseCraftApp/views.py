from django.shortcuts import render, redirect


# Create your views here.

def index(request):
    user = request.user
    if user.is_authenticated:
        # to course_list page
        return redirect('course_generation:course_list')
    else:
        # to login page
        return redirect('authentication:login')
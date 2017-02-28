from django.http import HttpResponse
from django.shortcuts import render
import os

def reg_complete(request):
    return render(request, 'registration/registration_complete.html' ,{'what':'Reg Completed!'})
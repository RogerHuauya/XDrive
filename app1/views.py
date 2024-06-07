from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse

def my_view(request):
    template = loader.get_template('base.html')
    context = {
        'variable': 'value',
    }
    return HttpResponse(template.render(context, request))
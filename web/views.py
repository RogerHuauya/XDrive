from django.template import loader
from django.http import HttpResponse


def my_view(request):
    template = loader.get_template('web/index.html')
    context = {
        'variable': 'value',
    }
    return HttpResponse(template.render(context, request))

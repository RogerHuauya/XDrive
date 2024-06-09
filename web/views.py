from django.shortcuts import render


def home_page(request):
    context = {
        'variable': 'value',
    }
    return render(request, 'web/index.html', context)

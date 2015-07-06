from django.conf import settings

def base_url(request):
    print(settings.BASE_TEMPLATE)
    return {
        'base_template' : settings.BASE_TEMPLATE,
        'base_navbar' : settings.BASE_NAVBAR
    } 

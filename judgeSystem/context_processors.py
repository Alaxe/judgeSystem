from django.conf import settings

def base_url(request):
    return {
        'base_template' : settings.BASE_TEMPLATE,
        'base_navbar' : settings.BASE_NAVBAR
    } 

from django.contrib import admin
from users.models import Confirmation, PassReset

admin.site.register(Confirmation)
admin.site.register(PassReset)

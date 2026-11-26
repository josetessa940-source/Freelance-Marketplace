from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Project)
admin.site.register(Contract)
admin.site.register(Proposal)
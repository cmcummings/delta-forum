from django.contrib import admin
from .models import Thread, Reply, Subforum, UserTitle

# Register your models here.
admin.site.register(Subforum)
admin.site.register(Thread)
admin.site.register(Reply)
admin.site.register(UserTitle)
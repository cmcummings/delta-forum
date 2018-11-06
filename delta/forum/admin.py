from django.contrib import admin
from .models import Thread, Reply, Subforum

# Register your models here.
admin.site.register(Subforum)
admin.site.register(Thread)
admin.site.register(Reply)
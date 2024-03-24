from django.contrib import admin
from .models import PDF, Document, Image, Summary, ChatHistory
# Register your models here.
admin.site.register(PDF)
admin.site.register(ChatHistory)

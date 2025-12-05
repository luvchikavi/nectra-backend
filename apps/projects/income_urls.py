from django.urls import path
from . import income_views

urlpatterns = [
    path('income/template/', income_views.download_income_template, name='income_template'),
    path('income/upload/', income_views.upload_income_file, name='income_upload'),
]

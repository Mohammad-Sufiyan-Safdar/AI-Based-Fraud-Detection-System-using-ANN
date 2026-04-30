
from django.urls import path
from AdminApp import views

urlpatterns = [
    path('', views.index),
    path('AdminAction', views.AdminAction),
    path('AdminHome', views.AdminHome),
    path('Upload', views.Upload),
    path('UploadAction', views.UploadAction),
    path('preprocess', views.preprocess),
    path('runANN', views.runANN),

]

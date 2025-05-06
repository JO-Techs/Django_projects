from django.urls import path
from . import views

app_name = 'sampleapi'

urlpatterns = [
    path('verify/', views.AadharVerifyAPI.as_view(), name='verify'),
    path('status/<str:request_id>/', views.VerificationStatusAPI.as_view(), name='check_status'),
    path('test/', views.api_test_view, name='test'),
]
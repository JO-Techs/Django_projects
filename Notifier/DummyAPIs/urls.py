# filepath: c:\Users\joelt\Development\notifier\notify-api\dummy_apis\urls.py
from django.urls import path
from .views import DummyAPI1, DummyAPI2, dummy_api1_age_validation_view, dummy_api2_data_validation_view

urlpatterns = [
    path('dummy-api-1/', DummyAPI1.as_view(), name='dummy-api-1'),
    path('dummy-api-2/', DummyAPI2.as_view(), name='dummy-api-2'),
    path('dummy-api-1/validate-age/', dummy_api1_age_validation_view, name='dummy-api-1-age-validation'),
    path('dummy-api-2/validate-data/', dummy_api2_data_validation_view, name='dummy-api-2-data-validation'),
]
from django.urls import path
from .views import DecryptAndVerifyData


urlpatterns = [
    path('decrypt/', DecryptAndVerifyData.as_view(), name='decrypt-client-data'),
]

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from notify.apps.notifications.views import FailureNotificationView, manage_rules_view, frontend_view, failure_logs_view


#def home_view(request):
 #   return HttpResponse("Welcome to the Notify API!")

urlpatterns = [
    path('', frontend_view, name='home'), # USELESS
    path('manage-rules/', manage_rules_view, name='manage-rules'),
    path('notify-failure/', FailureNotificationView.as_view(), name='notify-failure'),
    path('admin/', admin.site.urls),
    path('user-validation/', include('user_validation.urls')),  # USELESS url of user_validation app
    path('dummy-apis/', include('dummy_apis.urls')),  # Dummy API its "dummy-apis"
    path('failure-logs/',failure_logs_view, name='failure-logs'),
]
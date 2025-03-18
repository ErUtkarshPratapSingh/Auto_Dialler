from django.urls import path
from .views import home, webhook_receive  # Ensure views are correctly imported
from .call_logs import call_log_webhook  # ✅ Corrected import


urlpatterns = [
    path('', home, name='home'),  # Home Page URL
    path('webhook-receive/', webhook_receive, name = 'webhook_receive'),
    path("call-log-webhook/", call_log_webhook, name="call_log_webhook"),
]

from django.urls import path
from tokens import views

app_name = "tokens"

urlpatterns = [
    path("",                    views.balance,          name="balance"),
    path("planes/",             views.planes,           name="planes"),
    path("hotmart-webhook/",    views.hotmart_webhook,  name="hotmart_webhook"),
]

from django.urls import path
from mirror import views

app_name = "mirror"

urlpatterns = [
    path("",          views.espejo_home,    name="home"),
    path("nuevo/",    views.espejo_nuevo,   name="nuevo"),
    path("send/",     views.espejo_send,    name="send"),
    path("<int:pk>/archivar/", views.espejo_archivar, name="archivar"),
    path("tarjetas/", views.espejo_tarjetas, name="tarjetas"),
    path("cerebro/",                    views.espejo_cerebro,           name="cerebro"),
    path("cerebro/<int:pk>/restaurar/", views.espejo_cerebro_restaurar, name="cerebro_restaurar"),
    path("cerebro/actualizar/",         views.espejo_cerebro_actualizar, name="cerebro_actualizar"),
]

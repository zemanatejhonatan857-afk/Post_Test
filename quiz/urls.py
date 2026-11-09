from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('jugar/', views.jugar, name='jugar'),
    path('administrador/', views.administrador_login, name='administrador_login'),
    path('panel/', views.panel, name='panel'),
    path(
    'administrador/logout/',
    views.administrador_logout,
    name='administrador_logout'
),
    path(
    'resultado/<int:participante_id>/',
    views.resultado,
    name='resultado'
),
path(
    'exportar/',
    views.exportar,
    name='exportar'
),
path(
    'detalle/<int:participante_id>/',
    views.detalle,
    name='detalle'
),
path(
    'eliminar/<int:participante_id>/',
    views.eliminar_participante,
    name='eliminar_participante'
),
]
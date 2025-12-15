"""
URL configuration for ProyectoV project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from App_V import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'usuarios', views.UsuarioViewSet, basename='api_usuarios')
router.register(r'profesionales', views.ProfesionalViewSet, basename='api_profesionales')
router.register(r'recursos', views.RecursoViewSet, basename='api_recursos')
router.register(r'solicitudes', views.SolicitudViewSet, basename='api_solicitudes')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('base/', views.base, name='base'),
    path('', views.inicio, name='inicio'),
    path('ayuda/', views.lineas_ayuda, name='lineas_ayuda'),
    path('recursos/', views.recursos, name='recursos'),
    path('recursos/<int:id>/editar/', views.recurso_editar, name="recurso_editar"),
    path('recursos/<int:id>/eliminar/', views.recurso_eliminar, name="recurso_eliminar"),
    path('contactos/', views.contactos, name='contactos'),
    path('login/', views.login, name='login'),
    path('solicitudes/', views.solicitudes, name='solicitudes'),
    path('registrar/', views.registrar, name='registrar'),
    path('perfil', views.perfil_usuario, name='perfil_usuario'),
    path('perfil/editar/', views.editar_usuario, name='editar_usuario'),
    path('perfil/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('api/', include(router.urls)),
    path('logout/', views.cerrar_sesion, name='logout'),
    path("recursos/", views.recursos_youtube, name="recursos"), 
    path("recursos/youtube/json/", views.recursos_youtube_json, name="recursos_youtube_json"),

]

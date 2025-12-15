from django.contrib import admin
from .models import Usuarios, Profesionales, Recursos, Solicitudes

@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'nombre', 'correo')
    search_fields = ('nombre', 'correo')

@admin.register(Profesionales)
class ProfesionalesAdmin(admin.ModelAdmin):
    list_display = ('id_profesional', 'nombre', 'especialidad', 'correo', 'telefono')
    search_fields = ('nombre', 'especialidad', 'correo')

@admin.register(Recursos)
class RecursosAdmin(admin.ModelAdmin):
    list_display = ('id_recurso', 'titulo', 'categoria', 'enlace')
    search_fields = ('titulo', 'categoria')

@admin.register(Solicitudes)
class SolicitudesAdmin(admin.ModelAdmin):
    list_display = (
        'id_solicitud',
        'descripcion',
        'fecha',
        'estado',
        'fk_usuario',
        'fk_profesional',
    )
    list_filter = ('estado', 'fecha')
    search_fields = ('descripcion',)

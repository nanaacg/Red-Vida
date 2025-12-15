from rest_framework import serializers
from .models import Usuarios, Profesionales, Recursos, Solicitudes


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuarios
        # No exponemos la contraseña en la API
        fields = ['id_usuario', 'nombre', 'correo']


class ProfesionalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profesionales
        fields = ['id_profesional', 'nombre', 'especialidad', 'correo', 'telefono']


class RecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recursos
        fields = ['id_recurso', 'titulo', 'descripcion', 'enlace', 'categoria']


class SolicitudSerializer(serializers.ModelSerializer):
    # Esto hace que en la API se vea el nombre del usuario/profesional
    usuario = serializers.StringRelatedField(source='fk_usuario', read_only=True)
    profesional = serializers.StringRelatedField(source='fk_profesional', read_only=True)

    class Meta:
        model = Solicitudes
        fields = [
            'id_solicitud',
            'descripcion',
            'fecha',
            'estado',
            'fk_usuario',
            'fk_profesional',
            'usuario',
            'profesional',
        ]

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Profesionales(models.Model):
    id_profesional = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    correo = models.CharField(unique=True, max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'profesionales'
    
    def __str__(self):
        return self.nombre


class Recursos(models.Model):
    id_recurso = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    enlace = models.CharField(max_length=255, blank=True, null=True)
    categoria = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'recursos'

    def __str__(self):
        return self.titulo


class Solicitudes(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    descripcion = models.TextField()
    fecha = models.IntegerField()
    estado = models.CharField(max_length=20)
    fk_usuario = models.ForeignKey('Usuarios', on_delete=models.CASCADE, db_column='FK_USUARIO')
    fk_profesional = models.ForeignKey(Profesionales, on_delete=models.SET_NULL, db_column='FK_PROFESIONAL', null=True)

    class Meta:
        db_table = 'solicitudes'

    
    def __str__(self):
        return f"Solicitud {self.id_solicitud} - Estado: {self.estado}"


class Usuarios(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField(unique=True, max_length=100)
    contraseña = models.CharField(max_length=255)

    rol = models.CharField(
        max_length=20,
        default="usuario",
        choices=[
            ("usuario", "Usuario"),
            ("profesional", "Profesional"),
            ("admin", "Administrador"),
        ]
    )

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.nombre

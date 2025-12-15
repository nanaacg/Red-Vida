from django import forms
from .models import Usuarios, Recursos

class RegistroForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = ['nombre', 'correo', 'contraseña']
        widgets = {
            'contraseña': forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'}),
            'nombre': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'correo': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
        }

class LoginForm(forms.Form):
    correo = forms.EmailField(label="Correo electrónico", max_length=100, widget=forms.EmailInput(attrs={
        'placeholder': 'Ingrese su correo'
    }))
    contraseña = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={
        'placeholder': 'Ingrese su contraseña'
    }))

class ContactoForm(forms.Form):
    nombre = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Tu nombre'}))
    correo = forms.EmailField(max_length=100, widget=forms.EmailInput(attrs={'placeholder': 'Tu correo'}))
    mensaje = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Escribe tu mensaje aquí...'}))

class RecursoForm(forms.ModelForm):
    class Meta:
        model = Recursos
        fields = ['titulo', 'descripcion', 'enlace', 'categoria']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del recurso'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del recurso'}),
            'enlace': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enlace del recurso'}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoría'}),
        }

class RegistroForm(forms.ModelForm):
    contraseña = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña"
    )
    confirmar_contraseña = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar contraseña"
    )

    class Meta:
        model = Usuarios
        fields = ['nombre', 'correo', 'contraseña']

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuarios.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return correo

    def clean(self):
        cleaned_data = super().clean()
        c1 = cleaned_data.get("contraseña")
        c2 = cleaned_data.get("confirmar_contraseña")

        if c1 and c2 and c1 != c2:
            # Error general del formulario (no de un campo específico)
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

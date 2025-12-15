from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from functools import wraps
from datetime import datetime
import requests
import re

from .models import Usuarios, Solicitudes, Profesionales, Recursos
from .forms import RegistroForm, LoginForm, ContactoForm, RecursoForm

from rest_framework import viewsets, permissions
from .serializers import UsuarioSerializer, ProfesionalSerializer, RecursoSerializer, SolicitudSerializer



# Create your views here.

def inicio(request):
    return render(request,'templatesApp/inicio.html')

def lineas_ayuda(request):
    return render(request, 'templatesApp/lineas_ayuda.html')

def recursos(request):
    return render(request, 'templatesApp/recursos.html')

def contactos(request):
    return render(request, 'templatesApp/contactos.html')

def base(request):
    return render(request, 'templatesApp/base.html')

def crear(request):
    return render (request,'templatesApp/crear.html')

def editar(request):
    return render(request,'templatesApp/editar.html')

def lista(request):
    return render(request, 'templatesApp/lista.html')

def login(request):
    return render(request,'templatesApp/login.html')

def registrar(request):
    return render(request,'templatesApp/registrar.html')

def lista_usuarios(request):
    usuarios = Usuarios.Objects.all()
    return render(request, 'templatesApp/lista.html', {'usuarios': usuarios} )



def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        correo = request.POST['correo']
        contraseña = request.POST['contraseña']
        Usuarios.objects.create(nombre=nombre, correo=correo, contraseña=contraseña)
        return redirect('lista_usuarios')
    return render(request, 'templatesApp/crear.html')


def eliminar_usuario(request, id):
    usuario = Usuarios.objects.get(id_usuario=id)
    usuario.delete()
    return redirect('lista_usuarios')


#CRUD USUARIOS

def lista_usuarios(request):
    usuarios = Usuarios.objects.all()
    return render(request, 'templatesApp/lista.html', {'usuarios': usuarios})

def crear_usuario(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        correo = request.POST['correo']
        contraseña = request.POST['contraseña']
        Usuarios.objects.create(nombre=nombre, correo=correo, contraseña=contraseña)
        return redirect('lista_usuarios')
    return render(request, 'templatesApp/crear.html')

def editar_usuario(request, id):
    usuario = Usuarios.objects.get(id_usuario=id)
    if request.method == 'POST':
        usuario.nombre = request.POST['nombre']
        usuario.correo = request.POST['correo']
        usuario.contraseña = request.POST['contraseña']
        usuario.save()
        return redirect('lista_usuarios')
    return render(request, 'templatesApp/editar.html', {'usuario': usuario})

def eliminar_usuario(request, id):
    usuario = Usuarios.objects.get(id_usuario=id)
    usuario.delete()
    return redirect('lista_usuarios')

# Página de inicio o base
def base(request):
    return render(request, 'templatesApp/base.html')

# LOGIN

def login(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contraseña = request.POST.get("contraseña")

        try:
            usuario = Usuarios.objects.get(correo=correo)
        except Usuarios.DoesNotExist:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, "templatesApp/login.html")

        # Comparar contraseña (simple, sin hash)
        if usuario.contraseña != contraseña:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, "templatesApp/login.html")

        # Guardar datos básicos en la sesión
        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre

        messages.success(request, f"Sesión iniciada correctamente, bienvenido/a {usuario.nombre}.")
        return redirect("inicio")  # asegúrate que esta URL existe

    # GET
    return render(request, "templatesApp/login.html")

# REGISTRO

def registrar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        rol = request.POST.get("rol")
        c1 = request.POST.get("contraseña")
        c2 = request.POST.get("confirmar_contraseña")

        # 1) Validar contraseñas iguales
        if c1 != c2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "templatesApp/registrar.html")

        # 2) Validar correo único
        if Usuarios.objects.filter(correo=correo).exists():
            messages.error(request, "Este correo ya está registrado, intenta con otro.")
            return render(request, "templatesApp/registrar.html")

        # 3) Crear usuario en la BD
        Usuarios.objects.create(
            nombre=nombre,
            correo=correo,
            contraseña=c1,
            rol=rol
        )

        # 4) Mensaje de éxito y redirección a login
        messages.success(request, "Tu cuenta se creó con éxito. Ahora puedes iniciar sesión.")
        return redirect("login")

    # GET: solo muestra el formulario, sin 'form'
    return render(request, "templatesApp/registrar.html")

# INICIO (después de login)

def inicio(request):
    usuario_id = request.session.get('usuario_id')
    contexto = {}

    
    if usuario_id:
        try:
            usuario = Usuarios.objects.get(id_usuario=usuario_id)
            contexto['usuario'] = usuario
        except Usuarios.DoesNotExist:
            pass

    return render(request, 'templatesApp/inicio.html', contexto)

def contactos(request):
    usuario = obtener_usuario_actual(request)
    rol = usuario.rol if usuario else None

    if request.method == 'POST':
        # Solo profesional o admin pueden registrar nuevos profesionales
        if not usuario or rol not in ["profesional", "admin"]:
            messages.error(request, "No tienes permiso para registrar profesionales.")
            return redirect('contactos')

        nombre = request.POST.get('nombre')
        especialidad = request.POST.get('especialidad')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')

        if nombre and correo:
            Profesionales.objects.create(
                nombre=nombre,
                especialidad=especialidad,
                correo=correo,
                telefono=telefono
            )
            messages.success(request, "Profesional registrado correctamente.")
        else:
            messages.error(request, "Nombre y correo son obligatorios.")

        return redirect('contactos')

    profesionales = Profesionales.objects.all()
    return render(request, 'templatesApp/contactos.html', {
        'profesionales': profesionales,
        'rol': rol,
    })



def solicitudes(request):
    usuarios = Usuarios.objects.all()
    profesionales = Profesionales.objects.all()

    if request.method == 'POST':
        descripcion = request.POST.get('descripcion')
        fecha = datetime.now().year
        estado = request.POST.get('estado')
        fk_usuario_id = request.POST.get('fk_usuario')
        fk_profesional_id = request.POST.get('fk_profesional')

        if descripcion and fk_usuario_id and fk_profesional_id:
            Solicitudes.objects.create(
                descripcion=descripcion,
                fecha=fecha,
                estado=estado,
                fk_usuario_id=fk_usuario_id,
                fk_profesional_id=fk_profesional_id
            )
            return redirect('solicitudes')

    solicitudes = Solicitudes.objects.select_related('fk_usuario', 'fk_profesional').all()
    return render(request, 'templatesApp/solicitudes.html', {
        'solicitudes': solicitudes,
        'usuarios': usuarios,
        'profesionales': profesionales
    })


def perfil_usuario(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario = Usuarios.objects.get(id_usuario=request.session['usuario_id'])
    return render(request, 'templatesApp/perfil.html', {'usuario': usuario})


# Eliminar cuenta
def eliminar_usuario(request):
    if 'usuario_id' not in request.session:
        return redirect('login')

    usuario = get_object_or_404(Usuarios, id_usuario=request.session['usuario_id'])

    if request.method == 'POST':
        usuario.delete()
        request.session.flush()
        messages.success(request, '🗑️ Tu cuenta ha sido eliminada correctamente.')
        return redirect('inicio')

    return render(request, 'templatesApp/eliminar_usuario.html', {'usuario': usuario})

def login_requerido(vista_func):
    @wraps(vista_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('ususario_id'):
            messages.warning(request="Debes iniciar sesion para acceder al sitio web")
            return redirect('login')
        return vista_func(request, *args, **kwargs)
    return _wrapped_view

def login_requerido(vista_func):
    def _wrapped_view(request, *args, **kwargs):
        if "usuario_id" not in request.session:
            # 👇 AQUÍ ESTABA EL ERROR: ahora va (request, "mensaje")
            messages.warning(request, "Debes iniciar sesión para acceder al sitio web.")
            return redirect("login")
        return vista_func(request, *args, **kwargs)
    return _wrapped_view



# ----------------------------------------------
# DECORADOR: LOGIN REQUERIDO
# ----------------------------------------------
def login_requerido(vista_func):
    def _wrapped_view(request, *args, **kwargs):
        if "usuario_id" not in request.session:
            messages.warning(request, "Debes iniciar sesión para acceder al sitio web.")
            return redirect("login")
        return vista_func(request, *args, **kwargs)
    return _wrapped_view

# ----------------------------------------------
# INICIO
# ----------------------------------------------
def inicio(request):
    usuario_id = request.session.get("usuario_id")
    usuario = None

    if usuario_id:
        try:
            usuario = Usuarios.objects.get(id_usuario=usuario_id)
        except Usuarios.DoesNotExist:
            pass

    return render(request, "templatesApp/inicio.html", {"usuario": usuario})


# ----------------------------------------------
# LOGIN
# ----------------------------------------------
def login(request):
    if request.method == "POST":
        correo = request.POST.get("correo")
        contraseña = request.POST.get("contraseña")

        try:
            usuario = Usuarios.objects.get(correo=correo)
        except Usuarios.DoesNotExist:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, "templatesApp/login.html")

        
        if not check_password(contraseña, usuario.contraseña):
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, "templatesApp/login.html")

        request.session["usuario_id"] = usuario.id_usuario
        request.session["usuario_nombre"] = usuario.nombre
        request.session["usuario_rol"] = usuario.rol

        messages.success(request, f"Sesión iniciada correctamente, bienvenido/a {usuario.nombre}.")
        return redirect("inicio")

    return render(request, "templatesApp/login.html")

# ----------------------------------------------
# REGISTRO
# ----------------------------------------------
def registrar(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        c1 = request.POST.get("contraseña")
        c2 = request.POST.get("confirmar_contraseña")
        rol = request.POST.get("rol")

        if c1 != c2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, "templatesApp/registrar.html")

        if not password_segura(c1):
            messages.error(request, "La contraseña debe tener mínimo 8 caracteres e incluir mayúscula, minúscula, número y un símbolo.")
            return render(request, "templatesApp/registrar.html")

        if Usuarios.objects.filter(correo=correo).exists():
            messages.error(request, "Este correo ya está registrado, intenta con otro.")
            return render(request, "templatesApp/registrar.html")

        Usuarios.objects.create(
            nombre=nombre,
            correo=correo,
            contraseña=make_password(c1),
            rol=rol
        )

        messages.success(request, "Tu cuenta se creó con éxito. Ahora puedes iniciar sesión.")
        return redirect("login")

    return render(request, "templatesApp/registrar.html")


# ----------------------------------------------
# PERFIL USUARIO
# ----------------------------------------------
@login_requerido
def perfil_usuario(request):
    usuario = Usuarios.objects.get(id_usuario=request.session["usuario_id"])
    return render(request, "templatesApp/perfil.html", {"usuario": usuario})


# ----------------------------------------------
# EDITAR USUARIO
# ----------------------------------------------
@login_requerido
def editar_usuario(request):

    usuario = Usuarios.objects.get(id_usuario=request.session["usuario_id"])

    if request.method == "POST":
        usuario.nombre = request.POST.get("nombre")
        usuario.correo = request.POST.get("correo")

        nueva_contra = request.POST.get("contraseña")
        if nueva_contra:
            # 🔐 Validar seguridad de la nueva contraseña
            if not password_segura(nueva_contra):
                messages.error(
                    request,
                    "La contraseña debe tener mínimo 8 caracteres e incluir "
                    "mayúscula, minúscula, número y un símbolo."
                )
                return render(request, 'templatesApp/editar_usuario.html', {'usuario': usuario})
            

            # 🔐 Guardar contraseña hasheada
            usuario.contraseña = make_password(nueva_contra)

        usuario.save()
        messages.success(request, '✅ Tu cuenta fue actualizada con éxito.')
        return redirect('perfil_usuario')


    return render(request, "templatesApp/editar_usuario.html", {"usuario": usuario})


# ----------------------------------------------
# ELIMINAR USUARIO
# ----------------------------------------------
@login_requerido
def eliminar_usuario(request):

    usuario = get_object_or_404(Usuarios, id_usuario=request.session["usuario_id"])

    if request.method == "POST":
        usuario.delete()
        request.session.flush()
        messages.success(request, "Cuenta eliminada correctamente.")
        return redirect("inicio")

    return render(request, "templatesApp/eliminar_usuario.html")


# ----------------------------------------------
# CONTACTOS (PROFESIONALES)
# ----------------------------------------------
def contactos(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        especialidad = request.POST.get("especialidad")
        correo = request.POST.get("correo")
        telefono = request.POST.get("telefono")

        Profesionales.objects.create(
            nombre=nombre,
            especialidad=especialidad,
            correo=correo,
            telefono=telefono
        )
        messages.success(request, "Profesional agregado correctamente.")
        return redirect("contactos")

    profesionales = Profesionales.objects.all()
    return render(request, "templatesApp/contactos.html", {"profesionales": profesionales})


# ----------------------------------------------
# RECURSOS
# ----------------------------------------------
def recursos(request):
    # Rol desde sesión
    rol = request.session.get("usuario_rol")

    # -------------------------------
    # RECURSOS DESDE BASE DE DATOS
    # -------------------------------
    recursos_qs = Recursos.objects.all().order_by("-id_recurso")
    form = RecursoForm()

    # -------------------------------
    # AGREGAR RECURSO (ADMIN / PROFESIONAL)
    # -------------------------------
    if request.method == "POST":
        if rol not in ["admin", "profesional"]:
            messages.error(request, "No tienes permiso para agregar recursos.")
            return redirect("recursos")

        form = RecursoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Recurso agregado correctamente.")
            return redirect("recursos")
        else:
            messages.error(request, "Revisa los campos del formulario.")

    # -------------------------------
    # API EXTERNA: YOUTUBE
    # -------------------------------
    youtube_query = request.GET.get("q", "").strip()
    youtube_videos = []
    youtube_error = None

    if youtube_query:
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "type": "video",
                "maxResults": 6,
                "q": youtube_query,
                "safeSearch": "strict",
                "key": settings.YOUTUBE_API_KEY,
            }

            response = requests.get(url, params=params, timeout=8)
            response.raise_for_status()
            data = response.json()

            for item in data.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                snippet = item.get("snippet", {})

                if video_id:
                    youtube_videos.append({
                        "titulo": snippet.get("title"),
                        "canal": snippet.get("channelTitle"),
                        "thumb": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    })

        except Exception as e:
            youtube_error = "No se pudo conectar con YouTube."
            print("ERROR YOUTUBE:", e)

    # -------------------------------
    # RENDER FINAL
    # -------------------------------
    return render(request, "templatesApp/recursos.html", {
        "recursos": recursos_qs,
        "form": form,
        "rol": rol,

        # 👇 variables para el buscador YouTube
        "youtube_query": youtube_query,
        "youtube_videos": youtube_videos,
        "youtube_error": youtube_error,
    })


# ----------------------------------------------
def recurso_editar(request, id):
    rol = request.session.get("usuario_rol")
    if rol not in ["admin", "profesional"]:
        messages.error(request, "No tienes permiso para editar recursos.")
        return redirect("recursos")

    recurso = get_object_or_404(Recursos, id_recurso=id)
    form = RecursoForm(instance=recurso)

    if request.method == "POST":
        form = RecursoForm(request.POST, instance=recurso)
        if form.is_valid():
            form.save()
            messages.success(request, "Recurso actualizado correctamente.")
            return redirect("recursos")

    return render(request, "templatesApp/recurso_editar.html", {"form": form, "recurso": recurso})


def recurso_eliminar(request, id):
    rol = request.session.get("usuario_rol")
    if rol not in ["admin", "profesional"]:
        messages.error(request, "No tienes permiso para eliminar recursos.")
        return redirect("recursos")

    recurso = get_object_or_404(Recursos, id_recurso=id)

    if request.method == "POST":
        recurso.delete()
        messages.success(request, "Recurso eliminado correctamente.")
        return redirect("recursos")

    return render(request, "templatesApp/recurso_eliminar.html", {"recurso": recurso})



# ----------------------------------------------

# ----------------------------------------------
# SOLICITUDES
# ----------------------------------------------
def solicitudes(request):
    usuarios = Usuarios.objects.all()
    profesionales = Profesionales.objects.all()

    if request.method == "POST":
        descripcion = request.POST.get("descripcion")
        estado = request.POST.get("estado")
        fk_usuario = request.POST.get("fk_usuario")
        fk_profesional = request.POST.get("fk_profesional")

        Solicitudes.objects.create(
            descripcion=descripcion,
            fecha=datetime.now().year,
            estado=estado,
            fk_usuario_id=fk_usuario,
            fk_profesional_id=fk_profesional
        )

        messages.success(request, "Solicitud registrada correctamente.")
        return redirect("solicitudes")

    solicitudes = Solicitudes.objects.select_related("fk_usuario", "fk_profesional").all()

    return render(request, "templatesApp/solicitudes.html", {
        "solicitudes": solicitudes,
        "usuarios": usuarios,
        "profesionales": profesionales
    })



# --- EJEMPLO: VISTA PERFIL PROTEGIDA ---
@login_requerido
def perfil_usuario(request):
    usuario_id = request.session.get("usuario_id")
    usuario = Usuarios.objects.get(id_usuario=usuario_id)

    return render(request, "templatesApp/perfil.html", {
        "usuario": usuario
    })

class UsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Solo lectura de usuarios (lista y detalle).
    No permitimos crear/editar/borrar usuarios por aquí para no chocar con tu registro normal.
    """
    queryset = Usuarios.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]

class ProfesionalViewSet(viewsets.ModelViewSet):
    """
    CRUD completo de profesionales vía API.
    """
    queryset = Profesionales.objects.all()
    serializer_class = ProfesionalSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RecursoViewSet(viewsets.ModelViewSet):
    queryset = Recursos.objects.all()
    serializer_class = RecursoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]



class SolicitudViewSet(viewsets.ModelViewSet):
    queryset = Solicitudes.objects.all()
    serializer_class = SolicitudSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


def cerrar_sesion(request):
    # Elimina toda la sesión
    request.session.flush()

    # Mensaje opcional
    messages.success(request, "Sesión cerrada correctamente.")

    # Redirige al inicio
    return redirect('inicio')

def rol_requerido(*roles_permitidos):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            rol = request.session.get("usuario_rol")

            if rol not in roles_permitidos:
                messages.error(request, "No tienes permisos para acceder aquí.")
                return redirect("inicio")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def obtener_usuario_actual(request):
    """
    Devuelve el modelo Usuarios asociado a la sesión
    o None si no hay sesión activa.
    """
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    try:
        return Usuarios.objects.get(id_usuario=usuario_id)
    except Usuarios.DoesNotExist:
        return None

@login_requerido
def solicitudes(request):
    usuario = obtener_usuario_actual(request)
    rol = usuario.rol if usuario else None

    # Listas que usaremos para selects
    usuarios = Usuarios.objects.all()
    profesionales = Profesionales.objects.all()

    if request.method == 'POST':
        # Solo USUARIO normal puede crear solicitudes
        if rol != "usuario":
            messages.error(request, "Solo los usuarios pueden generar solicitudes.")
            return redirect('solicitudes')

        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado') or "Pendiente"
        fk_profesional_id = request.POST.get('fk_profesional')

        if descripcion and fk_profesional_id:
            Solicitudes.objects.create(
                descripcion=descripcion,
                fecha=datetime.now().year,
                estado=estado,
                fk_usuario_id=usuario.id_usuario,      # se asocia al usuario logueado
                fk_profesional_id=fk_profesional_id
            )
            messages.success(request, "Solicitud creada correctamente.")
            return redirect('solicitudes')
        else:
            messages.error(request, "Debe ingresar descripción y profesional.")

    # GET → qué ve cada tipo de usuario
    if rol == "usuario":
        # Usuario solo ve SUS solicitudes
        solicitudes_qs = Solicitudes.objects.filter(
            fk_usuario_id=usuario.id_usuario
        ).select_related('fk_usuario', 'fk_profesional')
    else:
        # Profesional y admin ven TODAS
        solicitudes_qs = Solicitudes.objects.select_related(
            'fk_usuario', 'fk_profesional'
        ).all()

    return render(request, 'templatesApp/solicitudes.html', {
        'solicitudes': solicitudes_qs,
        'usuarios': usuarios,
        'profesionales': profesionales,
        'rol': rol,
    })


@login_requerido
def recursos_youtube(request):
    """
    Muestra tu pantalla de recursos + resultados de YouTube (videos).
    Usa la misma plantilla: templatesApp/recursos.html
    """
    # 1) Tu listado normal de recursos (BD)
    recursos = Recursos.objects.all().order_by("-id_recurso")

    # 2) Buscar videos según lo que escriba el usuario
    q = request.GET.get("q", "").strip()
    videos = []
    error_api = None

    if q:
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "type": "video",
                "maxResults": 6,
                "q": q,
                "safeSearch": "strict",
                "key": settings.YOUTUBE_API_KEY,
            }
            r = requests.get(url, params=params, timeout=8)
            r.raise_for_status()
            data = r.json()

            # Normalizamos lo que necesitamos para el template
            for item in data.get("items", []):
                video_id = item["id"].get("videoId")
                snip = item.get("snippet", {})
                if video_id:
                    videos.append({
                        "titulo": snip.get("title"),
                        "canal": snip.get("channelTitle"),
                        "thumb": (snip.get("thumbnails", {}).get("medium", {}) or {}).get("url"),
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                    })

        except Exception as e:
            error_api = "No se pudo conectar a YouTube o hubo un error con la API Key."
            # opcional: mostrar detalle en consola
            print("ERROR YOUTUBE:", e)

    # 3) Renderizamos TU MISMA plantilla con datos extra
    return render(request, "templatesApp/recursos.html", {
        "recursos": recursos,
        "youtube_query": q,
        "youtube_videos": videos,
        "youtube_error": error_api
    })


@login_requerido
def recursos_youtube_json(request):
    q = request.GET.get("q", "salud mental").strip()

    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "type": "video",
        "maxResults": 6,
        "q": q,
        "safeSearch": "strict",
        "key": settings.YOUTUBE_API_KEY,
    }

    r = requests.get(url, params=params, timeout=8)
    return JsonResponse(r.json(), safe=False)



# =========================================================
# SEGURIDAD CONTRASEÑA
# =========================================================

def password_segura(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]", password):
        return False
    return True

# -------------------------------------

def login_requerido(vista_func):
    @wraps(vista_func)
    def _wrapped_view(request, *args, **kwargs):
        if "usuario_id" not in request.session:
            messages.warning(request, "Debes iniciar sesión para acceder.")
            return redirect("login")
        return vista_func(request, *args, **kwargs)
    return _wrapped_view


def obtener_usuario_actual(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        return None
    try:
        return Usuarios.objects.get(id_usuario=usuario_id)
    except Usuarios.DoesNotExist:
        return None
 

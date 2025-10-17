from django.shortcuts import render, get_object_or_404, redirect
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth import login as auth_login
from datetime import datetime, date
from django.db.models import F
from django.utils.timezone import now
from django.urls import reverse



def listar_proyectos(request):
    proyectos = Proyecto.objects.all()
    return render(request, 'tareas/seleccionarproyecto.html', {'proyectos': proyectos})



def crear_usuario(request):
    errores = []
    mensaje_exito = None

    if request.method == 'POST':
        # Obtener datos del formulario
        rut = request.POST.get('rut', '').upper()
        nombre = request.POST.get('nombre', '').upper()
        primer_apellido = request.POST.get('primer_apellido', '').upper()
        segundo_apellido = request.POST.get('segundo_apellido', '').upper()
        cargo_id = request.POST.get('cargo')
        correo_electronico = request.POST.get('correo_electronico', '').strip()

        # Validar datos básicos
        if not rut or not nombre or not primer_apellido or not cargo_id:
            errores.append("Todos los campos obligatorios deben ser completados.")
        
        # Validar si el correo es obligatorio para jefe o capataz
        if cargo_id:
            cargo = Cargo.objects.get(id=cargo_id)
            if cargo.nombre_cargo.upper() in ["JEFE", "CAPATAZ"] and not correo_electronico:
                errores.append("El correo electrónico es obligatorio para los cargos de jefe y capataz.")
        
        # Verificar si el usuario ya existe
        if Usuario.objects.filter(rut=rut).exists():
            errores.append("El RUT ya está registrado.")

        # Crear usuario si no hay errores
        if not errores:
            # Obtener el estado "ACTIVO" sin usar get_or_create
            estado_activo = Estado.objects.get(nombre_estado="ACTIVO")
            Usuario.objects.create(
                rut=rut,
                nombre=nombre,
                primer_apellido=primer_apellido,
                segundo_apellido=segundo_apellido,
                cargo=cargo,
                correo_electronico=correo_electronico,
                estado=estado_activo,
                contrasena="111"  # Contraseña por defecto
            )
            mensaje_exito = "Usuario creado correctamente."

    cargos = Cargo.objects.all()

    return render(request, 'Usuarios/CrearUsuario.html', {
        'mensaje_exito': mensaje_exito,
        'errores': errores,
        'rut': rut if 'rut' in locals() else '',
        'nombre': nombre if 'nombre' in locals() else '',
        'primer_apellido': primer_apellido if 'primer_apellido' in locals() else '',
        'segundo_apellido': segundo_apellido if 'segundo_apellido' in locals() else '',
        'correo_electronico': correo_electronico if 'correo_electronico' in locals() else '',
        'cargo_id': cargo_id if 'cargo_id' in locals() else '',
        'cargos': cargos,
    })



def mostrar_usuario(request):
    # Determinar el estado a mostrar basado en el parámetro GET
    estado_param = request.GET.get('estado', 'activo').upper()  # Por defecto muestra 'ACTIVO'
    
    # Filtrar usuarios por el estado seleccionado
    usuarios = Usuario.objects.select_related('cargo', 'estado', 'cuadrilla', 'cuadrilla__capataz').filter(
        estado__nombre_estado=estado_param
    )

    usuarios_info = []
    for usuario in usuarios:
        # Obtener el proyecto asociado a la cuadrilla del usuario, si existe
        proyecto_nombre = ""
        if usuario.cuadrilla:
            proyecto_cuadrilla = ProyectoCuadrilla.objects.filter(cuadrilla=usuario.cuadrilla).first()
            if proyecto_cuadrilla:
                proyecto_nombre = proyecto_cuadrilla.proyecto.nombre_proyecto

        # Agregar datos de usuario con valores en blanco si faltan
        usuarios_info.append({
            'id': usuario.id,
            'rut': usuario.rut,
            'nombre': usuario.nombre,
            'primer_apellido': usuario.primer_apellido,
            'segundo_apellido': usuario.segundo_apellido,
            'cargo': usuario.cargo.nombre_cargo if usuario.cargo else "",
            'estado': usuario.estado.nombre_estado if usuario.estado else "",
            'cuadrilla': usuario.cuadrilla.codigo_cuadrilla if usuario.cuadrilla else "",
            'capataz': usuario.cuadrilla.capataz.nombre_completo if usuario.cuadrilla and usuario.cuadrilla.capataz else "",
            'proyecto': proyecto_nombre,
        })

    # Renderizar la plantilla con la lista de usuarios y la información extraída
    return render(request, 'Usuarios/MostrarUsuario.html', {
        'usuarios': usuarios_info,
        'estado_mostrado': estado_param  # Pasar el estado actual para la lógica de botones en el HTML
    })



def editar_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    cargos = Cargo.objects.all()
    errores = []

    # Obtener mensaje de éxito desde la sesión, si existe
    errores = request.session.pop('errores', None)
    mensaje_exito = request.session.pop('mensaje_exito', None)

    # Obtener datos de proyecto, cuadrilla y capataz si están asociados
    cuadrilla = usuario.cuadrilla.codigo_cuadrilla if usuario.cuadrilla else ""
    capataz = usuario.cuadrilla.capataz.nombre_completo if usuario.cuadrilla and usuario.cuadrilla.capataz else ""
    proyecto_cuadrilla = ProyectoCuadrilla.objects.filter(cuadrilla=usuario.cuadrilla).first()
    proyecto = proyecto_cuadrilla.proyecto.nombre_proyecto if proyecto_cuadrilla else ""

    # Determinar si el cargo es editable
    cargo_editable = usuario.cuadrilla is None  # True si no tiene cuadrilla asignada

    if request.method == 'POST':
        usuario.nombre = request.POST.get('nombre', '').upper()
        usuario.primer_apellido = request.POST.get('primer_apellido', '').upper()
        usuario.segundo_apellido = request.POST.get('segundo_apellido', '').upper()
        usuario.correo_electronico = request.POST.get('correo_electronico', '').strip()
        cargo_id = request.POST.get('cargo')

      # Asignar el cargo solo si es editable
        if cargo_editable and cargo_id:
            usuario.cargo = get_object_or_404(Cargo, id=cargo_id)
        
        usuario.save()
        mensaje_exito = "Usuario actualizado correctamente."

    return render(request, 'Usuarios/EditarUsuario.html', {
        'usuario': usuario,
        'cargos': cargos,
        'mensaje_exito': mensaje_exito,
        'errores': errores,
        'proyecto': proyecto,
        'cuadrilla': cuadrilla,
        'capataz': capataz,
        'cargo_editable': cargo_editable,
    })



def cambiar_estado_usuario(request, usuario_id):
    usuario = get_object_or_404(Usuario, id=usuario_id)
    estado_actual = usuario.estado.nombre_estado

    # Verificar si el usuario está activo y tiene una cuadrilla asignada
    if estado_actual == "ACTIVO" and usuario.cuadrilla:
        # No permitir el cambio a inactivo si tiene cuadrilla asignada
        request.session['errores'] = ["No se puede cambiar el estado a INACTIVO porque el usuario tiene una cuadrilla asignada."]
        return redirect('editar_usuario', usuario_id=usuario.id)

    # Determinar el nuevo estado
    nuevo_estado = get_object_or_404(Estado, nombre_estado="INACTIVO" if estado_actual == "ACTIVO" else "ACTIVO")
    usuario.estado = nuevo_estado
    usuario.save()

    # Guardar mensaje de éxito en la sesión
    request.session['mensaje_exito'] = f"Estado cambiado a {nuevo_estado.nombre_estado}."

    return redirect('editar_usuario', usuario_id=usuario.id)



def crear_cuadrilla(request):
    mensaje_exito = None
    errores = []

    # Obtener proyectos y capataces activos sin cuadrilla asignada
    proyectos = Proyecto.objects.all()
    capataces = Usuario.objects.filter(cargo__nombre_cargo="Capataz", cuadrilla__isnull=True, estado__nombre_estado="ACTIVO")

    # Generar el próximo código de cuadrilla
    ultimo_id = Cuadrilla.objects.latest('id').id if Cuadrilla.objects.exists() else 0
    codigo_cuadrilla = f"C-{ultimo_id + 1:04d}"

    if request.method == 'POST':
        proyecto_id = request.POST.get('proyecto')
        capataz_id = request.POST.get('capataz')

        # Verificar si se seleccionó un proyecto
        if not proyecto_id:
            errores.append("Debe seleccionar un proyecto.")
        else:
            proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        # Verificar si se seleccionó un capataz
        if not capataz_id:
            errores.append("Debe seleccionar un capataz.")
        else:
            capataz = get_object_or_404(Usuario, id=capataz_id)

        # Crear la cuadrilla solo si no hay errores
        if not errores:
            nueva_cuadrilla = Cuadrilla.objects.create(capataz=capataz, codigo_cuadrilla=codigo_cuadrilla)
            ProyectoCuadrilla.objects.create(proyecto=proyecto, cuadrilla=nueva_cuadrilla)
            mensaje_exito = "Cuadrilla creada exitosamente."

    return render(request, 'Usuarios/CrearCuadrilla.html', {
        'proyectos': proyectos,
        'capataces': capataces,
        'codigo_cuadrilla': codigo_cuadrilla,
        'mensaje_exito': mensaje_exito,
        'errores': errores,
    })



def crear_proyecto(request):
    errores = []
    mensaje_exito = None

    if request.method == 'POST':
        nombre_proyecto = request.POST.get('nombre_proyecto', '').strip()
        ubicacion = request.POST.get('ubicacion', '').strip()
        fecha_inicio = request.POST.get('fecha_inicio', '').strip()
        fecha_termino = request.POST.get('fecha_termino', '').strip()

        # Validación simple
        if not nombre_proyecto or not ubicacion or not fecha_inicio or not fecha_termino:
            errores.append("Todos los campos son obligatorios.")
        else:
            # Crear el proyecto
            Proyecto.objects.create(
                nombre_proyecto=nombre_proyecto,
                ubicacion=ubicacion,
                fecha_inicio=fecha_inicio,
                fecha_termino=fecha_termino
            )
            mensaje_exito = "Proyecto creado correctamente."
            return redirect('crear_proyecto')  # Redirige para limpiar el formulario

    # Obtener todos los proyectos para mostrarlos
    proyectos = Proyecto.objects.all()

    return render(request, 'Usuarios/CrearProyecto.html', {
        'mensaje_exito': mensaje_exito,
        'errores': errores,
        'proyectos': proyectos,
    })



def gestionar_cuadrilla(request):
    mensaje_exito = None
    errores = []

    # Obtener proyectos y capataces activos sin cuadrilla asignada
    proyectos = Proyecto.objects.all()
    capataces = Usuario.objects.filter(cargo__nombre_cargo="Capataz", cuadrilla__isnull=True, estado__nombre_estado="ACTIVO")

    # Si el método es POST, procesamos el formulario de creación
    if request.method == 'POST':
        codigo_cuadrilla = request.POST.get('codigo_cuadrilla', '').strip()
        proyecto_id = request.POST.get('proyecto')
        capataz_id = request.POST.get('capataz')

        # Validación de campos
        if not codigo_cuadrilla:
            errores.append("Debe ingresar un código de cuadrilla.")
        if not proyecto_id:
            errores.append("Debe seleccionar un proyecto.")
        if not capataz_id:
            errores.append("Debe seleccionar un capataz.")

        # Crear la cuadrilla si no hay errores
        if not errores:
            proyecto = get_object_or_404(Proyecto, id=proyecto_id)
            capataz = get_object_or_404(Usuario, id=capataz_id)
            nueva_cuadrilla = Cuadrilla.objects.create(capataz=capataz, codigo_cuadrilla=codigo_cuadrilla)
            ProyectoCuadrilla.objects.create(proyecto=proyecto, cuadrilla=nueva_cuadrilla)
            
            # Asignar la cuadrilla al capataz
            capataz.cuadrilla = nueva_cuadrilla
            capataz.save()
            
            mensaje_exito = "Cuadrilla creada exitosamente."

    # Obtener todas las cuadrillas para mostrar en la tabla
    cuadrillas_info = []
    cuadrillas = Cuadrilla.objects.all()
    for cuadrilla in cuadrillas:
        proyecto_cuadrilla = ProyectoCuadrilla.objects.filter(cuadrilla=cuadrilla).first()
        proyecto_nombre = proyecto_cuadrilla.proyecto.nombre_proyecto if proyecto_cuadrilla else ""
        cuadrillas_info.append({
            'id': cuadrilla.id,
            'codigo_cuadrilla': cuadrilla.codigo_cuadrilla,
            'capataz': cuadrilla.capataz.nombre_completo if cuadrilla.capataz else "",
            'proyecto': proyecto_nombre,
            'trabajadores_count': cuadrilla.usuario_set.count(),
        })

    return render(request, 'Usuarios/Cuadrilla.html', {
        'proyectos': proyectos,
        'capataces': capataces,
        'cuadrillas': cuadrillas_info,
        'mensaje_exito': mensaje_exito,
        'errores': errores,
    })



def editar_cuadrilla(request, cuadrilla_id):
    cuadrilla = get_object_or_404(Cuadrilla, id=cuadrilla_id)
    errores = []
    mensaje_exito = None

    # Obtener el proyecto asociado, si existe
    proyecto_cuadrilla = ProyectoCuadrilla.objects.filter(cuadrilla=cuadrilla).first()
    proyecto = proyecto_cuadrilla.proyecto if proyecto_cuadrilla else None

    # Excluir cargos "Jefe" y "Capataz"
    cargos_excluidos = ["Jefe", "Capataz"]
    trabajadores_asignados = Usuario.objects.filter(cuadrilla=cuadrilla).exclude(cargo__nombre_cargo__in=cargos_excluidos)
    trabajadores_no_asignados = Usuario.objects.filter(cuadrilla__isnull=True).exclude(cargo__nombre_cargo__in=cargos_excluidos)

    if request.method == 'POST':
        if 'eliminar_cuadrilla' in request.POST:
            # Verificación para eliminar la cuadrilla
            if trabajadores_asignados.exists():
                errores.append("No se puede eliminar la cuadrilla porque tiene trabajadores asignados.")
            else:
                # Eliminar la relación de cuadrilla del capataz y la cuadrilla
                if cuadrilla.capataz:
                    cuadrilla.capataz.cuadrilla = None
                    cuadrilla.capataz.save()
                cuadrilla.delete()
                mensaje_exito = "Cuadrilla eliminada correctamente."
                return redirect('mostrar_cuadrilla')  # Redirige después de eliminar la cuadrilla
        else:
            # Obtener los trabajadores seleccionados para agregar y quitar
            agregar_ids = request.POST.getlist('agregar_trabajadores')
            quitar_ids = request.POST.getlist('quitar_trabajadores')

            # Agregar trabajadores seleccionados a la cuadrilla
            Usuario.objects.filter(id__in=agregar_ids).update(cuadrilla=cuadrilla)

            # Quitar trabajadores seleccionados de la cuadrilla
            Usuario.objects.filter(id__in=quitar_ids).update(cuadrilla=None)

            mensaje_exito = "Cuadrilla actualizada correctamente."
    
    return render(request, 'Usuarios/EditarCuadrilla.html', {
        'cuadrilla': cuadrilla,
        'proyecto': proyecto,
        'trabajadores_asignados': trabajadores_asignados,
        'trabajadores_no_asignados': trabajadores_no_asignados,
        'mensaje_exito': mensaje_exito,
        'errores': errores,
    })






#############################
##############################
#@login_required
def home(request):
    return render(request, 'Login/home.html')



#@login_required
def jefe(request):
    proyectos_info = []  # Aquí almacenaremos toda la información estructurada
    
    # Obtener todos los proyectos
    proyectos = Proyecto.objects.all()
    
    # Recorrer cada proyecto para calcular el avance y organizar la información
    for proyecto in proyectos:
        tareas_info = []  # Lista para almacenar la información de tareas de este proyecto
        tareas = proyecto.tarea_set.all()
        
        # Calcular el avance del proyecto en base a las subtareas completadas
        total_subtareas = 0
        subtareas_completadas = 0
        
        for tarea in tareas:
            subtareas = tarea.subtarea_set.all()
            total_subtareas += subtareas.count()  # Sumar todas las subtareas de cada tarea
            subtareas_completadas += subtareas.filter(estado__nombre_estado="FINALIZADA").count()  # Contar las subtareas completadas
        
            # Recoger la información de cada tarea y sus subtareas para el contexto
            subtareas_info = []
            for subtarea in subtareas:
                # Verificar si 'estado' no es None antes de acceder a 'nombre_estado'
                estado_nombre = subtarea.estado.nombre_estado if subtarea.estado else 'Estado no definido'

                # Calcular días de atraso en el inicio
                if subtarea.fecha_inicio_real:
                    dias_atraso_inicio = (subtarea.fecha_inicio_real - subtarea.fecha_inicio_planificada).days if subtarea.fecha_inicio_planificada else ''
                elif subtarea.fecha_inicio_planificada and subtarea.fecha_inicio_planificada < date.today():
                    dias_atraso_inicio = (date.today() - subtarea.fecha_inicio_planificada).days
                else:
                    dias_atraso_inicio = ''

                # Calcular días de atraso en el término
                dias_atraso_termino = (subtarea.fecha_termino_real - subtarea.fecha_termino_planificada).days if subtarea.fecha_termino_real and subtarea.fecha_termino_planificada else ''

                subtareas_info.append({
                    'nombre': subtarea.nombre_subtarea,
                    'estado': estado_nombre,  # Usar la variable 'estado_nombre' en lugar de acceder directamente
                    'fecha_inicio_planificada': subtarea.fecha_inicio_planificada or '',
                    'fecha_termino_planificada': subtarea.fecha_termino_planificada or '',
                    'fecha_inicio_real': subtarea.fecha_inicio_real or '',
                    'fecha_termino_real': subtarea.fecha_termino_real or '',
                    'dias_atraso_inicio': dias_atraso_inicio,
                    'dias_atraso_termino': dias_atraso_termino,
                    'porcentaje_avance': 100 if subtarea.fecha_inicio_real and subtarea.fecha_termino_real else 0,
                })

            tareas_info.append({
                'nombre': tarea.nombre_tarea,
                'fecha_inicio_planificada': tarea.fecha_inicio_planificada or '',
                'fecha_termino_planificada': tarea.fecha_termino_planificada or '',
                'dias_atraso_inicio': '',  # No calcular días de atraso si no están definidos en el modelo
                'dias_atraso_termino': '',
                'subtareas': subtareas_info,
            })

        # Calcular el porcentaje de avance del proyecto basado en las subtareas completadas
        porcentaje_avance_proyecto = round((subtareas_completadas / total_subtareas) * 100, 2) if total_subtareas > 0 else 0

        # Añadir el proyecto a la lista de proyectos
        proyectos_info.append({
            'nombre': proyecto.nombre_proyecto,
            'fecha_inicio': proyecto.fecha_inicio or '',
            'fecha_termino': proyecto.fecha_termino or '',
            'ubicacion': proyecto.ubicacion or '',
            'porcentaje_avance': porcentaje_avance_proyecto,
            'tareas': tareas_info,
        })
    
    context = {
        'proyectos_info': proyectos_info,
    }
    return render(request, 'Login/pagina_jefe.html', context)






def capataz(request, capataz_id):
    # Validar que el usuario en sesión coincide con el capataz_id
    usuario_id = request.session.get('usuario_id')
    if usuario_id != capataz_id:
        # Redirigir al login si no coincide
        errores = ["No tienes permiso para acceder a esta página."]
        return render(request, 'Login/login.html', {'errores': errores})

    # Obtener al capataz por su ID y cargo
    capataz = get_object_or_404(Usuario, id=capataz_id, cargo__nombre_cargo="CAPATAZ")

    # Obtener las cuadrillas que dirige este capataz
    cuadrillas = Cuadrilla.objects.filter(capataz=capataz)

    # Filtrar los proyectos asociados a esas cuadrillas
    proyectos_info = []
    proyectos = Proyecto.objects.filter(proyectocuadrilla__cuadrilla__in=cuadrillas).distinct()

    for proyecto in proyectos:
        tareas_info = []
        # Filtrar tareas únicamente asociadas a proyectos y cuadrillas del capataz
        tareas = Tarea.objects.filter(proyecto=proyecto)

        total_subtareas = 0
        subtareas_completadas = 0

        for tarea in tareas:
            # Filtrar subtareas de esta tarea únicamente asociadas a las cuadrillas del capataz
            subtareas = Subtarea.objects.filter(tarea=tarea, cuadrilla__in=cuadrillas)
            total_subtareas += subtareas.count()
            subtareas_completadas += subtareas.filter(estado__nombre_estado="FINALIZADA").count()

            # Recoger información de cada subtarea
            subtareas_info = []
            for subtarea in subtareas:
                dias_atraso_inicio = ''
                if subtarea.fecha_inicio_real:
                    dias_atraso_inicio = (
                        (subtarea.fecha_inicio_real - subtarea.fecha_inicio_planificada).days
                        if subtarea.fecha_inicio_planificada else ''
                    )
                elif subtarea.fecha_inicio_planificada and subtarea.fecha_inicio_planificada < date.today():
                    dias_atraso_inicio = (date.today() - subtarea.fecha_inicio_planificada).days

                dias_atraso_termino = (
                    (subtarea.fecha_termino_real - subtarea.fecha_termino_planificada).days
                    if subtarea.fecha_termino_real and subtarea.fecha_termino_planificada else ''
                )

                subtareas_info.append({
                    'id': subtarea.id,
                    'nombre': subtarea.nombre_subtarea,
                    'estado': subtarea.estado.nombre_estado,
                    'fecha_inicio_planificada': subtarea.fecha_inicio_planificada or '',
                    'fecha_termino_planificada': subtarea.fecha_termino_planificada or '',
                    'fecha_inicio_real': subtarea.fecha_inicio_real or '',
                    'fecha_termino_real': subtarea.fecha_termino_real or '',
                    'dias_atraso_inicio': dias_atraso_inicio,
                    'dias_atraso_termino': dias_atraso_termino,
                    'porcentaje_avance': 100 if subtarea.fecha_inicio_real and subtarea.fecha_termino_real else 0,
                    'capataz_id': capataz_id,
                })

            tareas_info.append({
                'nombre': tarea.nombre_tarea,
                'fecha_inicio_planificada': tarea.fecha_inicio_planificada or '',
                'fecha_termino_planificada': tarea.fecha_termino_planificada or '',
                'dias_atraso_inicio': '',
                'dias_atraso_termino': '',
                'subtareas': subtareas_info,
            })

        porcentaje_avance_proyecto = (
            round((subtareas_completadas / total_subtareas) * 100, 2)
            if total_subtareas > 0 else 0
        )

        proyectos_info.append({
            'nombre': proyecto.nombre_proyecto,
            'fecha_inicio': proyecto.fecha_inicio or '',
            'fecha_termino': proyecto.fecha_termino or '',
            'ubicacion': proyecto.ubicacion or '',
            'porcentaje_avance': porcentaje_avance_proyecto,
            'tareas': tareas_info,
        })

    context = {
        'proyectos_info': proyectos_info,
        'capataz_id': capataz_id,  # Añadir capataz_id al contexto
    }
    return render(request, 'Login/pagina_capataz.html', context)













def menu_jefe(request):
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return redirect('login')  # Redirige al login si no hay sesión activa

    usuario = Usuario.objects.get(id=usuario_id)  # Obtén el usuario actual
    if usuario.cargo.nombre != 'Jefe':
        return redirect('login')  # Si no es jefe, redirige al login

    return render(request, 'MenuJefe.html') 

from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Usuario




def login_view(request):
    if request.method == 'POST':
        correo = request.POST.get('correo_electronico')
        contrasena = request.POST.get('contrasena')

        # Verifica si el usuario existe y la contraseña es correcta
        try:
            usuario = Usuario.objects.get(correo_electronico=correo)
            if usuario.contrasena == contrasena:  # Comparación directa, sin hash
                # Almacena información del usuario en la sesión
                request.session['usuario_id'] = usuario.id
                request.session['nombre_usuario'] = usuario.nombre_completo

                # Redirige según el cargo del usuario
                if usuario.cargo.nombre_cargo == 'JEFE':
                    return redirect('menu_jefe')
                elif usuario.cargo.nombre_cargo == 'CAPATAZ':
                    # Redirige a la página del capataz con su ID
                    return redirect(reverse('pagina_capataz', args=[usuario.id]))
                else:
                    messages.error(request, "No tienes permisos suficientes para acceder.")
            else:
                messages.error(request, "Contraseña incorrecta.")
        except Usuario.DoesNotExist:
            messages.error(request, "Correo electrónico no registrado.")

    return render(request, 'Login/login.html')




def verificar_sesion(request):
    usuario_id = request.session.get('usuario_id')
    if usuario_id:
        usuario = Usuario.objects.get(id=usuario_id)
        return usuario
    return None

def vista_protegida(request):
    usuario = verificar_sesion(request)
    if usuario and usuario.cargo.nombre_cargo == 'JEFE':
        # Procede con la lógica de la vista
        return render(request, 'pagina_protegida.html', {'usuario': usuario})
    else:
        return redirect('login')



def registro(request):
    if request.method == 'POST':
        # Obtén los datos del formulario de registro
        nombre = request.POST.get('nombre')
        primer_apellido = request.POST.get('primer_apellido')
        segundo_apellido = request.POST.get('segundo_apellido')
        correo = request.POST.get('correo_electronico')
        contrasena = request.POST.get('contrasena')
        
        # Crea el nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            primer_apellido=primer_apellido,
            segundo_apellido=segundo_apellido,
            correo_electronico=correo,
        )
        nuevo_usuario.set_password(contrasena)  # Guarda la contraseña hasheada
        nuevo_usuario.save()
        
        messages.success(request, "Usuario registrado exitosamente")
        return redirect('login')
    
    return render(request, 'Login/registro.html')

def cerrar_sesion(request):
    logout(request)  # Cierra la sesión del usuario
    return redirect('login')  # Redirige a la página de inicio de sesión





#################
#################
#### TAREAS
def crear_tarea(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    errores = []
    mensaje_exito = None

    if request.method == 'POST':
        nombre_tarea = request.POST.get('nombre_tarea')
        descripcion = request.POST.get('descripcion')
        fecha_inicio_planificada = request.POST.get('fecha_inicio_planificada')
        fecha_termino_planificada = request.POST.get('fecha_termino_planificada')

        if nombre_tarea and descripcion and fecha_inicio_planificada and fecha_termino_planificada:
            # Obtener el estado PLANIFICADA directamente por su ID
            estado = get_object_or_404(EstadoTarea, id=1)

            fecha_inicio_planificada = datetime.strptime(fecha_inicio_planificada, '%Y-%m-%d').date()
            fecha_termino_planificada = datetime.strptime(fecha_termino_planificada, '%Y-%m-%d').date()

            # Validar fechas dentro del rango del proyecto
            if fecha_inicio_planificada < proyecto.fecha_inicio:
                errores.append("La fecha de inicio planificada debe ser igual o posterior a la fecha de inicio del proyecto.")
            if fecha_termino_planificada > proyecto.fecha_termino:
                errores.append("La fecha de término planificada debe ser igual o anterior a la fecha de término del proyecto.")

            if not errores:
                # Crear la tarea con estado PLANIFICADA
                Tarea.objects.create(
                    nombre_tarea=nombre_tarea,
                    descripcion=descripcion,
                    fecha_inicio_planificada=fecha_inicio_planificada,
                    fecha_termino_planificada=fecha_termino_planificada,
                    proyecto=proyecto,
                    estado=estado
                )
                mensaje_exito = "La tarea se ha creado exitosamente."

    # Convertir las fechas del proyecto al formato compatible con el input type="date"
    proyecto_fecha_inicio = proyecto.fecha_inicio.strftime('%Y-%m-%d') if proyecto.fecha_inicio else ''
    proyecto_fecha_termino = proyecto.fecha_termino.strftime('%Y-%m-%d') if proyecto.fecha_termino else ''

    return render(request, 'Tareas/CrearTareas.html', {
        'proyecto': proyecto,
        'proyecto_fecha_inicio': proyecto_fecha_inicio,
        'proyecto_fecha_termino': proyecto_fecha_termino,
        'mensaje_exito': mensaje_exito,
        'errores': errores,
        'nombre_tarea': nombre_tarea if 'nombre_tarea' in locals() else '',
        'descripcion': descripcion if 'descripcion' in locals() else '',
        'fecha_inicio_planificada': fecha_inicio_planificada if 'fecha_inicio_planificada' in locals() else '',
        'fecha_termino_planificada': fecha_termino_planificada if 'fecha_termino_planificada' in locals() else '',
    })





def listar_tareas(request):
    proyecto_id = request.GET.get('proyecto')  # Obtener el ID del proyecto seleccionado de la URL
    proyectos = Proyecto.objects.all()  # Obtener todos los proyectos para el filtro
    
    if proyecto_id:
        tareas = Tarea.objects.filter(proyecto_id=proyecto_id)  # Filtrar tareas por proyecto seleccionado
    else:
        tareas = Tarea.objects.all()  # Mostrar todas las tareas si no hay filtro aplicado

    return render(request, 'Tareas/ListarTareas.html', {
        'tareas': tareas,
        'proyectos': proyectos,
        'proyecto_id': proyecto_id  # Pasar el ID del proyecto seleccionado para mantener el estado en el formulario
    })




def detalle_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    subtareas = Subtarea.objects.filter(tarea=tarea).select_related('cuadrilla', 'cuadrilla__capataz')
    comentarios = tarea.comentarios.all()

    # Verifica si el usuario está autenticado
    nombre_usuario = request.session.get('nombre_usuario')

    # Inicializar mensajes
    errores = []
    mensaje_exito = None

    if request.method == 'POST':
        # Manejar acción de editar tarea
        if 'editar_tarea' in request.POST:
            if subtareas.exists():
                errores.append("No se puede editar esta tarea porque tiene subtareas asignadas.")
            else:
                return redirect('editar_tarea', tarea_id=tarea.id)

        # Manejar envío de comentarios
        texto_comentario = request.POST.get('texto_comentario')
        responder_a_id = request.POST.get('respuesta_a')  # ID del comentario al que se responderá

        if texto_comentario:
            try:
                usuario_actual = Usuario.objects.get(
                    nombre=nombre_usuario.split(' ')[0],
                    primer_apellido=nombre_usuario.split(' ')[1]
                )

                comentario_respuesta = None
                if responder_a_id:
                    comentario_respuesta = Comentario.objects.get(id=responder_a_id)

                comentario = Comentario(
                    usuario=usuario_actual,
                    texto_comentario=texto_comentario,
                    respuesta_a=comentario_respuesta
                )
                comentario.save()

                tarea.comentarios.add(comentario)
                tarea.save()
                mensaje_exito = "Comentario agregado exitosamente."
            except Usuario.DoesNotExist:
                errores.append("No se pudo identificar al usuario actual.")

    context = {
        'tarea': tarea,
        'subtareas': subtareas,
        'comentarios': comentarios,
        'nombre_usuario': nombre_usuario,
        'errores': errores,
        'mensaje_exito': mensaje_exito,
    }
    return render(request, 'Tareas/DetallesTareas.html', context)









def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    proyectos = Proyecto.objects.all()
    cuadrillas = Cuadrilla.objects.all()
    estados = EstadoTarea.objects.all()  # Obtener todos los estados

    if request.method == 'POST':
        tarea.nombre_tarea = request.POST.get('nombre_tarea')
        tarea.descripcion = request.POST.get('descripcion')
        tarea.fecha_inicio_planificada = request.POST.get('fecha_inicio_planificada')
        tarea.fecha_termino_planificada = request.POST.get('fecha_termino_planificada')
        proyecto_id = request.POST.get('proyecto')
        cuadrilla_id = request.POST.get('cuadrilla')
        estado_id = request.POST.get('estado')  # Obtener el estado seleccionado

        if proyecto_id:
            tarea.proyecto = Proyecto.objects.get(id=proyecto_id)
        if cuadrilla_id:
            tarea.cuadrilla = Cuadrilla.objects.get(id=cuadrilla_id)
        if estado_id:
            tarea.estado = EstadoTarea.objects.get(id=estado_id)  # Actualizar el estado de la tarea

        tarea.save()
        return redirect('detalle_tarea', tarea_id=tarea.id)

    return render(request, 'Tareas/EditarTareas.html', {
        'tarea': tarea,
        'proyectos': proyectos,
        'cuadrillas': cuadrillas,
        'estados': estados  # Pasar la lista de estados a la plantilla
    })



##############
#### SUBTAREAS
def crear_subtarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    errores = []
    mensaje_exito = None

    if request.method == 'POST':
        nombre_subtarea = request.POST.get('nombre_subtarea')
        descripcion = request.POST.get('descripcion')
        fecha_inicio_planificada = request.POST.get('fecha_inicio_planificada')
        fecha_termino_planificada = request.POST.get('fecha_termino_planificada')
        cuadrilla_id = request.POST.get('cuadrilla')

        # Verificar que todos los campos requeridos están presentes
        if nombre_subtarea and descripcion and fecha_inicio_planificada and fecha_termino_planificada and cuadrilla_id:
            cuadrilla = get_object_or_404(Cuadrilla, id=cuadrilla_id)

            # Convertir las fechas ingresadas a objetos de fecha
            fecha_inicio_planificada = datetime.strptime(fecha_inicio_planificada, '%Y-%m-%d').date()
            fecha_termino_planificada = datetime.strptime(fecha_termino_planificada, '%Y-%m-%d').date()

            # Validar las fechas en relación a la tarea padre
            if fecha_inicio_planificada < tarea.fecha_inicio_planificada:
                errores.append("La fecha de inicio de la subtarea debe ser igual o posterior a la fecha de inicio de la tarea.")
            if fecha_termino_planificada > tarea.fecha_termino_planificada:
                errores.append("La fecha de término de la subtarea debe ser igual o anterior a la fecha de término de la tarea.")

            # Obtener el estado "PLANIFICADA"
            try:
                estado_planificada = EstadoTarea.objects.get(id=1)  # ID=1 para el estado "PLANIFICADA"
            except EstadoTarea.DoesNotExist:
                errores.append("El estado 'PLANIFICADA' no está configurado en el sistema. Contacte al administrador.")
                estado_planificada = None

            # Crear subtarea si no hay errores
            if not errores and estado_planificada:
                Subtarea.objects.create(
                    nombre_subtarea=nombre_subtarea,
                    descripcion=descripcion,
                    fecha_inicio_planificada=fecha_inicio_planificada,
                    fecha_termino_planificada=fecha_termino_planificada,
                    tarea=tarea,
                    cuadrilla=cuadrilla,
                    estado=estado_planificada  # Asignar el estado "PLANIFICADA"
                )
                mensaje_exito = "La subtarea se ha creado exitosamente."
                return redirect('detalle_tarea', tarea_id=tarea.id)
        else:
            errores.append("Todos los campos son obligatorios.")

    # Preparar datos para renderizar la plantilla
    cuadrillas = Cuadrilla.objects.select_related('capataz').all()

    return render(request, 'Tareas/CrearSubtareas.html', {
        'tarea': tarea,
        'cuadrillas': cuadrillas,
        'errores': errores,
        'mensaje_exito': mensaje_exito,
        'nombre_subtarea': nombre_subtarea if 'nombre_subtarea' in locals() else '',
        'descripcion': descripcion if 'descripcion' in locals() else '',
        'fecha_inicio_planificada': fecha_inicio_planificada if 'fecha_inicio_planificada' in locals() else '',
        'fecha_termino_planificada': fecha_termino_planificada if 'fecha_termino_planificada' in locals() else '',
    })






def editar_subtarea(request, subtarea_id):
    subtarea = get_object_or_404(Subtarea, id=subtarea_id)
    tareas = Tarea.objects.all()
    errores = []
    mensaje_exito = None

    # Permitir edición solo si el estado es "PLANIFICADA"
    if subtarea.estado.nombre_estado != "PLANIFICADA":
        errores.append("La subtarea solo se puede modificar en estado Planificada.")
        return render(request, 'Tareas/EditarSubtareas.html', {
            'subtarea': subtarea,
            'tareas': tareas,
            'errores': errores,
        })

    if request.method == 'POST':
        subtarea.nombre_subtarea = request.POST.get('nombre_subtarea')
        subtarea.descripcion = request.POST.get('descripcion')
        subtarea.fecha_inicio_planificada = request.POST.get('fecha_inicio_planificada')
        subtarea.fecha_termino_planificada = request.POST.get('fecha_termino_planificada')
        nueva_tarea_id = request.POST.get('tarea')

        if nueva_tarea_id:
            subtarea.tarea_id = nueva_tarea_id

        subtarea.save()
        mensaje_exito = "Subtarea actualizada correctamente."

    return render(request, 'Tareas/EditarSubtareas.html', {
        'subtarea': subtarea,
        'tareas': tareas,
        'mensaje_exito': mensaje_exito,
    })





def detalles_subtarea(request, subtarea_id):
    # Obtener la subtarea específica
    subtarea = get_object_or_404(Subtarea, id=subtarea_id)
    comentarios = subtarea.comentarios.all()

    # Verificar si el usuario está autenticado
    nombre_usuario = request.session.get('nombre_usuario')

    # Inicializar mensajes
    errores = request.session.pop('errores', [])
    mensaje_exito = request.session.pop('mensaje_exito', None)

    if request.method == 'POST':
        # Si el botón "Editar Subtarea" es presionado
        if 'editar_subtarea' in request.POST:
            if subtarea.estado.id == 1:  # Verifica si el estado es "PLANIFICADA" (ID=1)
                return redirect('editar_subtarea', subtarea_id=subtarea.id)
            else:
                # Añade el error y guarda en la sesión para mostrarse en el modal
                errores.append("No se puede editar esta subtarea porque su estado no es 'PLANIFICADA'.")
                request.session['errores'] = errores
                return redirect('detalles_subtarea', subtarea_id=subtarea.id)

        # Manejar el envío de comentarios
        texto_comentario = request.POST.get('texto_comentario')
        responder_a_id = request.POST.get('respuesta_a')

        if texto_comentario:
            usuario_actual = Usuario.objects.get(
                nombre=nombre_usuario.split(' ')[0],
                primer_apellido=nombre_usuario.split(' ')[1]
            )

            comentario_respuesta = None
            if responder_a_id:
                comentario_respuesta = Comentario.objects.get(id=responder_a_id)

            comentario = Comentario(
                usuario=usuario_actual,
                texto_comentario=texto_comentario,
                respuesta_a=comentario_respuesta
            )
            comentario.save()

            subtarea.comentarios.add(comentario)
            subtarea.save()

        # Redirigir después de agregar comentario
        return redirect('detalles_subtarea', subtarea_id=subtarea.id)

    # Construir el contexto para pasar al template
    context = {
        'subtarea': subtarea,
        'proyecto': subtarea.tarea.proyecto,
        'tarea': subtarea.tarea,
        'comentarios': comentarios,
        'nombre_usuario': nombre_usuario,
        'errores': errores,
        'mensaje_exito': mensaje_exito,
    }

    return render(request, 'Tareas/DetallesSubtareas.html', context)











def listar_subtareas(request):
    # Filtrar las subtareas por un proyecto si es necesario
    proyecto_id = request.GET.get('proyecto', None)
    if proyecto_id:
        subtareas = Subtarea.objects.filter(tarea__proyecto_id=proyecto_id)
    else:
        subtareas = Subtarea.objects.all()

    proyectos = Proyecto.objects.all()  # Si deseas mostrar un selector de proyectos

    context = {
        'subtareas': subtareas,
        'proyectos': proyectos,
        'proyecto_id': proyecto_id,  # Para mantener el filtro
    }
    return render(request, 'Tareas/ListarSubtareas.html', context)





def iniciar_subtarea(request, subtarea_id):
    subtarea = get_object_or_404(Subtarea, id=subtarea_id)
    mensaje_exito = None
    errores = []

    try:
        # Usar el ID correspondiente al estado "EN PROCESO"
        estado_en_proceso = EstadoTarea.objects.get(id=2)  # Asegúrate de que 2 sea el ID correcto para "EN PROCESO"

        if not subtarea.fecha_inicio_real:
            # Si no tiene una fecha de inicio real, asignarla
            subtarea.fecha_inicio_real = now().date()  # Asignar la fecha actual
            subtarea.estado = estado_en_proceso  # Cambiar el estado a "EN PROCESO"
            subtarea.save()  # Guardar los cambios
            mensaje_exito = "La subtarea ha sido iniciada correctamente y su estado cambiado a 'EN PROCESO'."
        else:
            errores.append("La subtarea ya tiene una fecha de inicio establecida.")
    except EstadoTarea.DoesNotExist:
        errores.append("El estado 'EN PROCESO' no existe en la base de datos. Contacte al administrador.")

    # Guardar mensajes en la sesión para mostrarlos después de redirigir
    request.session['mensaje_exito'] = mensaje_exito
    request.session['errores'] = errores

    # Obtener capataz_id del parámetro GET
    capataz_id = request.GET.get('capataz_id')
    if not capataz_id:
        errores.append("El ID del capataz no fue proporcionado.")
        request.session['errores'] = errores
        return redirect('listar_subtareas')  # Redirigir a una página segura si falta capataz_id

    # Redirigir a la página de detalle del capataz
    return redirect('detalle_capataz', subtarea_id=subtarea.id, capataz_id=capataz_id)





def terminar_subtarea(request, subtarea_id):
    subtarea = get_object_or_404(Subtarea, id=subtarea_id)
    mensaje_exito = None
    errores = []

    try:
        # Usar el ID correspondiente al estado "FINALIZADA"
        estado_finalizada = EstadoTarea.objects.get(id=3)  # Cambia 3 por el ID real del estado "FINALIZADA"

        # Verificar si la fecha de término real ya está establecida
        if not subtarea.fecha_termino_real:
            subtarea.fecha_termino_real = now().date()  # Asignar la fecha actual
            subtarea.estado = estado_finalizada  # Cambiar el estado a "FINALIZADA"
            subtarea.save()  # Guardar los cambios
            mensaje_exito = "La subtarea ha sido finalizada correctamente y su estado cambiado a 'FINALIZADA'."
        else:
            errores.append("La subtarea ya tiene una fecha de término establecida.")

    except EstadoTarea.DoesNotExist:
        errores.append("El estado 'FINALIZADA' no existe en la base de datos. Contacte al administrador.")

    # Guardar mensajes en la sesión para mostrarlos después de redirigir
    request.session['mensaje_exito'] = mensaje_exito
    request.session['errores'] = errores

    # Obtener capataz_id del parámetro GET
    capataz_id = request.GET.get('capataz_id')
    if not capataz_id:
        errores.append("El ID del capataz no fue proporcionado.")
        request.session['errores'] = errores
        return redirect('listar_subtareas')  # Redirigir a una página segura si falta capataz_id

    # Redirigir a la página de detalle del capataz
    return redirect('detalle_capataz', subtarea_id=subtarea.id, capataz_id=capataz_id)






def detalle_capataz(request, subtarea_id, capataz_id):
    # Obtener subtarea específica junto con la tarea y el proyecto relacionados
    subtarea = get_object_or_404(Subtarea, id=subtarea_id)
    comentarios = subtarea.comentarios.all()

    nombre_usuario = request.session.get('nombre_usuario')

    ultimo_comentario = comentarios.last()

    if request.method == 'POST':
        texto_comentario = request.POST.get('texto_comentario')
        responder_a_id = request.POST.get('respuesta_a')  # ID del comentario al que se responderá

        if texto_comentario:
            # Encuentra al usuario basado en el nombre completo
            usuario_actual = Usuario.objects.get(
                nombre=nombre_usuario.split(' ')[0], 
                primer_apellido=nombre_usuario.split(' ')[1]
            )

            # Si es una respuesta, obtenemos el comentario al que se está respondiendo
            comentario_respuesta = None
            if responder_a_id:
                comentario_respuesta = Comentario.objects.get(id=responder_a_id)

            # Crea el nuevo comentario
            comentario = Comentario(
                usuario=usuario_actual, 
                texto_comentario=texto_comentario,
                respuesta_a=comentario_respuesta  # Asocia la respuesta si existe
            )
            comentario.save()

            subtarea.comentarios.add(comentario)  # Asumiendo que tienes una relación de comentarios en Subtarea
            subtarea.save()

        # Redirige pasando ambos parámetros
        return redirect('detalle_capataz', subtarea_id=subtarea.id, capataz_id=capataz_id)
    
    # Construir contexto para pasar al template
    context = {
        'subtarea': subtarea,
        'proyecto': subtarea.tarea.proyecto,
        'tarea': subtarea.tarea,
        'capataz_id': capataz_id,  # Pasar el id del capataz al contexto
        'comentarios': comentarios,
        'nombre_usuario': nombre_usuario,
        'ultimo_comentario': ultimo_comentario,
    }

    return render(request, 'Login/detalle_capataz.html', context)





def mostrar_pagina_cargos(request):
    """
    Vista que muestra la página de gestión de cargos.
    """
    # Excluir los cargos "Jefe" y "Capataz" de la lista
    cargos = Cargo.objects.exclude(nombre_cargo__in=["JEFE", "CAPATAZ"])
    return render(request, 'Usuarios/CrearCargo.html', {'cargos': cargos})

def crear_cargo(request):
    """
    Vista para crear un nuevo cargo.
    """
    if request.method == 'POST':
        nombre_cargo = request.POST.get('nombre_cargo')
        if nombre_cargo:
            Cargo.objects.create(nombre_cargo=nombre_cargo)
            return redirect('pagina_cargos')
    return redirect('pagina_cargos')

def editar_cargo(request):
    """
    Vista para editar un cargo existente.
    """
    if request.method == 'POST':
        cargo_id = request.POST.get('cargo_id')
        nuevo_nombre_cargo = request.POST.get('nuevo_nombre_cargo')
        try:
            # Asegurarse de que el cargo no sea "Jefe" ni "Capataz"
            cargo = Cargo.objects.exclude(nombre_cargo__in=["JEFE", "CAPATAZ"]).get(id=cargo_id)
            cargo.nombre_cargo = nuevo_nombre_cargo
            cargo.save()
        except Cargo.DoesNotExist:
            pass  # Si no existe o está excluido, simplemente ignorar
    return redirect('pagina_cargos')
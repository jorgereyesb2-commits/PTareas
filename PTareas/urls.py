from django.contrib import admin
from django.urls import path
from AppTareas.views import *
from AppTareas import views as login_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_views.login_view, name='login'),
    path('usuarios/crear/', crear_usuario, name='crear_usuario'),
    path('usuarios/mostrar/', mostrar_usuario, name='mostrar_usuario'),
    path('usuarios/editar/<int:usuario_id>/', editar_usuario, name='editar_usuario'),
    path('usuarios/cambiar_estado/<int:usuario_id>/', cambiar_estado_usuario, name='cambiar_estado_usuario'),
    path('cuadrillas/crear/', crear_cuadrilla, name='crear_cuadrilla'),
    path('cuadrillas/editar/<int:cuadrilla_id>/', editar_cuadrilla, name='editar_cuadrilla'),
    path('proyectos/crear/', crear_proyecto, name='crear_proyecto'),
    path('cuadrillas/gestionar/', gestionar_cuadrilla, name='gestionar_cuadrilla'),
    
    path('jefe/', login_views.jefe, name='menu_jefe'),
    
    ### LOGIN
    path('accounts/login/', login_views.login_view, name='login'),  # Agrega esta línea
    path('login/', login_views.login_view, name='login'),
    #path('', login_views.jefe, name='menu_jefe'),     # era  'jefe/' en lugar del espacio vacio
    path('logout/', login_views.cerrar_sesion, name='cerrar_sesion'),

    ### PARA LA PAGINA DEL CAPATAZ
    path('capataz/<int:capataz_id>', login_views.capataz, name='pagina_capataz'),

    ### TAREAS
    path('tareas/crear/<int:proyecto_id>', crear_tarea, name='crear_tarea'),
    path('tareas/listar/', listar_tareas, name='listar_tareas'),
    path('detalle/<int:tarea_id>/', detalle_tarea, name='detalle_tarea'), 
    path('editar/<int:tarea_id>/', editar_tarea, name='editar_tarea'),


    ### SUBTAREAS
    path('tarea/<int:tarea_id>/crear_subtarea/', crear_subtarea, name='crear_subtarea'),
    path('subtarea/editar/<int:subtarea_id>/', editar_subtarea, name='editar_subtarea'),
    path('subtarea/detalles/<int:subtarea_id>/', detalles_subtarea, name='detalles_subtarea'),
    path('subtarea/listar/', listar_subtareas, name='listar_subtareas'),


    path('capataz/detalle/<int:subtarea_id>/<int:capataz_id>/', detalle_capataz, name='detalle_capataz'), #PUSE ID CAPATAZ


    ### RUTAS PARA INICIAR Y TERMINAR SUBTAREA
    path('subtarea/iniciar/<int:subtarea_id>/', iniciar_subtarea, name='iniciar_subtarea'),
    path('subtarea/terminar/<int:subtarea_id>/', terminar_subtarea, name='terminar_subtarea'),

    # PAGINA QUE SELECCIONA EL PROYECTO ANTES DE AGREGAR UNA TAREA
    path('tareas/seleccionarproyecto', listar_proyectos, name='listar_proyectos'),

    ### NUEVAS RUTAS PARA CARGOS
    path('usuarios/cargos/', mostrar_pagina_cargos, name='pagina_cargos'),  # Muestra la página para crear/editar cargos
    path('usuarios/cargos/crear/', crear_cargo, name='crear_cargo'),  # Ruta para crear cargos
    path('usuarios/cargos/editar/', editar_cargo, name='editar_cargo'),  # Ruta para editar cargos

]


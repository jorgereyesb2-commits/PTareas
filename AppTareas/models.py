from django.db import models

# Modelo para representar los posibles estados (ej. ACTIVO, INACTIVO)
class Estado(models.Model):
    nombre_estado = models.CharField(max_length=20, unique=True)  # Nombre único para cada estado

    def __str__(self):
        return self.nombre_estado


# Modelo para representar los diferentes cargos (ej. Capataz, Jefe)
class Cargo(models.Model):
    nombre_cargo = models.CharField(max_length=30)  # Nombre del cargo (p.ej., "Jefe de Obra")

    def __str__(self):
        return self.nombre_cargo


# Modelo para representar una cuadrilla de trabajadores
class Cuadrilla(models.Model):
    codigo_cuadrilla = models.CharField(max_length=20, unique=True, blank=True)  # Código único de la cuadrilla
    capataz = models.ForeignKey('Usuario', on_delete=models.PROTECT, null=True, blank=True, related_name='cuadrillas_dirigidas')

    def save(self, *args, **kwargs):
        if not self.codigo_cuadrilla:
            last_id = Cuadrilla.objects.all().count() + 1
            self.codigo_cuadrilla = f"C-{last_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo_cuadrilla


# Modelo para representar los usuarios y trabajadores en el sistema
class Usuario(models.Model):
    rut = models.CharField(max_length=15, unique=True)  # RUT único de la persona
    nombre = models.CharField(max_length=20)  # Nombre de la persona
    primer_apellido = models.CharField(max_length=20)  # Primer apellido
    segundo_apellido = models.CharField(max_length=20)  # Segundo apellido
    cargo = models.ForeignKey(Cargo, on_delete=models.PROTECT)  # Cargo de la persona (ej. Jefe, Capataz, Trabajador)
    correo_electronico = models.EmailField(max_length=100, blank=True, null=True)  # Solo para usuarios del sistema
    contrasena = models.CharField(max_length=255, blank=True, null=True)  # Solo para usuarios del sistema
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)  # Estado actual (activo/inactivo)
    cuadrilla = models.ForeignKey(Cuadrilla, null=True, blank=True, on_delete=models.SET_NULL)  # Solo para trabajadores en cuadrillas

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.primer_apellido} {self.segundo_apellido}"

    def __str__(self):
        return f"{self.nombre_completo} ({self.rut})"


# Modelo para representar un proyecto
class Proyecto(models.Model):
    nombre_proyecto = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField()

    def __str__(self):
        return self.nombre_proyecto


# Tabla intermedia para la relación muchos a muchos entre Proyectos y Cuadrillas
class ProyectoCuadrilla(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    cuadrilla = models.ForeignKey(Cuadrilla, on_delete=models.CASCADE)


class EstadoTarea(models.Model):
    nombre_estado = models.CharField(max_length=20, unique=True)  # Ejemplo: "Sin empezar", "Comenzado", "Terminado"

    def __str__(self):
        return self.nombre_estado


class Tarea(models.Model):
    nombre_tarea = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio_planificada = models.DateField()
    fecha_termino_planificada = models.DateField()
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    observacion_jefe = models.TextField(null=True, blank=True)
    estado = models.ForeignKey(EstadoTarea, on_delete=models.SET_NULL, null=True)  # Estado de la tarea
    comentarios = models.ManyToManyField('Comentario', related_name='tareas', blank=True)  # Relación con los comentarios

    def __str__(self):
        return self.nombre_tarea


# Modelo para representar una subtarea específica dentro de una tarea
class Subtarea(models.Model):
    nombre_subtarea = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio_planificada = models.DateField()
    fecha_termino_planificada = models.DateField()
    fecha_inicio_real = models.DateField(null=True, blank=True)
    fecha_termino_real = models.DateField(null=True, blank=True)
    cuadrilla = models.ForeignKey(Cuadrilla, null=True, blank=True, on_delete=models.CASCADE)
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoTarea, on_delete=models.SET_NULL, null=True)  # Estado de la subtarea
    comentarios = models.ManyToManyField('Comentario', related_name='subtareas', blank=True)

    def __str__(self):
        return self.nombre_subtarea


# Modelo para representar un comentario en una tarea o subtarea
class Comentario(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que hace el comentario
    texto_comentario = models.TextField()  # Texto del comentario
    respuesta_a = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)  # Respuesta a otro comentario
    fecha_comentario = models.DateTimeField(auto_now_add=True)  # Fecha y hora del comentario

    def __str__(self):
        return f"Comentario de {self.usuario} en {self.fecha_comentario}"




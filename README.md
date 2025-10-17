Luego de hacer las migraciones necesarias con:

python manage.py makemigrations
python manage.py migrate


Insertamos los siguientes datos a las tablas correspondientes para que el programa tenga funcionamiento:


-- Insertar Estados
INSERT INTO appTareas_estado (NOMBRE_ESTADO) VALUES ('ACTIVO'), ('INACTIVO');


-- Insertar Cargos
INSERT INTO appTareas_cargo (NOMBRE_CARGO) VALUES ('JEFE'), ('CAPATAZ'), ('ALBAÑIL'), ('CARPINTERO');


-- Insertar Proyecto
INSERT INTO appTareas_proyecto (nombre_proyecto, ubicacion, fecha_inicio, fecha_termino)
VALUES 
('Construcción de Edificio A', 'Avenida Principal 123, Rancagua', '2024-01-01', '2024-12-31'),
('Construcción de Edificio B', 'Avenida Dos 1321, Requinoa', '2024-10-01', '2025-12-31');


-- Crear Cuadrillas
INSERT INTO appTareas_cuadrilla (codigo_cuadrilla, capataz_id)
VALUES 
('C-0001', NULL),
('C-0002', NULL),
('C-0003', NULL),
('C-0004', NULL);


-- Insertar Usuarios en appTareas_usuario
INSERT INTO appTareas_usuario (rut, nombre, primer_apellido, segundo_apellido, cargo_id, correo_electronico, contrasena, estado_id, cuadrilla_id)
VALUES 
('11111111-1', 'CARLOS', 'PÉREZ', 'GONZÁLEZ', 1, 'carlos.perez@jira.cl', '111', 1, NULL);  


INSERT INTO appTareas_usuario (rut, nombre, primer_apellido, segundo_apellido, cargo_id, correo_electronico, contrasena, estado_id, cuadrilla_id)
VALUES 
('22222222-2', 'ANA', 'MARTINEZ', 'LOPEZ', 2, 'ana.martinez@jira.cl', '111', 1, 1),  
('33333333-3', 'LUIS', 'ROJAS', 'SANCHEZ', 2, 'luis.rojas@jira.cl', '111', 1, 2),  
('44555444-4', 'PEDRO', 'GÓMEZ', 'HERNANDEZ', 2, 'pedro.gomez@jira.cl', '111', 1, 3),
('44666444-4', 'JUAN', 'PEREZ', 'OLEA', 2, 'juan.perez@jira.cl', '111', 1, 4),
('44777444-4', 'LAURA', 'ARMIJO', 'MACHUCA', 2, 'laura.armijo@jira.cl', '111', 1, NULL);   


INSERT INTO appTareas_usuario (rut, nombre, primer_apellido, segundo_apellido, cargo_id, correo_electronico, contrasena, estado_id, cuadrilla_id)
VALUES 
('55555555-5', 'JUAN', 'DIAZ', 'JIMENEZ', 3, NULL, NULL, 1, 1),      
('66666666-6', 'JOSE', 'VEGA', 'LOPEZ', 3, NULL, NULL, 1, 1),        
('77777777-7', 'RAUL', 'RAMIREZ', 'TORRES', 3, NULL, NULL, 1, 2),    
('88888888-8', 'ENRIQUE', 'SUAREZ', 'CASTILLO', 3, NULL, NULL, 1, 2),
('99999999-9', 'FERNANDO', 'HIDALGO', 'FLORES', 4, NULL, NULL, 1, 3),  
('12345678-0', 'MARIO', 'MORALES', 'GUTIERREZ', 4, NULL, NULL, 1, 3),   
('23456789-1', 'RUBÉN', 'NAVARRO', 'PEREZ', 4, NULL, NULL, 1, 4),       
('34567890-2', 'SERGIO', 'ORTIZ', 'MARTINEZ', 4, NULL, NULL, 1, 4),     
('43453901-3', 'DAVID', 'SILVA', 'REYES', 4, NULL, NULL, 1, NULL),
('56744901-3', 'ROSA', 'ESPINOZA', 'REYES', 4, NULL, NULL, 1, NULL),
('15678383-3', 'OSCAR', 'ROJAS', 'SALAS', 4, NULL, NULL, 1, NULL),
('17898901-3', 'JUAN', 'AGUERO', 'DIAZ', 4, NULL, NULL, 2, NULL);


-- Asignar Cuadrillas al Proyecto en ProyectoCuadrilla
INSERT INTO appTareas_proyectocuadrilla (proyecto_id, cuadrilla_id)
VALUES
(1, 1),  -- Asocia la cuadrilla 1 al proyecto 1
(1, 2),  -- Asocia la cuadrilla 2 al proyecto 1
(2, 3),
(2, 4);


-- Asignar a Ana Martínez como capataz de la cuadrilla C-0001
UPDATE appTareas_cuadrilla
SET capataz_id = (SELECT id FROM appTareas_usuario WHERE rut = '22222222-2')
WHERE codigo_cuadrilla = 'C-0001';


-- Asignar a Luis Rojas como capataz de la cuadrilla C-0002
UPDATE appTareas_cuadrilla
SET capataz_id = (SELECT id FROM appTareas_usuario WHERE rut = '33333333-3')
WHERE codigo_cuadrilla = 'C-0002';


-- Asignar a Pedro Gomez como capataz de la cuadrilla C-0003
UPDATE appTareas_cuadrilla
SET capataz_id = (SELECT id FROM appTareas_usuario WHERE rut = '44555444-4')
WHERE codigo_cuadrilla = 'C-0003';


-- Asignar a Juan Perez como capataz de la cuadrilla C-0004
UPDATE appTareas_cuadrilla
SET capataz_id = (SELECT id FROM appTareas_usuario WHERE rut = '44666444-4')
WHERE codigo_cuadrilla = 'C-0004';


-- Insert para estado tareas
INSERT INTO apptareas_estadotarea (nombre_estado) VALUES ('PLANIFICADA');
INSERT INTO apptareas_estadotarea (nombre_estado) VALUES ('EN PROCESO');
INSERT INTO apptareas_estadotarea (nombre_estado) VALUES ('FINALIZADA');


-- Insert para tareas asociadas al proyecto 1
-- Insertar Tarea 1 (Finalizada)
INSERT INTO apptareas_tarea (nombre_tarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, proyecto_id, estado_id, observacion_jefe)
VALUES ('Poner puertas y reparar muros en piso 2', 'Poner las puertas de los departamentos del piso 2 y arreglar imperfecciones en los muros', '2024-01-01', '2024-10-31', 1, (SELECT id FROM apptareas_estadotarea WHERE nombre_estado = 'FINALIZADA'), 'Tener cuidado con las puertas de las cocinas');


-- Insertar Tarea 2 (En Proceso)
INSERT INTO apptareas_tarea (nombre_tarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, proyecto_id, estado_id, observacion_jefe)
VALUES ('Instalar artefactos en los baños del piso 2', 'Instalar baños y lavamanos', '2024-11-01', '2024-12-30', 1, (SELECT id FROM apptareas_estadotarea WHERE nombre_estado = 'EN PROCESO'), 'Ojo con los lavamanos');


-- Insertar Tarea 3 (Sin Iniciar)
INSERT INTO apptareas_tarea (nombre_tarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, proyecto_id, estado_id, observacion_jefe)
VALUES ('Pintar departamentos piso 2', 'Pintar el interior de los departamentos del piso 2', '2024-12-01', '2024-12-31', 1, (SELECT id FROM apptareas_estadotarea WHERE nombre_estado = 'PLANIFICADA'), 'Si encuentran imperfecciones en los muros avisar y dejar sin pintar hasta que se arreglen las imperfecciones');


-- insertar subtareas en la tarea 1
INSERT INTO apptareas_subtarea (nombre_subtarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, tarea_id, fecha_inicio_real, fecha_termino_real, cuadrilla_id, estado_id) VALUES
('Puertas depto. 201', 'Instalar todas las puertas del depto 201', '2024-01-01', '2024-01-31', 1, '2024-01-01', '2024-01-31', 1, 3),
('Puertas depto. 202', 'Instalar todas las puertas del depto 202', '2024-02-01', '2024-02-28', 1, '2024-02-01', '2024-02-28', 1, 3),
('Puertas depto. 203', 'Instalar todas las puertas del depto 203', '2024-03-01', '2024-03-30', 1, '2024-03-02', '2024-03-30', 1, 3),
('Puertas depto. 204', 'Instalar todas las puertas del depto 204', '2024-04-01', '2024-04-30', 1, '2024-04-03', '2024-05-05', 1, 3),
('Puertas depto. 205', 'Instalar todas las puertas del depto 205', '2024-05-01', '2024-05-30', 1, '2024-05-01', '2024-05-30', 1, 3);


-- insertar subtareas en la tarea 2
INSERT INTO apptareas_subtarea (nombre_subtarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, tarea_id, fecha_inicio_real, fecha_termino_real, cuadrilla_id, estado_id) VALUES
('Artefactos depto. 201', 'Instalar todas los artefactos del depto 201', '2024-11-01', '2024-11-10', 2, '2024-11-01', '2024-11-10', 2, 3),
('Artefactos depto. 202', 'Instalar todas los artefactos del depto 202', '2024-11-10', '2024-11-30', 2, NULL, NULL, 2, 1);


-- insertar subtareas en la tarea 3
INSERT INTO apptareas_subtarea (nombre_subtarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, tarea_id, fecha_inicio_real, fecha_termino_real, cuadrilla_id, estado_id) VALUES
('Pintar depto. 201', 'Pintar depto 201', '2024-12-01', '2024-12-14', 3, NULL, NULL, 1, 1),
('Pintar depto. 202', 'Pintar depto 202', '2024-12-16', '2024-12-30', 3, NULL, NULL, 1, 1);


-- INSERTAR TAREAS PROYECTO 2
-- Insertar Tarea 4 (Finalizada)
INSERT INTO apptareas_tarea (nombre_tarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, proyecto_id, estado_id, observacion_jefe)
VALUES ('Poner ventanas en piso 1', 'Poner las ventanas de los departamentos del piso 1', '2024-10-01', '2024-10-30', 2, (SELECT id FROM apptareas_estadotarea WHERE nombre_estado = 'FINALIZADA'), 'Tener cuidado con las ventanas');


-- Insertar Tarea 5 (En Proceso)
INSERT INTO apptareas_tarea (nombre_tarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, proyecto_id, estado_id, observacion_jefe)
VALUES ('Pintar departamentos piso 1', 'Usar los colores nuevos', '2024-11-01', '2024-12-30', 2, (SELECT id FROM apptareas_estadotarea WHERE nombre_estado = 'EN PROCESO'), 'Ojo con los guardapolvos, no manchar');


-- insertar subtareas en la tarea 4
INSERT INTO apptareas_subtarea (nombre_subtarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, tarea_id, fecha_inicio_real, fecha_termino_real, cuadrilla_id, estado_id) VALUES
('Instalar ventanas en depto. 101', 'Instalar todas las ventanas del depto. 101', '2024-10-01', '2024-10-15', 4, '2024-10-02', '2024-10-30', 3, 3),
('Instalar ventanas en depto. 102', 'Instalar todas las ventanas del depto. 102', '2024-10-15', '2024-10-30', 4, '2024-10-15', '2024-10-30', 3, 3);


-- insertar subtareas en la tarea 5
INSERT INTO apptareas_subtarea (nombre_subtarea, descripcion, fecha_inicio_planificada, fecha_termino_planificada, tarea_id, fecha_inicio_real, fecha_termino_real, cuadrilla_id, estado_id) VALUES
('Pintar depto. 101', 'Pintar todo el depto. 101', '2024-11-01', '2024-11-30', 5, NULL, NULL, 4, 2),
('Pintar depto. 102', 'Pintar todo el depto. 102', '2024-12-01', '2024-12-30', 5, NULL, NULL, 4, 1);



-- ESTO ES SOLO PARA REINICIAR EL CONTADOR DE AUTOINCREMENT EN LA TABLA appTareas_usuario
ALTER TABLE appTareas_usuario AUTO_INCREMENT = 1;


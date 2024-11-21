import sqlite3
from datetime import datetime

# Conectar a la base de datos
conn = sqlite3.connect('club.db')
cursor = conn.cursor()

# Crear las tablas (si no existen)
def crear_tablas():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS integrantes (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            fecha_nacimiento TEXT NOT NULL,
            telefono TEXT NOT NULL,
            domicilio TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS actividades (
            ID_actividad INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_integrante INTEGER,
            tipo_actividad TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            FOREIGN KEY (ID_integrante) REFERENCES integrantes (ID)
        )
    ''')

# Función para validar entrada de datos
def obtener_input_validado(mensaje, tipo=str, obligatorio=True, formato_fecha=False, no_numeros=False):
    while True:
        valor = input(mensaje).strip()
        
        # Verificar si el campo es obligatorio y está vacío
        if obligatorio and not valor:
            print("Este campo no puede estar vacío. Por favor, ingresa un valor.")
            continue
        
        # Validar si debe evitarse números en el texto
        if no_numeros and any(char.isdigit() for char in valor):
            print("Este campo no puede contener números. Por favor, ingresa un texto válido.")
            continue
        
        # Validación para valores numéricos
        if tipo == int:
            if not valor.isdigit():
                print("Por favor, ingresa un número válido.")
                continue
            return int(valor)
        
        # Validación de formato de fecha
        if formato_fecha:
            try:
                datetime.strptime(valor, '%Y-%m-%d')
                return valor
            except ValueError:
                print("Por favor, ingresa una fecha válida en formato YYYY-MM-DD.")
                continue
        
        # Si pasa todas las validaciones, devolver el valor
        return valor

# Función para agregar un integrante
def agregar_integrante():
    nombre = obtener_input_validado("Nombre: ", no_numeros = True)
    apellido = obtener_input_validado("Apellido: ",no_numeros = True)
    numero_documento = obtener_input_validado("Número de documento: ", tipo=int)
    fecha_nacimiento = obtener_input_validado("Fecha de nacimiento (YYYY-MM-DD): ", formato_fecha=True)
    telefono = obtener_input_validado("Teléfono: ", tipo=int)
    domicilio = obtener_input_validado("Domicilio: ")

    cursor.execute('''
        INSERT INTO integrantes (nombre, apellido, numero_documento, fecha_nacimiento, telefono, domicilio)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, apellido, numero_documento, fecha_nacimiento, telefono, domicilio))
    conn.commit()
    print("Integrante agregado correctamente.")

# Función para consultar los datos de los integrantes
def consultar_integrantes():
    cursor.execute('SELECT * FROM integrantes')
    integrantes = cursor.fetchall()  # Obtiene todos los resultados de la consulta
    if integrantes:
        for integrante in integrantes:
            print(integrante)
    else:
        print("No hay integrantes registrados.")

# Función para eliminar un integrante
def eliminar_integrante():
    id_integrante = obtener_input_validado("ID del integrante a eliminar: ", tipo=int)
    cursor.execute('DELETE FROM integrantes WHERE ID = ?', (id_integrante,))
    conn.commit()
    print("Integrante eliminado correctamente.")

# Función para ordenar los integrantes por criterio
def ordenar_integrantes():
    print("Ordenar por:")
    print("1. Alfabético por nombre")
    print("2. Numérico por ID")
    print("3. Por edad")
    opcion = obtener_input_validado("Selecciona una opción: ", tipo=int)

    if opcion == 1:
        cursor.execute('SELECT * FROM integrantes ORDER BY nombre')
    elif opcion == 2:
        cursor.execute('SELECT * FROM integrantes ORDER BY ID')
    elif opcion == 3:
        cursor.execute('''
            SELECT * FROM integrantes
            ORDER BY strftime('%Y', fecha_nacimiento) ASC
        ''')
    else:
        print("Opción no válida.")
        return

    integrantes = cursor.fetchall()
    if integrantes:
        for integrante in integrantes:
            print(integrante)
    else:
        print("No hay datos para mostrar.")

# Función para agregar actividad a un integrante
def agregar_actividad():
    id_integrante = obtener_input_validado("ID del integrante: ", tipo=int)

    # Validamos que el ID exista en la base de datos
    cursor.execute("SELECT COUNT(*) FROM integrantes WHERE ID = ?", (id_integrante,))
    if cursor.fetchone()[0] == 0: #Accede al primer elemento del resultado, que contiene el conteo.
        print("El ID del integrante no existe. Por favor, verifica los datos.")
        return

    tipo_actividad = obtener_input_validado("Tipo de actividad: ")
    fecha_inicio = obtener_input_validado("Fecha de inicio (YYYY-MM-DD): ", formato_fecha=True)
    fecha_fin = obtener_input_validado("Fecha de finalización (YYYY-MM-DD): ", formato_fecha=True)

    cursor.execute('''
        INSERT INTO actividades (ID_integrante, tipo_actividad, fecha_inicio, fecha_fin)
        VALUES (?, ?, ?, ?)
    ''', (id_integrante, tipo_actividad, fecha_inicio, fecha_fin))
    conn.commit()
    print("Actividad agregada correctamente.")

# Menú principal
def mostrar_menu():
    while True:
        print("\n--- Menú de Administración de Club ---")
        print("1. Ingresar datos")
        print("2. Consultar datos")
        print("3. Eliminar datos")
        print("4. Ordenar datos")
        print("5. Listar todos los datos")
        print("6. Agregar actividad")
        print("7. salir")

        opcion = obtener_input_validado("Selecciona una opción: ", tipo=int)

        if opcion == 1:
            agregar_integrante()
        elif opcion == 2:
            consultar_integrantes()
        elif opcion == 3:
            eliminar_integrante()
        elif opcion == 4:
            ordenar_integrantes()
        elif opcion == 5:
            consultar_integrantes()
        elif opcion == 6:
            agregar_actividad()
        elif opcion == 7:
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida, intenta de nuevo.")

# Ejecutar el sistema
crear_tablas()
mostrar_menu()

# Cerrar la conexión con la base de datos al salir
conn.close()

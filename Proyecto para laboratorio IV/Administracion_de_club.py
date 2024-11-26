import sqlite3
from datetime import datetime

# Conectar a la base de datos y habilitar claves foraneas
conn = sqlite3.connect('club.db')
cursor = conn.cursor()
cursor.execute('PRAGMA foreign_keys = ON')

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
            FOREIGN KEY (ID_integrante) REFERENCES integrantes (ID) ON DELETE CASCADE
        )
    ''')
    
    # Se crea una tabla para ID disponibles para reutilizar en un futuro
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ids_disponibles (
            ID INTEGER PRIMARY KEY
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
        
       # Validación de formato de fecha (DD-MM-YYYY)
        if formato_fecha:
            try:
                # Convertir de DD-MM-YYYY a YYYY-MM-DD
                fecha_formateada = datetime.strptime(valor, '%d-%m-%Y').strftime('%Y-%m-%d') # Se valida el formato DD-MM-YYYY pero internamente es YYYY-MM-DD
                return fecha_formateada
            except ValueError:
                print("Por favor, ingresa una fecha válida en formato DD-MM-YYYY.")
                continue
        
        # Si pasa todas las validaciones, devolver el valor
        return valor

# Función para agregar un integrante
def agregar_integrante():

    cursor.execute("SELECT ID FROM ids_disponibles ORDER BY ID LIMIT 1")
    id_disponible = cursor.fetchone()

    if id_disponible: # En caso de haber una ID disponible, se la elimina de la tabla de ID disponible
        id_usar = id_disponible[0]
        cursor.execute("DELETE FROM ids_disponibles WHERE ID = ?", (id_usar,))
    else:
        id_usar = None

    nombre = obtener_input_validado("Nombre: ", no_numeros = True)
    apellido = obtener_input_validado("Apellido: ",no_numeros = True)
    numero_documento = obtener_input_validado("Número de documento: ", tipo=int)
    fecha_nacimiento = obtener_input_validado("Fecha de nacimiento (DD-MM-YYYY): ", formato_fecha=True)
    telefono = obtener_input_validado("Teléfono: ", tipo=int)
    domicilio = obtener_input_validado("Domicilio: ")

    if id_usar: # En caso de que haya una ID para reutilizar
        cursor.execute('''
            INSERT INTO integrantes (ID, nombre, apellido, numero_documento, fecha_nacimiento, telefono, domicilio)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (id_usar, nombre, apellido, numero_documento, fecha_nacimiento, telefono, domicilio))
    else:
        cursor.execute('''
            INSERT INTO integrantes (nombre, apellido, numero_documento, fecha_nacimiento, telefono, domicilio)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, apellido, numero_documento, fecha_nacimiento, telefono, domicilio))

    conn.commit()
    print("Integrante agregado correctamente.")

# Función para consultar los datos de los integrantes
def consultar_integrantes():
    cursor.execute('SELECT * FROM integrantes')
    integrantes = cursor.fetchall() # Obtiene todos los resultados de la consulta
    if integrantes:
        for integrante in integrantes:
            # Convertir fecha de nacimiento al formato DD-MM-YYYY antes de mostrarla
            fecha_nacimiento = datetime.strptime(integrante[4], '%Y-%m-%d').strftime('%d-%m-%Y') 
            print(f"ID: {integrante[0]}, Nombre: {integrante[1]}, Apellido: {integrante[2]}, "
                  f"Documento: {integrante[3]}, Fecha de Nacimiento: {fecha_nacimiento}, "
                  f"Teléfono: {integrante[5]}, Domicilio: {integrante[6]}")
 
# Función para eliminar un integrante
def eliminar_integrante():
    id_integrante = obtener_input_validado("ID del integrante a eliminar: ", tipo=int)
    cursor.execute("SELECT * FROM integrantes WHERE ID = ?", (id_integrante,))
    if cursor.fetchone() is None:
        print("El ID no existe. Por favor, verifica los datos.")
        return
        
    # Al eliminar un integrante el ID se lo coloca en una tabla de IDS disponibles
    cursor.execute("INSERT INTO ids_disponibles (ID) VALUES (?)", (id_integrante,))

    # Se elimina el integrante de dicha ID
    cursor.execute("DELETE FROM integrantes WHERE ID = ?", (id_integrante,))
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
    fecha_inicio = obtener_input_validado("Fecha de inicio (DD-MM-YYYY): ", formato_fecha=True)
    fecha_fin = obtener_input_validado("Fecha de finalización (DD-MM-YYYY): ", formato_fecha=True)

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

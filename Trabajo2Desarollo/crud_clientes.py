import csv
import os
import random
import re

ARCHIVO = "clientes.csv"
PREFIJO_TELEFONO = "+56 9 "
DOMINIOS_VALIDOS = {
    "gmail.com", "gmail.cl",
    "hotmail.com", "hotmail.cl",
    "outlook.com", "outlook.cl",
    "yahoo.com", "yahoo.cl",
    "live.com", "icloud.com",
}


# ─────────────────────────────────────────────
# VALIDACIONES
# ─────────────────────────────────────────────

def validar_nombre(nombre):
    """Retorna (True, None) o (False, mensaje_error)."""
    if not nombre or not nombre.strip():
        return False, "EL NOMBRE NO PUEDE ESTAR VACÍO"
    if len(nombre.strip()) < 3:
        return False, "EL NOMBRE DEBE TENER AL MENOS 3 CARACTERES"
    if len(nombre.strip()) > 50:
        return False, "EL NOMBRE NO PUEDE EXCEDER 50 CARACTERES"
    # Solo letras y espacios (incluye acentos)
    if not re.match(r"^[A-Za-záéíóúñÑ\s]+$", nombre.strip()):
        return False, "EL NOMBRE SOLO PUEDE CONTENER LETRAS Y ESPACIOS"
    return True, None


def validar_correo(correo):
    """Retorna (True, None) o (False, mensaje_error)."""
    if not correo or "@" not in correo:
        return False, "CORREO NO VÁLIDO"
    if len(correo.strip()) > 100:
        return False, "EL CORREO NO PUEDE EXCEDER 100 CARACTERES"
    # No puede tener múltiples @
    if correo.count("@") > 1:
        return False, "CORREO NO VÁLIDO"
    usuario, dominio = correo.split("@", 1)
    if not usuario or not dominio:
        return False, "CORREO NO VÁLIDO"
    # No puede tener puntos consecutivos
    if ".." in usuario or ".." in dominio:
        return False, "CORREO NO VÁLIDO"
    # No puede empezar o terminar con punto
    if usuario.startswith(".") or usuario.endswith("."):
        return False, "CORREO NO VÁLIDO"
    if dominio.startswith(".") or dominio.endswith("."):
        return False, "CORREO NO VÁLIDO"
    if not re.match(r"^[A-Za-z0-9._%+-]+$", usuario):
        return False, "CORREO NO VÁLIDO"
    if dominio not in DOMINIOS_VALIDOS:
        return False, f"DOMINIO NO PERMITIDO: {dominio}"
    return True, None


def validar_telefono(telefono):
    """Retorna (True, None) o (False, mensaje_error)."""
    if not telefono.startswith(PREFIJO_TELEFONO):
        return False, "EL TELÉFONO DEBE EMPEZAR CON +56 9"
    parte = telefono[len(PREFIJO_TELEFONO):]
    digitos = re.sub(r"\D", "", parte)
    if len(digitos) != 8:
        return False, "EL TELÉFONO DEBE TENER 8 DÍGITOS TRAS +56 9"
    return True, None


def validar_cliente(nombre, correo, telefono):
    """
    Valida los tres campos juntos.
    Retorna (True, None) si todo está bien,
    o (False, mensaje_error) al primer error encontrado.
    """
    for fn, valor in [
        (validar_nombre,   nombre),
        (validar_correo,   correo),
        (validar_telefono, telefono),
    ]:
        ok, msg = fn(valor)
        if not ok:
            return False, msg
    return True, None


def validar_duplicados(correo, telefono, id_excluir=None):
    """
    Verifica si correo o teléfono ya existen.
    id_excluir: ID a ignorar (útil para actualizar un cliente).
    Retorna (True, None) o (False, mensaje_error).
    """
    try:
        clientes = leer_clientes()
    except Exception:
        return True, None  # Si hay error al leer, permitir continuar
    
    for c in clientes:
        if id_excluir and c["ID"] == id_excluir:
            continue
        if c["CORREO"].lower() == correo.lower():
            return False, f"EL CORREO YA EXISTE (ID: {c['ID']})"
        if c["TELEFONO"] == telefono:
            return False, f"EL TELÉFONO YA EXISTE (ID: {c['ID']})"
    return True, None


def validar_integridad_csv():
    """
    Valida que el CSV tenga formato correcto.
    Retorna (True, None) o (False, mensaje_error).
    """
    if not os.path.exists(ARCHIVO):
        return True, None  # Archivo no existe, se creará nuevo
    
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            lector = csv.reader(f)
            # Verificar encabezado
            encabezado = next(lector, None)
            if encabezado != ["ID", "NOMBRE", "CORREO", "TELEFONO"]:
                return False, "FORMATO DE CSV INVÁLIDO: ENCABEZADO INCORRECTO"
            
            # Validar que cada fila tenga exactamente 4 columnas
            for num_fila, fila in enumerate(lector, start=2):
                if len(fila) != 4:
                    return False, f"FORMATO DE CSV INVÁLIDO: FILA {num_fila} CON {len(fila)} COLUMNAS"
                # Validar que el ID no esté vacío
                if not fila[0].strip():
                    return False, f"FORMATO DE CSV INVÁLIDO: ID VACÍO EN FILA {num_fila}"
        
        return True, None
    except UnicodeDecodeError:
        return False, "ARCHIVO CORRUPTO: CODIFICACIÓN INVÁLIDA"
    except Exception as e:
        return False, f"ERROR AL VALIDAR CSV: {e}"


# ─────────────────────────────────────────────
# INICIALIZACIÓN
# ─────────────────────────────────────────────

def inicializar_base():
    """Crea el CSV con cabeceras si no existe."""
    if not os.path.exists(ARCHIVO):
        try:
            with open(ARCHIVO, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "NOMBRE", "CORREO", "TELEFONO"])
        except IOError as e:
            raise IOError(f"NO SE PUDO CREAR EL ARCHIVO: {e}")


# ─────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────

def leer_clientes():
    """Retorna lista de dicts con todos los clientes."""
    # Validar integridad antes de leer
    ok, msg = validar_integridad_csv()
    if not ok:
        raise ValueError(msg)
    
    inicializar_base()
    try:
        with open(ARCHIVO, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except IOError as e:
        raise IOError(f"NO SE PUDO LEER EL ARCHIVO: {e}")
    except Exception as e:
        raise Exception(f"ERROR AL LEER EL ARCHIVO: {e}")


def _generar_id(ids_existentes):
    """Genera un ID de 4 dígitos que no esté en ids_existentes."""
    nuevo_id = None
    while nuevo_id is None or nuevo_id in ids_existentes:
        nuevo_id = f"{random.randint(0, 9999):04d}"
    return nuevo_id


def crear_cliente(nombre, correo, telefono):
    """
    Valida y crea un cliente.
    Retorna (True, id_nuevo) o (False, mensaje_error).
    """
    nombre  = nombre.strip().upper()
    correo  = correo.strip().lower()
    telefono = telefono.strip()

    ok, msg = validar_cliente(nombre, correo, telefono)
    if not ok:
        return False, msg

    ok, msg = validar_duplicados(correo, telefono)
    if not ok:
        return False, msg

    try:
        clientes = leer_clientes()
        ids_existentes = {c["ID"] for c in clientes}
        nuevo_id = _generar_id(ids_existentes)

        with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([nuevo_id, nombre, correo, telefono])
    except IOError as e:
        return False, f"ERROR AL GUARDAR: {e}"
    except Exception as e:
        return False, f"ERROR INESPERADO: {e}"

    return True, nuevo_id


def buscar_clientes(termino):
    """
    Busca clientes cuyo NOMBRE contenga el término (sin distinguir mayúsculas).
    Retorna lista de dicts (puede ser vacía).
    """
    termino = termino.strip().upper()
    return [c for c in leer_clientes() if termino in c["NOMBRE"]]


def actualizar_cliente(id_cliente, nombre, correo, telefono):
    """
    Valida y actualiza un cliente por ID.
    Retorna (True, None) o (False, mensaje_error).
    """
    nombre   = nombre.strip().upper()
    correo   = correo.strip().lower()
    telefono = telefono.strip()

    ok, msg = validar_cliente(nombre, correo, telefono)
    if not ok:
        return False, msg

    ok, msg = validar_duplicados(correo, telefono, id_excluir=id_cliente)
    if not ok:
        return False, msg

    try:
        clientes = leer_clientes()
        actualizado = False

        for cliente in clientes:
            if cliente["ID"] == id_cliente:
                cliente["NOMBRE"]   = nombre
                cliente["CORREO"]   = correo
                cliente["TELEFONO"] = telefono
                actualizado = True
                break

        if not actualizado:
            return False, f"NO SE ENCONTRÓ EL ID: {id_cliente}"

        _guardar_todos(clientes)
    except IOError as e:
        return False, f"ERROR AL GUARDAR: {e}"
    except Exception as e:
        return False, f"ERROR INESPERADO: {e}"

    return True, None


def eliminar_cliente(id_cliente):
    """
    Elimina un cliente por ID.
    Retorna (True, None) o (False, mensaje_error).
    """
    try:
        clientes = leer_clientes()
        nuevos = [c for c in clientes if c["ID"] != id_cliente]

        if len(nuevos) == len(clientes):
            return False, f"NO SE ENCONTRÓ EL ID: {id_cliente}"

        _guardar_todos(nuevos)
    except IOError as e:
        return False, f"ERROR AL GUARDAR: {e}"
    except Exception as e:
        return False, f"ERROR INESPERADO: {e}"

    return True, None


# ─────────────────────────────────────────────
# AUXILIAR INTERNO
# ─────────────────────────────────────────────

def _guardar_todos(lista):
    """Sobreescribe el CSV con la lista entregada."""
    try:
        with open(ARCHIVO, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "NOMBRE", "CORREO", "TELEFONO"])
            for c in lista:
                writer.writerow([c["ID"], c["NOMBRE"], c["CORREO"], c["TELEFONO"]])
    except IOError as e:
        raise IOError(f"NO SE PUDO GUARDAR EL ARCHIVO: {e}")
    except Exception as e:
        raise Exception(f"ERROR AL GUARDAR: {e}")
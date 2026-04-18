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
    return True, None


def validar_correo(correo):
    """Retorna (True, None) o (False, mensaje_error)."""
    if not correo or "@" not in correo:
        return False, "CORREO NO VÁLIDO"
    usuario, dominio = correo.split("@", 1)
    if not usuario or not dominio:
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


# ─────────────────────────────────────────────
# INICIALIZACIÓN
# ─────────────────────────────────────────────

def inicializar_base():
    """Crea el CSV con cabeceras si no existe."""
    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "NOMBRE", "CORREO", "TELEFONO"])


# ─────────────────────────────────────────────
# CRUD
# ─────────────────────────────────────────────

def leer_clientes():
    """Retorna lista de dicts con todos los clientes."""
    inicializar_base()
    with open(ARCHIVO, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


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

    clientes = leer_clientes()
    ids_existentes = {c["ID"] for c in clientes}
    nuevo_id = _generar_id(ids_existentes)

    with open(ARCHIVO, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([nuevo_id, nombre, correo, telefono])

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
    return True, None


def eliminar_cliente(id_cliente):
    """
    Elimina un cliente por ID.
    Retorna (True, None) o (False, mensaje_error).
    """
    clientes = leer_clientes()
    nuevos = [c for c in clientes if c["ID"] != id_cliente]

    if len(nuevos) == len(clientes):
        return False, f"NO SE ENCONTRÓ EL ID: {id_cliente}"

    _guardar_todos(nuevos)
    return True, None


# ─────────────────────────────────────────────
# AUXILIAR INTERNO
# ─────────────────────────────────────────────

def _guardar_todos(lista):
    """Sobreescribe el CSV con la lista entregada."""
    with open(ARCHIVO, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "NOMBRE", "CORREO", "TELEFONO"])
        for c in lista:
            writer.writerow([c["ID"], c["NOMBRE"], c["CORREO"], c["TELEFONO"]])
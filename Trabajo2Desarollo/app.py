import customtkinter as ctk
from crud_clientes import (
    crear_cliente,
    leer_clientes,
    buscar_clientes,
    actualizar_cliente,
    eliminar_cliente,
    PREFIJO_TELEFONO,
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppRegistros(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SISTEMA DE GESTIÓN DE CLIENTES")
        self.geometry("860x680")
        self.resizable(False, False)
        self.after(100, self._centrar_ventana)

        self._construir_ui()
        self._actualizar_lista()

    # ─────────────────────────────────────────
    # CONSTRUCCIÓN DE LA UI
    # ─────────────────────────────────────────

    def _construir_ui(self):
        # Título
        ctk.CTkLabel(
            self, text="REGISTRO EMPRESARIAL DE CLIENTES",
            font=("Arial", 22, "bold"),
        ).pack(pady=(18, 6))

        # ── Formulario de registro ──────────────────────────────────────
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.pack(pady=6, padx=20)

        ancho = 340

        self.entrada_nombre = ctk.CTkEntry(
            marco, placeholder_text="NOMBRE COMPLETO", width=ancho)
        self.entrada_nombre.pack(pady=4)

        self.entrada_correo = ctk.CTkEntry(
            marco, placeholder_text="CORREO ELECTRÓNICO", width=ancho)
        self.entrada_correo.pack(pady=4)

        self.entrada_telefono = ctk.CTkEntry(
            marco, placeholder_text=f"{PREFIJO_TELEFONO}_________", width=ancho)
        self.entrada_telefono.pack(pady=4)
        self.entrada_telefono.insert(0, PREFIJO_TELEFONO)
        self.entrada_telefono.bind("<FocusIn>",  self._colocar_cursor_telefono)
        self.entrada_telefono.bind("<KeyPress>", self._validar_prefijo_telefono)

        ctk.CTkButton(
            marco, text="REGISTRAR NUEVO CLIENTE",
            command=self._registrar_cliente,
            fg_color="#1a5276", hover_color="#21618c",
        ).pack(pady=12, fill="x")

        # ── Buscador — botones SIEMPRE visibles ────────────────────────
        marco_busqueda = ctk.CTkFrame(self, fg_color="transparent")
        marco_busqueda.pack(pady=(4, 8), padx=20)

        self.entrada_buscar = ctk.CTkEntry(
            marco_busqueda, placeholder_text="BUSCAR POR NOMBRE...", width=300)
        self.entrada_buscar.pack(side="left")
        self.entrada_buscar.bind("<Return>", lambda e: self._consultar_cliente())

        ctk.CTkButton(
            marco_busqueda, text="🔍 BUSCAR",
            command=self._consultar_cliente,
            fg_color="#1e8449", hover_color="#239b56",
            width=110,
        ).pack(side="left", padx=(8, 6))

        ctk.CTkButton(
            marco_busqueda, text="MOSTRAR TODOS",
            command=self._actualizar_lista,
            fg_color="#5d6d7e", hover_color="#717d8a",
            width=130,
        ).pack(side="left")

        # ── Etiqueta de estado ─────────────────────────────────────────
        self.etiqueta_estado = ctk.CTkLabel(
            self, text="SISTEMA LISTO", font=("Arial", 12, "italic"))
        self.etiqueta_estado.pack(pady=2)

        # ── Tabla de resultados ────────────────────────────────────────
        self.caja_texto = ctk.CTkTextbox(
            self, height=200, font=("Courier New", 12))
        self.caja_texto.pack(pady=(4, 6), padx=20, fill="both", expand=True)

        # ── Botones de acción sobre un registro ───────────────────────
        marco_acciones = ctk.CTkFrame(self, fg_color="transparent")
        marco_acciones.pack(pady=(2, 14), padx=20)

        ctk.CTkLabel(
            marco_acciones, text="ID:", font=("Arial", 13),
        ).pack(side="left")

        self.entrada_id = ctk.CTkEntry(
            marco_acciones, placeholder_text="ID del cliente", width=90)
        self.entrada_id.pack(side="left", padx=(4, 12))

        ctk.CTkButton(
            marco_acciones, text="✏  EDITAR",
            command=self._abrir_modal_edicion,
            fg_color="#7d6608", hover_color="#9a7d0a",
            width=120,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            marco_acciones, text="🗑  ELIMINAR",
            command=self._eliminar_cliente,
            fg_color="#7b241c", hover_color="#96281b",
            width=120,
        ).pack(side="left")

    # ─────────────────────────────────────────
    # ACCIONES CRUD
    # ─────────────────────────────────────────

    def _registrar_cliente(self):
        ok, resultado = crear_cliente(
            self.entrada_nombre.get(),
            self.entrada_correo.get(),
            self.entrada_telefono.get(),
        )
        if not ok:
            self._set_estado(f"ERROR: {resultado}", "#e74c3c")
            return
        self._set_estado(f"REGISTRO EXITOSO — ID: {resultado}", "#2ecc71")
        self._limpiar_entradas()
        self._actualizar_lista()

    def _consultar_cliente(self):
        termino = self.entrada_buscar.get().strip()
        if not termino:
            self._actualizar_lista()
            return
        resultados = buscar_clientes(termino)
        self._renderizar_tabla(resultados)
        if resultados:
            self._set_estado(
                f"{len(resultados)} RESULTADO(S) PARA '{termino.upper()}'", "#3498db")
        else:
            self._set_estado(
                f"SIN RESULTADOS PARA '{termino.upper()}'", "#f1c40f")

    def _actualizar_lista(self):
        self._renderizar_tabla(leer_clientes())
        self._set_estado("LISTADO ACTUALIZADO", "white")

    def _eliminar_cliente(self):
        id_cliente = self.entrada_id.get().strip()
        if not id_cliente:
            self._set_estado("ERROR: INGRESA UN ID PARA ELIMINAR", "#e74c3c")
            return
        ok, msg = eliminar_cliente(id_cliente)
        if not ok:
            self._set_estado(f"ERROR: {msg}", "#e74c3c")
            return
        self._set_estado(f"CLIENTE {id_cliente} ELIMINADO", "#e67e22")
        self.entrada_id.delete(0, "end")
        self._actualizar_lista()

    def _abrir_modal_edicion(self):
        """Abre una ventana secundaria para editar un cliente por ID."""
        id_cliente = self.entrada_id.get().strip()
        if not id_cliente:
            self._set_estado("ERROR: INGRESA UN ID PARA EDITAR", "#e74c3c")
            return

        clientes = leer_clientes()
        cliente = next((c for c in clientes if c["ID"] == id_cliente), None)
        if cliente is None:
            self._set_estado(f"ERROR: NO SE ENCONTRÓ EL ID {id_cliente}", "#e74c3c")
            return

        # ── Modal ──────────────────────────────────────────────────────
        modal = ctk.CTkToplevel(self)
        modal.title(f"EDITAR CLIENTE — ID {id_cliente}")
        modal.geometry("400x300")
        modal.resizable(False, False)
        modal.grab_set()

        ctk.CTkLabel(
            modal, text=f"EDITANDO ID: {id_cliente}",
            font=("Arial", 15, "bold"),
        ).pack(pady=(16, 10))

        ancho = 320

        e_nombre = ctk.CTkEntry(modal, width=ancho)
        e_nombre.insert(0, cliente["NOMBRE"])
        e_nombre.pack(pady=5)

        e_correo = ctk.CTkEntry(modal, width=ancho)
        e_correo.insert(0, cliente["CORREO"])
        e_correo.pack(pady=5)

        e_telefono = ctk.CTkEntry(modal, width=ancho)
        e_telefono.insert(0, cliente["TELEFONO"])
        e_telefono.pack(pady=5)

        lbl_error = ctk.CTkLabel(modal, text="", text_color="#e74c3c", font=("Arial", 11))
        lbl_error.pack()

        def _guardar():
            ok, msg = actualizar_cliente(
                id_cliente,
                e_nombre.get(),
                e_correo.get(),
                e_telefono.get(),
            )
            if not ok:
                lbl_error.configure(text=f"ERROR: {msg}")
                return
            self._set_estado(f"CLIENTE {id_cliente} ACTUALIZADO", "#2ecc71")
            self.entrada_id.delete(0, "end")
            self._actualizar_lista()
            modal.destroy()

        ctk.CTkButton(
            modal, text="GUARDAR CAMBIOS",
            command=_guardar,
            fg_color="#1a5276", hover_color="#21618c",
        ).pack(pady=10, padx=20, fill="x")

    # ─────────────────────────────────────────
    # HELPERS DE UI
    # ─────────────────────────────────────────

    def _renderizar_tabla(self, filas):
        self.caja_texto.configure(state="normal")
        self.caja_texto.delete("1.0", "end")
        encabezado = f"{'ID':<6}| {'NOMBRE':<28}| {'CORREO':<28}| TEL\n"
        self.caja_texto.insert("end", encabezado + "─" * 82 + "\n")
        for fila in filas:
            linea = (
                f"{fila['ID']:<6}| {fila['NOMBRE']:<28}| "
                f"{fila['CORREO']:<28}| {fila['TELEFONO']}\n"
            )
            self.caja_texto.insert("end", linea)
        self.caja_texto.configure(state="disabled")

    def _set_estado(self, mensaje, color="white"):
        self.etiqueta_estado.configure(text=mensaje, text_color=color)

    def _limpiar_entradas(self):
        self.entrada_nombre.delete(0, "end")
        self.entrada_correo.delete(0, "end")
        self.entrada_telefono.delete(0, "end")
        self.entrada_telefono.insert(0, PREFIJO_TELEFONO)

    # ─────────────────────────────────────────
    # TELÉFONO — PROTECCIÓN DEL PREFIJO
    # ─────────────────────────────────────────

    def _colocar_cursor_telefono(self, event=None):
        texto = self.entrada_telefono.get()
        if not texto.startswith(PREFIJO_TELEFONO):
            self.entrada_telefono.delete(0, "end")
            self.entrada_telefono.insert(0, PREFIJO_TELEFONO)
        self.entrada_telefono.icursor(len(PREFIJO_TELEFONO))

    def _validar_prefijo_telefono(self, event):
        cursor = int(self.entrada_telefono.index("insert"))
        limite = len(PREFIJO_TELEFONO)
        if event.keysym == "BackSpace" and cursor <= limite:
            return "break"
        if event.keysym == "Delete" and cursor < limite:
            return "break"
        if event.keysym in ("Left", "Home"):
            self.entrada_telefono.icursor(limite)
            return "break"
        self.after(1, self._reforzar_prefijo_telefono)

    def _reforzar_prefijo_telefono(self):
        texto = self.entrada_telefono.get()
        if not texto.startswith(PREFIJO_TELEFONO):
            parte = texto.lstrip(PREFIJO_TELEFONO.strip())
            self.entrada_telefono.delete(0, "end")
            self.entrada_telefono.insert(0, PREFIJO_TELEFONO + parte)
            self.entrada_telefono.icursor(len(PREFIJO_TELEFONO) + len(parte))

    # ─────────────────────────────────────────
    # UTILIDADES DE VENTANA
    # ─────────────────────────────────────────

    def _centrar_ventana(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (sw - w) // 2
        y = max((sh - h) // 2 - 30, 0)
        self.geometry(f"+{x}+{y}")


if __name__ == "__main__":
    app = AppRegistros()
    app.mainloop()
import customtkinter as ctk
from crud_clientes import (
    crear_cliente,
    leer_clientes,
    buscar_clientes,
    eliminar_cliente,
    PREFIJO_TELEFONO,
)
from modal_edicion import ModalEdicion

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class AppRegistros(ctk.CTk):

    # Paleta centralizada
    COLOR_PRIMARIO       = "#1a5276"
    COLOR_PRIMARIO_HOVER = "#21618c"
    COLOR_EXITO          = "#2ecc71"
    COLOR_ERROR          = "#e74c3c"
    COLOR_INFO           = "#3498db"
    COLOR_ALERTA         = "#f1c40f"
    COLOR_NEUTRO         = "#5d6d7e"
    COLOR_NEUTRO_HOVER   = "#717d8a"
    COLOR_EDITAR         = "#7d6608"
    COLOR_EDITAR_HOVER   = "#9a7d0a"
    COLOR_ELIMINAR       = "#7b241c"
    COLOR_ELIMINAR_HOVER = "#96281b"

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
        self._ui_titulo()
        self._ui_formulario()
        self._ui_buscador()
        self._ui_estado()
        self._ui_tabla()
        self._ui_acciones()

    def _ui_titulo(self):
        ctk.CTkLabel(
            self, text="REGISTRO EMPRESARIAL DE CLIENTES",
            font=("Arial", 22, "bold"),
        ).pack(pady=(18, 6))

    def _ui_formulario(self):
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.pack(pady=6, padx=20)

        self.entrada_nombre   = self._entry(marco, "NOMBRE COMPLETO")
        self.entrada_correo   = self._entry(marco, "CORREO ELECTRÓNICO")
        self.entrada_telefono = self._entry(marco, f"{PREFIJO_TELEFONO}_________")

        self.entrada_telefono.insert(0, PREFIJO_TELEFONO)
        self.entrada_telefono.bind("<FocusIn>",  self._colocar_cursor_telefono)
        self.entrada_telefono.bind("<KeyPress>", self._validar_prefijo_telefono)

        ctk.CTkButton(
            marco, text="REGISTRAR NUEVO CLIENTE",
            command=self._registrar_cliente,
            fg_color=self.COLOR_PRIMARIO,
            hover_color=self.COLOR_PRIMARIO_HOVER,
        ).pack(pady=12, fill="x")

    def _ui_buscador(self):
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.pack(pady=(4, 8), padx=20)

        self.entrada_buscar = ctk.CTkEntry(
            marco, placeholder_text="BUSCAR POR NOMBRE...", width=300)
        self.entrada_buscar.pack(side="left")
        self.entrada_buscar.bind("<Return>", lambda e: self._consultar_cliente())

        ctk.CTkButton(
            marco, text="🔍 BUSCAR",
            command=self._consultar_cliente,
            fg_color="#1e8449", hover_color="#239b56", width=110,
        ).pack(side="left", padx=(8, 6))

        ctk.CTkButton(
            marco, text="MOSTRAR TODOS",
            command=self._actualizar_lista,
            fg_color=self.COLOR_NEUTRO,
            hover_color=self.COLOR_NEUTRO_HOVER, width=130,
        ).pack(side="left")

    def _ui_estado(self):
        self.etiqueta_estado = ctk.CTkLabel(
            self, text="SISTEMA LISTO", font=("Arial", 12, "italic"))
        self.etiqueta_estado.pack(pady=2)

    def _ui_tabla(self):
        self.caja_texto = ctk.CTkTextbox(self, height=200, font=("Courier New", 12))
        self.caja_texto.pack(pady=(4, 6), padx=20, fill="both", expand=True)

    def _ui_acciones(self):
        marco = ctk.CTkFrame(self, fg_color="transparent")
        marco.pack(pady=(2, 14), padx=20)

        ctk.CTkLabel(marco, text="ID:", font=("Arial", 13)).pack(side="left")

        self.entrada_id = ctk.CTkEntry(
            marco, placeholder_text="ID del cliente", width=90)
        self.entrada_id.pack(side="left", padx=(4, 12))

        ctk.CTkButton(
            marco, text="✏  EDITAR",
            command=self._abrir_modal_edicion,
            fg_color=self.COLOR_EDITAR,
            hover_color=self.COLOR_EDITAR_HOVER, width=120,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            marco, text="🗑  ELIMINAR",
            command=self._eliminar_cliente,
            fg_color=self.COLOR_ELIMINAR,
            hover_color=self.COLOR_ELIMINAR_HOVER, width=120,
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
            self._estado_error(f"ERROR: {resultado}")
            return
        self._estado_ok(f"REGISTRO EXITOSO — ID: {resultado}")
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
            self._estado_info(f"{len(resultados)} RESULTADO(S) PARA '{termino.upper()}'")
        else:
            self._estado_alerta(f"SIN RESULTADOS PARA '{termino.upper()}'")

    def _actualizar_lista(self):
        self._renderizar_tabla(leer_clientes())
        self._set_estado("LISTADO ACTUALIZADO")

    def _eliminar_cliente(self):
        id_cliente = self.entrada_id.get().strip()
        if not id_cliente:
            self._estado_error("ERROR: INGRESA UN ID PARA ELIMINAR")
            return
        ok, msg = eliminar_cliente(id_cliente)
        if not ok:
            self._estado_error(f"ERROR: {msg}")
            return
        self._set_estado(f"CLIENTE {id_cliente} ELIMINADO", "#e67e22")
        self.entrada_id.delete(0, "end")
        self._actualizar_lista()

    def _abrir_modal_edicion(self):
        id_cliente = self.entrada_id.get().strip()
        if not id_cliente:
            self._estado_error("ERROR: INGRESA UN ID PARA EDITAR")
            return
        cliente = next((c for c in leer_clientes() if c["ID"] == id_cliente), None)
        if cliente is None:
            self._estado_error(f"ERROR: NO SE ENCONTRÓ EL ID {id_cliente}")
            return
        ModalEdicion(self, cliente, on_guardado=self._post_edicion)

    def _post_edicion(self, id_cliente):
        """Callback que ejecuta ModalEdicion al guardar con éxito."""
        self._estado_ok(f"CLIENTE {id_cliente} ACTUALIZADO")
        self.entrada_id.delete(0, "end")
        self._actualizar_lista()

    # ─────────────────────────────────────────
    # HELPERS DE UI
    # ─────────────────────────────────────────

    def _entry(self, parent, placeholder, width=340):
        """Crea un CTkEntry con placeholder y lo empaqueta."""
        e = ctk.CTkEntry(parent, placeholder_text=placeholder, width=width)
        e.pack(pady=4)
        return e

    def _renderizar_tabla(self, filas):
        self.caja_texto.configure(state="normal")
        self.caja_texto.delete("1.0", "end")
        encabezado = f"{'ID':<6}| {'NOMBRE':<28}| {'CORREO':<28}| TEL\n"
        self.caja_texto.insert("end", encabezado + "─" * 82 + "\n")
        for fila in filas:
            self.caja_texto.insert(
                "end",
                f"{fila['ID']:<6}| {fila['NOMBRE']:<28}| "
                f"{fila['CORREO']:<28}| {fila['TELEFONO']}\n",
            )
        self.caja_texto.configure(state="disabled")

    def _limpiar_entradas(self):
        for campo in (self.entrada_nombre, self.entrada_correo):
            campo.delete(0, "end")
        self.entrada_telefono.delete(0, "end")
        self.entrada_telefono.insert(0, PREFIJO_TELEFONO)

    # Feedback semántico
    def _set_estado(self, mensaje, color="white"):
        self.etiqueta_estado.configure(text=mensaje, text_color=color)

    def _estado_ok(self, msg):     self._set_estado(msg, self.COLOR_EXITO)
    def _estado_error(self, msg):  self._set_estado(msg, self.COLOR_ERROR)
    def _estado_info(self, msg):   self._set_estado(msg, self.COLOR_INFO)
    def _estado_alerta(self, msg): self._set_estado(msg, self.COLOR_ALERTA)

    # ─────────────────────────────────────────
    # TELÉFONO — PROTECCIÓN DEL PREFIJO
    # ─────────────────────────────────────────

    def _colocar_cursor_telefono(self, event=None):
        if not self.entrada_telefono.get().startswith(PREFIJO_TELEFONO):
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
        self.geometry(f"+{(sw - w) // 2}+{max((sh - h) // 2 - 30, 0)}")


if __name__ == "__main__":
    app = AppRegistros()
    app.mainloop()
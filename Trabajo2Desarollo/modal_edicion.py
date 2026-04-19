import customtkinter as ctk
from crud_clientes import actualizar_cliente, PREFIJO_TELEFONO


class ModalEdicion(ctk.CTkToplevel):
    """Ventana secundaria para editar los datos de un cliente."""

    COLOR_PRIMARIO       = "#1a5276"
    COLOR_PRIMARIO_HOVER = "#21618c"
    COLOR_ERROR          = "#e74c3c"

    def __init__(self, parent, cliente, on_guardado):
        super().__init__(parent)
        self._cliente     = cliente
        self._on_guardado = on_guardado

        self.title(f"EDITAR CLIENTE — ID {cliente['ID']}")
        self.geometry("400x300")
        self.resizable(False, False)
        self.grab_set()

        self._construir_ui()

    def _construir_ui(self):
        ctk.CTkLabel(
            self, text=f"EDITANDO ID: {self._cliente['ID']}",
            font=("Arial", 15, "bold"),
        ).pack(pady=(16, 10))

        self._e_nombre   = self._entry_precargado(self._cliente["NOMBRE"])
        self._e_correo   = self._entry_precargado(self._cliente["CORREO"])
        self._e_telefono = self._entry_precargado(self._cliente["TELEFONO"])

        self._lbl_error = ctk.CTkLabel(
            self, text="", text_color=self.COLOR_ERROR, font=("Arial", 11))
        self._lbl_error.pack()

        ctk.CTkButton(
            self, text="GUARDAR CAMBIOS",
            command=self._guardar,
            fg_color=self.COLOR_PRIMARIO,
            hover_color=self.COLOR_PRIMARIO_HOVER,
        ).pack(pady=10, padx=20, fill="x")

    def _entry_precargado(self, valor, width=320):
        """Crea un CTkEntry ya con el valor inicial insertado."""
        e = ctk.CTkEntry(self, width=width)
        e.insert(0, valor)
        e.pack(pady=5)
        return e

    def _guardar(self):
        nombre   = self._e_nombre.get().strip()
        correo   = self._e_correo.get().strip()
        telefono = self._e_telefono.get().strip()

        # Validar campos no vacíos
        if not nombre:
            self._lbl_error.configure(text="ERROR: EL NOMBRE NO PUEDE ESTAR VACÍO")
            return
        if not correo:
            self._lbl_error.configure(text="ERROR: EL CORREO NO PUEDE ESTAR VACÍO")
            return
        if not telefono or telefono == PREFIJO_TELEFONO:
            self._lbl_error.configure(text="ERROR: EL TELÉFONO NO PUEDE ESTAR VACÍO")
            return

        try:
            ok, msg = actualizar_cliente(
                self._cliente["ID"],
                nombre,
                correo,
                telefono,
            )
            if not ok:
                self._lbl_error.configure(text=f"ERROR: {msg}")
                return
            self._on_guardado(self._cliente["ID"])
            self.destroy()
        except Exception as e:
            self._lbl_error.configure(text=f"ERROR INESPERADO: {e}")
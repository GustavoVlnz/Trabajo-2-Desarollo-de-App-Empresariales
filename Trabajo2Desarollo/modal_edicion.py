import re
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
        self._telefono_var = ctk.StringVar(value=self._cliente["TELEFONO"])
        self._e_telefono = self._entry_telefono(self._telefono_var)

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

    def _entry_telefono(self, variable, width=320):
        e = ctk.CTkEntry(
            self,
            textvariable=variable,
            placeholder_text=f"{PREFIJO_TELEFONO}XXXX XXXX",
            width=width,
        )
        e.pack(pady=5)
        variable.trace_add("write", self._on_telefono_var_changed)
        e.bind("<FocusIn>", self._colocar_cursor_telefono)
        e.bind("<KeyPress>", self._validar_prefijo_telefono)
        return e

    def _on_telefono_var_changed(self, *args):
        if getattr(self, "_telefono_actualizando", False):
            return
        self._telefono_actualizando = True
        try:
            texto = self._telefono_var.get() or ""
            if not texto.startswith(PREFIJO_TELEFONO):
                texto = PREFIJO_TELEFONO + texto
            digitos = re.sub(r"\D", "", texto[len(PREFIJO_TELEFONO):])[:8]
            if len(digitos) <= 4:
                nuevo = PREFIJO_TELEFONO + digitos
            else:
                nuevo = PREFIJO_TELEFONO + digitos[:4] + " " + digitos[4:]
            if texto != nuevo:
                self._telefono_var.set(nuevo)
            if int(self._e_telefono.index("insert")) < len(PREFIJO_TELEFONO):
                self._e_telefono.icursor(len(PREFIJO_TELEFONO))
        finally:
            self._telefono_actualizando = False

    def _colocar_cursor_telefono(self, event=None):
        if not self._telefono_var.get().startswith(PREFIJO_TELEFONO):
            self._telefono_var.set(PREFIJO_TELEFONO)
        self._e_telefono.icursor(len(PREFIJO_TELEFONO))

    def _validar_prefijo_telefono(self, event):
        cursor = int(self._e_telefono.index("insert"))
        limite = len(PREFIJO_TELEFONO)
        if event.keysym == "BackSpace" and cursor <= limite:
            return "break"
        if event.keysym == "Delete" and cursor < limite:
            return "break"
        if event.keysym in ("Left", "Home"):
            self._e_telefono.icursor(limite)
            return "break"
        self.after(1, self._colocar_cursor_telefono)

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
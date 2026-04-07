import customtkinter as ctk
import csv
import os
import random
import re

# CONFIGURACION DE APARIENCIA
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppRegistros(ctk.CTk):
    def __init__(self):
        super().__init__()

        # CONFIGURACION DE LA VENTANA (TAMAÑO FIJO)
        self.title("SISTEMA DE GESTION DE CLIENTES")
        self.geometry("800x600")
        self.resizable(False, False) # BLOQUEA EL CAMBIO DE TAMAÑO
        
        # CENTRAR VENTANA EN LA PANTALLA
        self.after(100, self.centrar_ventana)

        self.inicializar_base_datos()

        # --- DISEÑO DE LA INTERFAZ ---
        
        # TITULO PRINCIPAL
        self.titulo = ctk.CTkLabel(self, text="REGISTRO EMPRESARIAL DE CLIENTES", font=("Arial", 24, "bold"))
        self.titulo.pack(pady=20)

        # FORMULARIO DE ENTRADA
        self.marco_formulario = ctk.CTkFrame(self, fg_color="transparent", border_width=0)
        self.marco_formulario.pack(pady=10, padx=20)

        entrada_ancho = 340
        self.entrada_nombre = ctk.CTkEntry(self.marco_formulario, placeholder_text="NOMBRE COMPLETO", width=entrada_ancho)
        self.entrada_nombre.pack(pady=5)

        self.entrada_correo = ctk.CTkEntry(self.marco_formulario, placeholder_text="CORREO ELECTRONICO", width=entrada_ancho)
        self.entrada_correo.pack(pady=5)

        self.telefono_prefijo = "+56 9 "
        self.entrada_telefono = ctk.CTkEntry(self.marco_formulario, placeholder_text=self.telefono_prefijo + "_________", width=entrada_ancho)
        self.entrada_telefono.pack(pady=5)
        self.entrada_telefono.insert(0, self.telefono_prefijo)
        self.entrada_telefono.bind("<FocusIn>", self.colocar_cursor_telefono)
        self.entrada_telefono.bind("<KeyPress>", self.validar_prefijo_telefono)

        self.boton_registrar = ctk.CTkButton(self.marco_formulario, text="REGISTRAR NUEVO CLIENTE", 
                                             command=self.registrar_cliente, fg_color="#1a5276", hover_color="#21618c")
        self.boton_registrar.pack(pady=15, fill="x")

        # AREA DE BUSQUEDA (ARRIBA DE LA TABLA)
        self.marco_busqueda = ctk.CTkFrame(self, fg_color="transparent", border_width=0)
        self.marco_busqueda.pack(pady=(5, 10), padx=20)

        self.entrada_buscar = ctk.CTkEntry(self.marco_busqueda, placeholder_text="BUSCAR POR NOMBRE...", width=340)
        self.entrada_buscar.pack(pady=5, side="left")
        self.entrada_buscar.bind("<FocusIn>", self.mostrar_botones_busqueda)

        self.boton_buscar = ctk.CTkButton(self.marco_busqueda, text="🔍", 
                                          command=self.consultar_cliente, fg_color="#1e8449", hover_color="#239b56", width=60, font=("Arial", 18, "bold"))
        self.boton_buscar.pack(side="left", padx=(8, 8), pady=5)
        self.boton_buscar.pack_forget()

        self.boton_ver_todos = ctk.CTkButton(self.marco_busqueda, text="MOSTRAR TODOS", 
                                             command=self.actualizar_lista, fg_color="#5d6d7e", width=140)
        self.boton_ver_todos.pack(side="left", padx=(0, 0), pady=5)
        self.boton_ver_todos.pack_forget()

        self.bind("<Button-1>", self.click_fuera_busqueda)

        # ETIQUETA DE ESTADO (LOGICA DE FEEDBACK)
        self.etiqueta_estado = ctk.CTkLabel(self, text="SISTEMA LISTO", font=("Arial", 12, "italic"))
        self.etiqueta_estado.pack(pady=3)

        # LISTA DE RESULTADOS (TABLA VISUAL)
        self.caja_texto = ctk.CTkTextbox(self, height=220, font=("Courier New", 13))
        self.caja_texto.pack(pady=(5, 10), padx=20, fill="both", expand=True)
        
        self.actualizar_lista()

    # --- LOGICA DE LA APLICACION ---

    def inicializar_base_datos(self):
        if not os.path.exists('clientes.csv'):
            with open('clientes.csv', mode='w', newline='', encoding='utf-8') as f:
                escritor = csv.writer(f)
                escritor.writerow(['ID', 'NOMBRE', 'CORREO', 'TELEFONO'])

    def validar_correo(self, correo):
        dominios_validos = {
            'gmail.com', 'gmail.cl',
            'hotmail.com', 'hotmail.cl',
            'outlook.com', 'outlook.cl',
            'yahoo.com', 'yahoo.cl',
            'live.com', 'icloud.com'
        }
        if not correo or '@' not in correo:
            return False
        usuario, dominio = correo.split('@', 1)
        if not usuario or not dominio:
            return False
        if not re.match(r'^[A-Za-z0-9._%+-]+$', usuario):
            return False
        if dominio not in dominios_validos:
            return False
        return True

    def validar_telefono(self, telefono):
        if not telefono.startswith(self.telefono_prefijo):
            return False
        parte = telefono[len(self.telefono_prefijo):]
        digitos = re.sub(r'\D', '', parte)
        return len(digitos) == 8 and digitos.isdigit()

    def registrar_cliente(self):
        nombre = self.entrada_nombre.get().upper()
        correo = self.entrada_correo.get().lower()
        telefono = self.entrada_telefono.get()

        if not nombre:
            self.etiqueta_estado.configure(text="ERROR: INGRESA EL NOMBRE", text_color="#e74c3c")
            return

        if not self.validar_correo(correo):
            self.etiqueta_estado.configure(text="ERROR: CORREO NO VALIDO", text_color="#e74c3c")
            return

        if not self.validar_telefono(telefono):
            self.etiqueta_estado.configure(text="ERROR: TELEFONO DEBE SER +56 9 8 DIGITOS", text_color="#e74c3c")
            return

        # GENERAR ID UNICO DE 4 DIGITOS ALEATORIO
        ids_existentes = set()
        with open('clientes.csv', mode='r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                ids_existentes.add(fila['ID'])
            
        nuevo_id = None
        while nuevo_id is None or nuevo_id in ids_existentes:
            nuevo_id = f"{random.randint(0, 9999):04d}"

        with open('clientes.csv', mode='a', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f)
            escritor.writerow([nuevo_id, nombre, correo, telefono])
        
        self.etiqueta_estado.configure(text=f"REGISTRO EXITOSO: {nombre}", text_color="#2ecc71")
        self.limpiar_entradas()
        self.actualizar_lista()

    def consultar_cliente(self):
        termino_busqueda = self.entrada_buscar.get().upper()
        self.caja_texto.configure(state="normal")
        self.caja_texto.delete("1.0", "end")
        encabezado = f"{'ID':<5} | {'NOMBRE':<30} | {'CORREO':<30} | {'TEL'}\n"
        self.caja_texto.insert("end", encabezado + ("-"*10) + "\n")

        encontrado = False
        with open('clientes.csv', mode='r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                if termino_busqueda in fila['NOMBRE']:
                    linea = f"{fila['ID']:<5} | {fila['NOMBRE']:<30} | {fila['CORREO']:<30} | {fila['TELEFONO']}\n"
                    self.caja_texto.insert("end", linea)
                    encontrado = True
        
        if not encontrado:
            self.etiqueta_estado.configure(text="NO SE ENCONTRARON RESULTADOS", text_color="#f1c40f")
        else:
            self.etiqueta_estado.configure(text="CONSULTA FINALIZADA", text_color="#3498db")
            
        self.caja_texto.configure(state="disabled")

    def actualizar_lista(self):
        self.caja_texto.configure(state="normal")
        self.caja_texto.delete("1.0", "end")
        encabezado = f"{'ID':<5} | {'NOMBRE':<30} | {'CORREO':<30} | {'TEL'}\n"
        self.caja_texto.insert("end", encabezado + ("-"*85) + "\n")

        with open('clientes.csv', mode='r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                linea = f"{fila['ID']:<5} | {fila['NOMBRE']:<30} | {fila['CORREO']:<30} | {fila['TELEFONO']}\n"
                self.caja_texto.insert("end", linea)
        
        self.caja_texto.configure(state="disabled")
        self.etiqueta_estado.configure(text="LISTADO ACTUALIZADO", text_color="white")

    def mostrar_botones_busqueda(self, event=None):
        self.boton_buscar.pack(side="left", padx=(8, 8), pady=5)
        self.boton_ver_todos.pack(side="left", padx=(0, 0), pady=5)

    def click_fuera_busqueda(self, event):
        if event.widget not in (self.entrada_buscar, self.boton_buscar, self.boton_ver_todos):
            self.boton_buscar.pack_forget()
            self.boton_ver_todos.pack_forget()

    def colocar_cursor_telefono(self, event=None):
        texto = self.entrada_telefono.get()
        if not texto.startswith(self.telefono_prefijo):
            self.entrada_telefono.delete(0, 'end')
            self.entrada_telefono.insert(0, self.telefono_prefijo)
        self.entrada_telefono.icursor(len(self.telefono_prefijo))

    def validar_prefijo_telefono(self, event):
        cursor = int(self.entrada_telefono.index("insert"))
        if event.keysym == "BackSpace":
            if cursor <= len(self.telefono_prefijo):
                return "break"
        elif event.keysym == "Delete":
            if cursor < len(self.telefono_prefijo):
                return "break"
        elif event.keysym == "Left":
            if cursor <= len(self.telefono_prefijo):
                self.entrada_telefono.icursor(len(self.telefono_prefijo))
                return "break"
        elif event.keysym == "Home":
            self.entrada_telefono.icursor(len(self.telefono_prefijo))
            return "break"

        self.after(1, self._reforzar_prefijo_telefono)

    def _reforzar_prefijo_telefono(self):
        texto = self.entrada_telefono.get()
        if not texto.startswith(self.telefono_prefijo):
            texto_sin_prefijo = texto
            if texto.startswith(self.telefono_prefijo.strip()):
                texto_sin_prefijo = texto[len(self.telefono_prefijo.strip()):]
            self.entrada_telefono.delete(0, 'end')
            self.entrada_telefono.insert(0, self.telefono_prefijo + texto_sin_prefijo)
            self.entrada_telefono.icursor(max(len(self.telefono_prefijo), len(texto_sin_prefijo) + len(self.telefono_prefijo)))

    def limpiar_entradas(self):
        self.entrada_nombre.delete(0, 'end')
        self.entrada_correo.delete(0, 'end')
        self.entrada_telefono.delete(0, 'end')
        self.entrada_telefono.insert(0, self.telefono_prefijo)

    def centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        ancho_ventana = self.winfo_width()
        alto_ventana = self.winfo_height()
        ancho_pantalla = self.winfo_screenwidth()
        alto_pantalla = self.winfo_screenheight()
        
        x = (ancho_pantalla - ancho_ventana) // 2
        y = max((alto_pantalla - alto_ventana) // 2 - 30, 0)
        
        self.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    app = AppRegistros()
    app.mainloop()
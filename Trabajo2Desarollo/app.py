import customtkinter as ctk
import csv
import os
import random

# CONFIGURACION DE APARIENCIA
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppRegistros(ctk.CTk):
    def __init__(self):
        super().__init__()

        # CONFIGURACION DE LA VENTANA (TAMAÑO FIJO)
        self.title("SISTEMA DE GESTION DE CLIENTES V1.0")
        self.geometry("800x600")
        self.resizable(False, False) # BLOQUEA EL CAMBIO DE TAMAÑO

        self.inicializar_base_datos()

        # --- DISEÑO DE LA INTERFAZ ---
        
        # TITULO PRINCIPAL
        self.titulo = ctk.CTkLabel(self, text="REGISTRO EMPRESARIAL DE CLIENTES", font=("Arial", 24, "bold"))
        self.titulo.pack(pady=20)

        # CONTENEDOR PRINCIPAL (IZQUIERDA: FORMULARIO, DERECHA: BUSQUEDA)
        self.contenedor_superior = ctk.CTkFrame(self, width=700)
        self.contenedor_superior.pack(pady=10, padx=20)
        self.contenedor_superior.grid_columnconfigure(0, weight=1)
        self.contenedor_superior.grid_columnconfigure(1, weight=1)

        # FORMULARIO DE ENTRADA
        self.marco_formulario = ctk.CTkFrame(self.contenedor_superior, fg_color="transparent")
        self.marco_formulario.grid(row=0, column=0, padx=(10, 5), pady=20, sticky="nw")

        self.entrada_nombre = ctk.CTkEntry(self.marco_formulario, placeholder_text="NOMBRE COMPLETO", width=300)
        self.entrada_nombre.pack(pady=5)

        self.entrada_correo = ctk.CTkEntry(self.marco_formulario, placeholder_text="CORREO ELECTRONICO", width=300)
        self.entrada_correo.pack(pady=5)

        self.entrada_telefono = ctk.CTkEntry(self.marco_formulario, placeholder_text="+56 9 _________", width=300)
        self.entrada_telefono.pack(pady=5)
        self.entrada_telefono.insert(0, "+56 9 ")

        self.boton_registrar = ctk.CTkButton(self.marco_formulario, text="REGISTRAR NUEVO CLIENTE", 
                                             command=self.registrar_cliente, fg_color="#1a5276", hover_color="#21618c")
        self.boton_registrar.pack(pady=15, fill="x")

        # AREA DE BUSQUEDA (SALIDA/CONSULTA)
        self.marco_busqueda = ctk.CTkFrame(self.contenedor_superior, fg_color="transparent")
        self.marco_busqueda.grid(row=0, column=1, padx=(5, 10), pady=20, sticky="nw")

        self.entrada_buscar = ctk.CTkEntry(self.marco_busqueda, placeholder_text="BUSCAR POR NOMBRE...", width=250)
        self.entrada_buscar.pack(pady=5)

        self.boton_buscar = ctk.CTkButton(self.marco_busqueda, text="CONSULTAR", 
                                          command=self.consultar_cliente, fg_color="#1e8449", hover_color="#239b56")
        self.boton_buscar.pack(pady=5, fill="x")

        self.boton_ver_todos = ctk.CTkButton(self.marco_busqueda, text="MOSTRAR TODOS", 
                                             command=self.actualizar_lista, fg_color="#5d6d7e")
        self.boton_ver_todos.pack(pady=5, fill="x")

        # ETIQUETA DE ESTADO (LOGICA DE FEEDBACK)
        self.etiqueta_estado = ctk.CTkLabel(self, text="SISTEMA LISTO", font=("Arial", 12, "italic"))
        self.etiqueta_estado.pack(pady=5)

        # LISTA DE RESULTADOS (TABLA VISUAL)
        self.caja_texto = ctk.CTkTextbox(self, width=750, height=280, font=("Courier New", 13))
        self.caja_texto.pack(pady=10, padx=20)
        
        self.actualizar_lista()

    # --- LOGICA DE LA APLICACION ---

    def inicializar_base_datos(self):
        if not os.path.exists('clientes.csv'):
            with open('clientes.csv', mode='w', newline='', encoding='utf-8') as f:
                escritor = csv.writer(f)
                escritor.writerow(['ID', 'NOMBRE', 'CORREO', 'TELEFONO'])

    def registrar_cliente(self):
        nombre = self.entrada_nombre.get().upper()
        correo = self.entrada_correo.get().lower()
        telefono = self.entrada_telefono.get()

        if nombre and correo and telefono:
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
        else:
            self.etiqueta_estado.configure(text="ERROR: FALTAN DATOS", text_color="#e74c3c")

    def consultar_cliente(self):
        termino_busqueda = self.entrada_buscar.get().upper()
        self.caja_texto.configure(state="normal")
        self.caja_texto.delete("1.0", "end")
        encabezado = f"{'ID':<5} | {'NOMBRE':<30} | {'CORREO':<30} | {'TEL'}\n"
        self.caja_texto.insert("end", encabezado + ("-"*85) + "\n")

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

    def limpiar_entradas(self):
        self.entrada_nombre.delete(0, 'end')
        self.entrada_correo.delete(0, 'end')
        self.entrada_telefono.delete(0, 'end')
        self.entrada_telefono.insert(0, "+56 9 ")

if __name__ == "__main__":
    app = AppRegistros()
    app.mainloop()
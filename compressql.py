import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import datetime
import os
import csv

# Nombre de la carpeta donde se guardarán las imágenes .webp y los archivos .unl y .csv
WEBP_DIR = 'imagenes_webp'
UNL_FILE = 'zimagenes.unl'
CSV_FILE = 'zimagenes.csv'
SQL_FILE = 'zimagenes.sql'

# Crear la carpeta si no existe
if not os.path.exists(WEBP_DIR):
    os.makedirs(WEBP_DIR)

def compress_image(img):
    """ Comprimir la imagen. """
    img = img.convert("RGB")
    return img

def convert_image_to_webp(input_path):
    """ Convertir una imagen a formato .webp y guardarla en la carpeta indicada. """
    try:
        with Image.open(input_path) as img:
            img = compress_image(img)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            webp_name = base_name + '.webp'
            webp_path = os.path.join(WEBP_DIR, webp_name)
            img.save(webp_path, 'webp', quality=85)  # Ajusta la calidad según sea necesario
        return base_name, webp_name, webp_path
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo convertir la imagen: {e}")
        return None, None, None

def create_unl_file(image_data):
    """ Crear el archivo zimagenes.unl con los datos de las imágenes. """
    try:
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        with open(UNL_FILE, 'w') as file:
            for original_name, webp_name in image_data:
                unl_content = f"{original_name}|{webp_name}|{current_date}|1"
                file.write(unl_content + '\n')
        messagebox.showinfo("Éxito", f"Archivo .unl creado exitosamente: {UNL_FILE}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear el archivo .unl: {e}")

def create_csv_file(image_data):
    """ Crear el archivo zimagenes.csv con los nombres de las imágenes .webp. """
    try:
        with open(CSV_FILE, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            for _, webp_name in image_data:
                csvwriter.writerow([webp_name])
        messagebox.showinfo("Éxito", f"Archivo .csv creado exitosamente: {CSV_FILE}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear el archivo .csv: {e}")

def create_sql_file(image_data):
    """ Crear el archivo zimagenes.sql con sentencias INSERT para las imágenes. """
    try:
        sql_content = """--
BEGIN WORK;
--SET client_encoding=LATIN1;
SET client_encoding=UTF8;
SET datestyle = 'ISO,DMY';
ALTER TABLE img_product DISABLE TRIGGER ALL;
DELETE FROM img_product;
"""
        for original_name, webp_name in image_data:
            sql_content += f"INSERT INTO img_product (cod_producto, img, fecha_actualizacion, predet) VALUES ('{original_name}', '{webp_name}', '{datetime.datetime.now().strftime('%Y-%m-%d')}', 1);\n"
        
        sql_content += """ALTER TABLE img_product ENABLE TRIGGER ALL;
COMMIT;
"""
        with open(SQL_FILE, 'w') as sqlfile:
            sqlfile.write(sql_content)
        messagebox.showinfo("Éxito", f"Archivo .sql creado exitosamente: {SQL_FILE}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo crear el archivo .sql: {e}")

def browse_images():
    """ Abrir un diálogo para seleccionar múltiples imágenes y agregarlas a la lista. """
    file_paths = filedialog.askopenfilenames(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
    if file_paths:
        file_listbox.delete(0, tk.END)  # Limpiar la lista antes de agregar nuevas imágenes
        for path in file_paths:
            file_listbox.insert(tk.END, path)  # Guardar la ruta completa
        update_image_count()

def process_images():
    """ Comprimir, convertir y crear los archivos .unl, .csv y .sql con todas las imágenes seleccionadas. """
    if file_listbox.size() == 0:
        messagebox.showwarning("Advertencia", "No hay imágenes seleccionadas.")
        return

    image_data = []
    for index in range(file_listbox.size()):
        original_path = file_listbox.get(index)
        base_name, webp_name, webp_path = convert_image_to_webp(original_path)
        if base_name and webp_name and webp_path:
            image_data.append((base_name, webp_name))

    if image_data:
        create_unl_file(image_data)
        create_csv_file(image_data)
        create_sql_file(image_data)
        update_image_count()

def update_image_count():
    """ Actualizar el recuento de imágenes en la interfaz gráfica. """
    image_count_label.config(text=f"Imágenes seleccionadas: {file_listbox.size()}")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Conversor de Imágenes y Generador de Archivos")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Lista de imágenes seleccionadas
file_listbox = tk.Listbox(frame, selectmode=tk.SINGLE, width=50, height=15, bg="lightgray")
file_listbox.pack(side=tk.LEFT, padx=(0, 10))

# Botones
button_frame = tk.Frame(frame)
button_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.Y)

btn_browse = tk.Button(button_frame, text="Seleccionar Imágenes", command=browse_images)
btn_browse.pack(fill=tk.X)

btn_process = tk.Button(button_frame, text="Comprimir y Convertir", command=process_images)
btn_process.pack(fill=tk.X, pady=5)

# Etiqueta para el conteo de imágenes
image_count_label = tk.Label(frame, text="Imágenes seleccionadas: 0")
image_count_label.pack(side=tk.BOTTOM, pady=(10, 0))

root.mainloop()

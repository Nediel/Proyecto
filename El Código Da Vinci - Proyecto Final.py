import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import datetime
import os

def start_application():
    def update_frame():
        ret, frame = cap.read()
        if ret:
            frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Ajustar los límites de detección de color para mejorar la precisión
            rojoBajo1 = np.array([0, 120, 70], np.uint8)
            rojoAlto1 = np.array([10, 255, 255], np.uint8)
            rojoBajo2 = np.array([170, 120, 70], np.uint8)
            rojoAlto2 = np.array([180, 255, 255], np.uint8)

            verdeBajo = np.array([36, 50, 70], np.uint8)
            verdeAlto = np.array([89, 255, 255], np.uint8)

            # Detectar color rojo
            maskRojo1 = cv2.inRange(frameHSV, rojoBajo1, rojoAlto1)
            maskRojo2 = cv2.inRange(frameHSV, rojoBajo2, rojoAlto2)
            maskRojo = cv2.add(maskRojo1, maskRojo2)
            maskRojoVis = cv2.bitwise_and(frame, frame, mask=maskRojo)

            # Detectar color verde
            maskVerde = cv2.inRange(frameHSV, verdeBajo, verdeAlto)
            maskVerdeVis = cv2.bitwise_and(frame, frame, mask=maskVerde)

            # Calcular porcentaje de píxeles rojos y verdes
            porcentajeRojo = (cv2.countNonZero(maskRojo) / (frame.shape[0] * frame.shape[1])) * 100
            porcentajeVerde = (cv2.countNonZero(maskVerde) / (frame.shape[0] * frame.shape[1])) * 100

            # Mostrar porcentajes en la imagen principal
            cv2.putText(frame, f'Rojo: {porcentajeRojo:.2f}%', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, f'Verde: {porcentajeVerde:.2f}%', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            # Mostrar mensaje de mayoría de color
            if porcentajeVerde > porcentajeRojo:
                label_color.config(text="El objeto es mayoritariamente VERDE", fg='#0033FF')
            else:
                label_color.config(text="El objeto es mayoritariamente ROJO", fg='#0033FF')

            # Convertir imagen para mostrar con Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(image=img)

            # Actualizar imagen en el label
            label_img.img = img
            label_img.config(image=img)

            # Mostrar máscaras de colores
            mask_combined = cv2.addWeighted(maskRojoVis, 1, maskVerdeVis, 1, 0)
            mask_combined = cv2.cvtColor(mask_combined, cv2.COLOR_BGR2RGB)
            mask_img = Image.fromarray(mask_combined)
            mask_img = ImageTk.PhotoImage(image=mask_img)
            label_mask.img = mask_img
            label_mask.config(image=mask_img)

            # Guardar resultados en archivo
            file_path = "resultados_deteccion.csv"
            if not os.path.isfile(file_path) or os.stat(file_path).st_size == 0:
                with open(file_path, "w") as f:
                    f.write("Fecha y Hora,Porcentaje Rojo,Porcentaje Verde\n")
            with open(file_path, "a") as f:
                f.write(f"{datetime.datetime.now()}, {porcentajeRojo:.2f}, {porcentajeVerde:.2f}\n")

            # Llamar a esta función cada 10 ms (aproximadamente 30 FPS)
            label_img.after(10, update_frame)
        else:
            label_color.config(text="Error en la captura de video", fg='#000000')

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        label_color.config(text="No se puede acceder a la cámara", fg='#000000')
        return

    # Crear contenedores para organizar los widgets
    frame1 = tk.Frame(root)
    frame1.grid(row=0, column=0, padx=10, pady=10, sticky='n')

    frame2 = tk.Frame(root)
    frame2.grid(row=0, column=1, padx=10, pady=10, sticky='n')

    label_img = tk.Label(frame1)
    label_img.pack()

    label_rojo = tk.Label(frame1, font=('Arial', 14))
    label_rojo.pack()

    label_verde = tk.Label(frame1, font=('Arial', 14))
    label_verde.pack()

    label_color = tk.Label(frame1, font=('Arial', 14))
    label_color.pack()

    label_mask = tk.Label(frame2)
    label_mask.pack()

    update_frame()

def quit_application():
    root.destroy()

root = tk.Tk()
root.title("Detección de colores")

# Crear contenedores para los botones y centrar la interfaz
button_frame = tk.Frame(root)
button_frame.grid(row=1, column=0, columnspan=2, pady=10)

start_button = tk.Button(button_frame, text="Iniciar", command=start_application)
start_button.grid(row=0, column=0, padx=10)

quit_button = tk.Button(button_frame, text="Salir", command=quit_application)
quit_button.grid(row=0, column=1, padx=10)

root.mainloop()


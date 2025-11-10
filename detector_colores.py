#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de Colores con Webcam
Academia Cortex

Programa para detectar colores usando la webcam con las siguientes características:
- Presionar ESPACIO para detectar color
- Historial de aciertos y errores
- Triple clic en ESPACIO para grabar audio de 10 segundos
- Generación de reporte en formato 9:16 para Instagram
"""

import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import datetime
import os
import json
import threading
import time
import sounddevice as sd
import soundfile as sf
from scipy.io import wavfile
import wave

class DetectorColores:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Colores - Academia Cortex")
        self.root.geometry("1200x700")

        # Variables de control
        self.cap = None
        self.running = False
        self.historial = []
        self.imagenes_guardadas = []

        # Control de triple clic
        self.click_times = []
        self.grabando_audio = False
        self.audio_data = []

        # Colores predefinidos (en HSV)
        self.colores_conocidos = {
            'Rojo': {'hsv_min': np.array([0, 100, 100]), 'hsv_max': np.array([10, 255, 255])},
            'Rojo2': {'hsv_min': np.array([170, 100, 100]), 'hsv_max': np.array([180, 255, 255])},
            'Naranja': {'hsv_min': np.array([10, 100, 100]), 'hsv_max': np.array([25, 255, 255])},
            'Amarillo': {'hsv_min': np.array([25, 100, 100]), 'hsv_max': np.array([35, 255, 255])},
            'Verde': {'hsv_min': np.array([35, 100, 100]), 'hsv_max': np.array([85, 255, 255])},
            'Cian': {'hsv_min': np.array([85, 100, 100]), 'hsv_max': np.array([95, 255, 255])},
            'Azul': {'hsv_min': np.array([95, 100, 100]), 'hsv_max': np.array([130, 255, 255])},
            'Violeta': {'hsv_min': np.array([130, 100, 100]), 'hsv_max': np.array([170, 255, 255])},
            'Blanco': {'hsv_min': np.array([0, 0, 200]), 'hsv_max': np.array([180, 30, 255])},
            'Negro': {'hsv_min': np.array([0, 0, 0]), 'hsv_max': np.array([180, 255, 50])},
            'Gris': {'hsv_min': np.array([0, 0, 50]), 'hsv_max': np.array([180, 30, 200])},
        }

        # Crear carpetas necesarias
        os.makedirs('capturas', exist_ok=True)
        os.makedirs('audios', exist_ok=True)
        os.makedirs('reportes', exist_ok=True)

        self.crear_interfaz()
        self.iniciar_camara()

    def crear_interfaz(self):
        """Crea la interfaz gráfica"""
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame izquierdo (video)
        left_frame = tk.Frame(main_frame, bg='#2b2b2b')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Título
        titulo = tk.Label(left_frame, text="Academia Cortex - Detector de Colores",
                         font=('Arial', 18, 'bold'), bg='#2b2b2b', fg='white')
        titulo.pack(pady=10)

        # Canvas para video
        self.video_canvas = tk.Label(left_frame, bg='black')
        self.video_canvas.pack(pady=10)

        # Frame de controles
        control_frame = tk.Frame(left_frame, bg='#2b2b2b')
        control_frame.pack(pady=10)

        # Etiqueta de instrucciones
        instrucciones = tk.Label(control_frame,
                                text="ESPACIO: Detectar color | ESPACIO x3: Grabar audio 10s | Q: Salir",
                                font=('Arial', 12), bg='#2b2b2b', fg='#00ff00')
        instrucciones.pack(pady=5)

        # Label para mostrar color detectado
        self.label_color = tk.Label(control_frame, text="Color detectado: -",
                                   font=('Arial', 14, 'bold'), bg='#2b2b2b', fg='white')
        self.label_color.pack(pady=5)

        # Label para estado de grabación
        self.label_grabacion = tk.Label(control_frame, text="",
                                       font=('Arial', 12), bg='#2b2b2b', fg='red')
        self.label_grabacion.pack(pady=5)

        # Frame derecho (historial)
        right_frame = tk.Frame(main_frame, bg='#3b3b3b', width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)

        # Título historial
        titulo_historial = tk.Label(right_frame, text="Historial",
                                    font=('Arial', 16, 'bold'), bg='#3b3b3b', fg='white')
        titulo_historial.pack(pady=10)

        # Estadísticas
        self.label_stats = tk.Label(right_frame, text="Aciertos: 0 | Errores: 0",
                                   font=('Arial', 12), bg='#3b3b3b', fg='white')
        self.label_stats.pack(pady=5)

        # Lista de historial con scrollbar
        scroll_frame = tk.Frame(right_frame, bg='#3b3b3b')
        scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.historial_listbox = tk.Listbox(scroll_frame, yscrollcommand=scrollbar.set,
                                            bg='#2b2b2b', fg='white', font=('Arial', 10),
                                            selectbackground='#555555')
        self.historial_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.historial_listbox.yview)

        # Botón para generar reporte
        btn_reporte = tk.Button(right_frame, text="Generar Reporte Instagram",
                               command=self.generar_reporte, bg='#FF1493', fg='white',
                               font=('Arial', 12, 'bold'), pady=10)
        btn_reporte.pack(pady=10, padx=10, fill=tk.X)

    def iniciar_camara(self):
        """Inicia la captura de video"""
        self.cap = cv2.VideoCapture(0)
        # Configurar resolución de la cámara para mejor rendimiento
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Configurar exposición y brillo para mejor detección
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)

        self.running = True
        self.actualizar_video()

        # Bind de teclas
        self.root.bind('<space>', self.on_space_press)
        self.root.bind('q', lambda e: self.cerrar())

    def actualizar_video(self):
        """Actualiza el frame del video"""
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                # Aplicar mejoras de imagen para mejor detección
                frame = cv2.flip(frame, 1)  # Espejo

                # Aplicar filtro bilateral para suavizar manteniendo bordes
                frame = cv2.bilateralFilter(frame, 9, 75, 75)

                # Dibujar círculo en el centro para indicar área de detección
                h, w = frame.shape[:2]
                center = (w // 2, h // 2)
                radius = 50
                cv2.circle(frame, center, radius, (0, 255, 0), 2)
                cv2.circle(frame, center, 3, (0, 255, 0), -1)

                # Convertir a formato para tkinter
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                img_tk = ImageTk.PhotoImage(image=img)

                self.video_canvas.img_tk = img_tk
                self.video_canvas.configure(image=img_tk)

                # Guardar frame actual para detección
                self.frame_actual = frame

            self.root.after(10, self.actualizar_video)

    def on_space_press(self, event):
        """Maneja el evento de presionar la barra espaciadora"""
        current_time = time.time()
        self.click_times.append(current_time)

        # Mantener solo los últimos 3 clics en los últimos 2 segundos
        self.click_times = [t for t in self.click_times if current_time - t < 2.0]

        if len(self.click_times) >= 3:
            # Triple clic detectado
            self.click_times = []
            self.iniciar_grabacion_audio()
        else:
            # Clic simple - detectar color
            self.detectar_color()

    def detectar_color(self):
        """Detecta el color en el centro de la imagen"""
        if not hasattr(self, 'frame_actual'):
            return

        frame = self.frame_actual.copy()
        h, w = frame.shape[:2]

        # Extraer región central
        center_x, center_y = w // 2, h // 2
        roi_size = 50
        roi = frame[center_y-roi_size:center_y+roi_size,
                   center_x-roi_size:center_x+roi_size]

        # Convertir a HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # Calcular color promedio en la ROI
        color_promedio = cv2.mean(hsv)[:3]

        # Encontrar el color más cercano
        color_detectado = self.identificar_color(hsv)

        # Mostrar en interfaz
        self.label_color.config(text=f"Color detectado: {color_detectado}")

        # Preguntar si es correcto
        self.root.after(100, lambda: self.validar_deteccion(color_detectado, frame))

    def identificar_color(self, hsv_roi):
        """Identifica el color basándose en los rangos HSV"""
        max_pixels = 0
        color_identificado = "Desconocido"

        for nombre_color, rangos in self.colores_conocidos.items():
            if nombre_color == 'Rojo2':  # Caso especial del rojo
                continue

            mask = cv2.inRange(hsv_roi, rangos['hsv_min'], rangos['hsv_max'])

            # Para rojo, combinar ambos rangos
            if nombre_color == 'Rojo':
                mask2 = cv2.inRange(hsv_roi, self.colores_conocidos['Rojo2']['hsv_min'],
                                   self.colores_conocidos['Rojo2']['hsv_max'])
                mask = cv2.bitwise_or(mask, mask2)

            pixels = cv2.countNonZero(mask)

            if pixels > max_pixels:
                max_pixels = pixels
                color_identificado = nombre_color

        # Si no se detectó suficiente coincidencia, es desconocido
        if max_pixels < 100:
            color_identificado = "Desconocido"

        return color_identificado

    def validar_deteccion(self, color_detectado, frame):
        """Pregunta al usuario si la detección fue correcta"""
        respuesta = messagebox.askyesno("Validación",
                                        f"¿El color detectado '{color_detectado}' es correcto?")

        # Guardar imagen en baja resolución
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        thumbnail = cv2.resize(frame, (160, 120))
        filename = f"capturas/captura_{timestamp}.jpg"
        cv2.imwrite(filename, thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 70])

        # Registrar en historial
        resultado = "ACIERTO" if respuesta else "ERROR"
        entrada = {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'color_detectado': color_detectado,
            'resultado': resultado,
            'imagen': filename
        }

        self.historial.append(entrada)
        self.imagenes_guardadas.append(filename)

        # Actualizar interfaz
        color_texto = "green" if respuesta else "red"
        texto = f"[{entrada['timestamp']}] {color_detectado} - {resultado}"
        self.historial_listbox.insert(0, texto)
        self.historial_listbox.itemconfig(0, fg=color_texto)

        self.actualizar_estadisticas()

        # Guardar historial en JSON
        self.guardar_historial()

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas en la interfaz"""
        aciertos = sum(1 for h in self.historial if h['resultado'] == 'ACIERTO')
        errores = sum(1 for h in self.historial if h['resultado'] == 'ERROR')
        self.label_stats.config(text=f"Aciertos: {aciertos} | Errores: {errores}")

    def guardar_historial(self):
        """Guarda el historial en un archivo JSON"""
        with open('historial.json', 'w', encoding='utf-8') as f:
            json.dump(self.historial, f, indent=2, ensure_ascii=False)

    def iniciar_grabacion_audio(self):
        """Inicia la grabación de audio de 10 segundos"""
        if self.grabando_audio:
            return

        self.grabando_audio = True
        self.label_grabacion.config(text="🔴 GRABANDO AUDIO (10s)...")

        # Reproducir sonido de inicio (beep)
        self.reproducir_beep(440, 0.2)  # 440 Hz, 0.2 segundos

        # Iniciar grabación en thread separado
        thread = threading.Thread(target=self.grabar_audio)
        thread.daemon = True
        thread.start()

    def reproducir_beep(self, frecuencia, duracion):
        """Reproduce un tono beep"""
        try:
            sample_rate = 44100
            t = np.linspace(0, duracion, int(sample_rate * duracion))
            wave_data = 0.3 * np.sin(2 * np.pi * frecuencia * t)
            sd.play(wave_data, sample_rate)
            sd.wait()
        except Exception as e:
            print(f"Error al reproducir beep: {e}")

    def grabar_audio(self):
        """Graba audio durante 10 segundos"""
        try:
            sample_rate = 44100
            duracion = 10

            print("Grabando audio...")
            audio_data = sd.rec(int(duracion * sample_rate),
                              samplerate=sample_rate,
                              channels=1,
                              dtype='float32')
            sd.wait()

            # Guardar audio
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audios/audio_{timestamp}.wav"
            sf.write(filename, audio_data, sample_rate)

            print(f"Audio guardado: {filename}")

            # Reproducir sonido de fin
            self.reproducir_beep(880, 0.2)  # 880 Hz, 0.2 segundos

            self.root.after(0, self.finalizar_grabacion_audio)

        except Exception as e:
            print(f"Error al grabar audio: {e}")
            self.root.after(0, self.finalizar_grabacion_audio)

    def finalizar_grabacion_audio(self):
        """Finaliza la grabación de audio"""
        self.grabando_audio = False
        self.label_grabacion.config(text="✓ Audio guardado")
        self.root.after(2000, lambda: self.label_grabacion.config(text=""))

    def generar_reporte(self):
        """Genera el reporte en formato 9:16 para Instagram"""
        if not self.historial:
            messagebox.showwarning("Sin datos", "No hay datos en el historial para generar reporte.")
            return

        self.label_grabacion.config(text="Generando reporte...")
        thread = threading.Thread(target=self._generar_reporte_thread)
        thread.daemon = True
        thread.start()

    def _generar_reporte_thread(self):
        """Genera el reporte en un thread separado"""
        try:
            # Dimensiones 9:16 (Instagram Stories/Reels)
            width, height = 1080, 1920

            # Crear imagen base
            img = Image.new('RGB', (width, height), color='#1a1a1a')
            draw = ImageDraw.Draw(img)

            # Intentar cargar fuente
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
                font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
                font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)
            except:
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()
                font_text = ImageFont.load_default()

            # Título
            draw.text((width//2, 100), "ACADEMIA CORTEX", fill='white',
                     font=font_title, anchor='mm')

            # Línea decorativa
            draw.rectangle([100, 180, width-100, 190], fill='#FF1493')

            # Estadísticas
            aciertos = sum(1 for h in self.historial if h['resultado'] == 'ACIERTO')
            errores = sum(1 for h in self.historial if h['resultado'] == 'ERROR')
            total = len(self.historial)

            y_pos = 250
            draw.text((width//2, y_pos), "ESTADÍSTICAS", fill='white',
                     font=font_subtitle, anchor='mm')

            y_pos += 80
            draw.text((width//2, y_pos), f"Total de detecciones: {total}",
                     fill='white', font=font_text, anchor='mm')

            y_pos += 60
            draw.text((width//2, y_pos), f"Aciertos: {aciertos} ({aciertos*100//total if total > 0 else 0}%)",
                     fill='#00ff00', font=font_text, anchor='mm')

            y_pos += 60
            draw.text((width//2, y_pos), f"Errores: {errores} ({errores*100//total if total > 0 else 0}%)",
                     fill='#ff0000', font=font_text, anchor='mm')

            # Miniaturas de imágenes
            y_pos += 100
            draw.text((width//2, y_pos), "ÚLTIMAS DETECCIONES",
                     fill='white', font=font_subtitle, anchor='mm')

            y_pos += 80

            # Mostrar últimas 12 imágenes en grid 3x4
            imagenes_recientes = self.imagenes_guardadas[-12:]
            thumb_width, thumb_height = 240, 180
            padding = 30
            cols = 3

            x_start = (width - (cols * thumb_width + (cols-1) * padding)) // 2

            for idx, img_path in enumerate(imagenes_recientes):
                if os.path.exists(img_path):
                    row = idx // cols
                    col = idx % cols

                    x = x_start + col * (thumb_width + padding)
                    y = y_pos + row * (thumb_height + padding)

                    try:
                        thumb = Image.open(img_path)
                        thumb = thumb.resize((thumb_width, thumb_height))
                        img.paste(thumb, (x, y))

                        # Borde según resultado
                        entrada = self.historial[-(len(imagenes_recientes)-idx)]
                        border_color = '#00ff00' if entrada['resultado'] == 'ACIERTO' else '#ff0000'
                        draw.rectangle([x-2, y-2, x+thumb_width+2, y+thumb_height+2],
                                     outline=border_color, width=4)
                    except Exception as e:
                        print(f"Error al cargar imagen {img_path}: {e}")

            # Pie de página
            y_footer = height - 150
            draw.rectangle([100, y_footer-20, width-100, y_footer-10], fill='#FF1493')

            timestamp = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            draw.text((width//2, y_footer+30), f"Generado: {timestamp}",
                     fill='#888888', font=font_text, anchor='mm')

            # Guardar reporte
            timestamp_file = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reportes/reporte_instagram_{timestamp_file}.jpg"
            img.save(filename, quality=95)

            print(f"Reporte generado: {filename}")

            # Notificar en interfaz
            self.root.after(0, lambda: self.label_grabacion.config(text=f"✓ Reporte guardado: {filename}"))
            self.root.after(0, lambda: messagebox.showinfo("Reporte generado",
                                                           f"Reporte guardado en:\n{filename}"))
            self.root.after(3000, lambda: self.label_grabacion.config(text=""))

        except Exception as e:
            print(f"Error al generar reporte: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error",
                                                            f"Error al generar reporte: {e}"))
            self.root.after(0, lambda: self.label_grabacion.config(text=""))

    def cerrar(self):
        """Cierra la aplicación"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.quit()

def main():
    root = tk.Tk()
    app = DetectorColores(root)
    root.protocol("WM_DELETE_WINDOW", app.cerrar)
    root.mainloop()

if __name__ == "__main__":
    main()

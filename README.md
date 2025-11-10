# Detector de Colores con Webcam - Academia Cortex

Programa interactivo para detectar colores usando la webcam con funcionalidades avanzadas de grabación de audio y generación de reportes para Instagram.

## 🚀 Inicio Rápido (Sin Instalación)

### ✨ Versión Web - ¡Usa directamente desde tu navegador!

**La forma más fácil de usar el programa:**

1. **Abre el archivo `index.html`** en tu navegador
   - Descarga el archivo y haz doble clic, o
   - Usa GitHub Pages (si está habilitado)

2. **Permite el acceso a la webcam** cuando te lo pida

3. **¡Listo!** Ya puedes detectar colores

📖 **[Ver instrucciones detalladas](COMO_USAR.md)**

---

## 💻 Versión Python (Avanzada)

Si prefieres la versión de escritorio con Python, ve a la sección [Instalación](#instalación) más abajo.

---

## Características

- **Detección de colores en tiempo real** con alta sensibilidad
- **Historial de aciertos y errores** con estadísticas detalladas
- **Captura automática de imágenes** en baja resolución para cada detección
- **Grabación de audio** de 10 segundos mediante triple clic en la barra espaciadora
- **Sonidos de inicio y fin** para la grabación de audio
- **Generación de reportes** en formato 9:16 optimizado para Instagram Stories/Reels
- **Interfaz gráfica intuitiva** con visualización en tiempo real

## Colores Detectables

El programa puede detectar los siguientes colores:
- Rojo
- Naranja
- Amarillo
- Verde
- Cian
- Azul
- Violeta
- Blanco
- Negro
- Gris

## Requisitos del Sistema

- Python 3.8 o superior
- Webcam conectada
- Micrófono (para la función de grabación de audio)
- Sistema operativo: Windows, macOS o Linux

## Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone <url-del-repositorio>
cd Cartulinas
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar instalación de dependencias del sistema

**En Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3-tk libportaudio2 portaudio19-dev
```

**En macOS:**
```bash
brew install portaudio
```

**En Windows:**
Las dependencias generalmente se instalan automáticamente con pip.

## Uso

### Iniciar el programa

```bash
python detector_colores.py
```

### Controles

- **BARRA ESPACIADORA**: Detectar el color frente a la webcam
- **BARRA ESPACIADORA x3** (triple clic rápido): Iniciar grabación de audio de 10 segundos
- **Q**: Salir del programa

### Flujo de trabajo

1. **Iniciar el programa**: Se abrirá una ventana con la vista de la webcam
2. **Posicionar el color**: Coloca el objeto de color frente a la webcam, centrándolo en el círculo verde
3. **Detectar color**: Presiona la BARRA ESPACIADORA
4. **Validar**: Responde si la detección fue correcta (Sí/No)
5. **Ver historial**: El resultado se registra automáticamente en el panel derecho
6. **Grabar audio** (opcional): Presiona la BARRA ESPACIADORA 3 veces rápidamente
7. **Generar reporte**: Haz clic en "Generar Reporte Instagram" cuando quieras crear el resumen

## Estructura de Archivos Generados

```
Cartulinas/
├── capturas/           # Imágenes en miniatura de cada detección
├── audios/            # Grabaciones de audio en formato WAV
├── reportes/          # Reportes generados en formato 9:16 para Instagram
├── historial.json     # Historial de detecciones en formato JSON
└── detector_colores.py
```

## Características Técnicas

### Detección de Colores
- Usa espacio de color HSV para mayor precisión
- Filtro bilateral para suavizar ruido manteniendo bordes
- ROI (Region of Interest) de 100x100 píxeles en el centro
- Algoritmo de conteo de píxeles para identificar el color dominante

### Captura de Imágenes
- Resolución: 160x120 píxeles
- Formato: JPEG con calidad del 70%
- Almacenamiento automático con timestamp

### Grabación de Audio
- Duración: 10 segundos
- Formato: WAV
- Sample rate: 44100 Hz
- Canales: Mono
- Sonidos de beep: 440 Hz (inicio) y 880 Hz (fin)

### Reporte Instagram
- Formato: 1080x1920 píxeles (9:16)
- Incluye:
  - Encabezado "ACADEMIA CORTEX"
  - Estadísticas de aciertos y errores
  - Grid de últimas 12 detecciones (3x4)
  - Bordes verdes (aciertos) y rojos (errores)
  - Timestamp de generación

## Solución de Problemas

### La webcam no se inicia
- Verifica que la webcam esté conectada correctamente
- Cierra otras aplicaciones que puedan estar usando la webcam
- Prueba cambiar `cv2.VideoCapture(0)` por `cv2.VideoCapture(1)` en el código

### Error de audio
- Verifica que el micrófono esté conectado y habilitado
- En Linux, instala: `sudo apt-get install portaudio19-dev`
- En macOS, instala: `brew install portaudio`

### Detección de colores inexacta
- Mejora la iluminación del entorno
- Asegúrate de que el objeto esté bien centrado
- Evita fondos con colores similares al objeto
- Ajusta los rangos HSV en el código si es necesario

### No se genera el reporte
- Verifica que haya al menos una detección en el historial
- Comprueba los permisos de escritura en la carpeta `reportes/`
- Asegúrate de tener las fuentes DejaVu instaladas (Linux)

## Personalización

### Modificar colores detectables

Edita el diccionario `self.colores_conocidos` en `detector_colores.py`:

```python
self.colores_conocidos = {
    'Rojo': {'hsv_min': np.array([0, 100, 100]), 'hsv_max': np.array([10, 255, 255])},
    # Agregar más colores...
}
```

### Cambiar duración de grabación de audio

Modifica la variable `duracion` en el método `grabar_audio()`:

```python
duracion = 10  # Cambiar a los segundos deseados
```

### Ajustar tamaño de ROI

Modifica la variable `roi_size` en el método `detectar_color()`:

```python
roi_size = 50  # Cambiar al tamaño deseado en píxeles
```

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz un fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Autor

**Academia Cortex**

## Contacto

Para preguntas, sugerencias o reportar problemas, por favor abre un issue en el repositorio.

---

**¡Disfruta detectando colores y compartiendo tus estadísticas en Instagram!** 📸🎨

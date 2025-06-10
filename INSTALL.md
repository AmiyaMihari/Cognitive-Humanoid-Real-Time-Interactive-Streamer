# Guía de Instalación y Configuración de C.H.R.I.S.

## Requisitos previos

- **Sistema operativo:** Windows o Linux
- **Python:** 3.10 o superior
- **Git:** Instalado y configurado
- **VTube Studio:** Instalar desde [Steam](https://store.steampowered.com/app/1325860/VTube_Studio/)  
  (Necesario para la integración en tiempo real con el avatar VTuber)
- Se recomienda conexión a internet para instalar dependencias

## Clonar el repositorio

```bash
git clone https://github.com/AmiyaMihari/Cognitive-Humanoid-Real-Time-Interactive-Streamer.git
cd Cognitive-Humanoid-Real-Time-Interactive-Streamer
```

## Crear un entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## Instalar dependencias

Asegúrate de estar en el directorio raíz del proyecto y con el entorno virtual activado.

```bash
pip install -r requirements.txt
```

## Configurar el entorno

1. Renombra el archivo `.env.example` a `.env` si existe.
2. Completa las variables necesarias en el archivo `.env` (por ejemplo, claves de API para Twitch, configuración de Vtube Studio, etc.).  
   Si el archivo no existe, créalo según las instrucciones de la documentación o los módulos que desees utilizar.

## Ejecutar el proyecto

Este proyecto se encuentra en etapa de planeación/prototipo y la ejecución puede variar.  
Si existe un archivo principal (por ejemplo, `main.py`), puedes ejecutarlo así:

```bash
python main.py
```

Revisa la documentación o los archivos de cada módulo para instrucciones específicas.

## Problemas comunes

- **No se reconoce el comando `python`:**  
  Prueba usar `python3` en su lugar.
- **Faltan dependencias:**  
  Verifica que ejecutaste `pip install -r requirements.txt` con el entorno virtual activo.
- **Error de variables de entorno o claves:**  
  Asegúrate de tener el archivo `.env` correctamente configurado.
- **Problemas de permisos en Linux:**  
  Usa `chmod +x script.sh` si algún script requiere permisos de ejecución.
- **VTube Studio no detectado:**  
  Verifica que VTube Studio está instalado y ejecutándose desde Steam antes de iniciar la integración.

## Soporte

Para dudas, problemas o sugerencias:
- Abre un [Issue](https://github.com/AmiyaMihari/Cognitive-Humanoid-Real-Time-Interactive-Streamer/issues) en el repositorio
- Contacta directamente a [AmiyaMihari](https://github.com/AmiyaMihari)

¡Gracias por utilizar y contribuir a C.H.R.I.S.!
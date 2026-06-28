# Guía de Instalación y Configuración de C.H.R.I.S.

La instalación está automatizada: un solo script instala **todo** (el gestor
`uv`, Python 3.12, el entorno virtual y todas las dependencias). Tú solo tienes
que poner tu token. Funciona en **Linux, macOS y Windows**.

## Requisitos previos

- **Sistema operativo:** Linux, macOS o Windows
- **Git:** instalado y configurado
- **GPU NVIDIA** (opcional, recomendada): acelera la transcripción de voz. Sin
  ella, el sistema funciona igual en CPU (un poco más lento).
- Conexión a internet (para descargar dependencias y modelos la primera vez)

> **No necesitas instalar Python tú mismo.** El script instala la versión exacta
> (3.12) de forma aislada, sin tocar el Python del sistema.

## 1. Clonar el repositorio

```bash
git clone https://github.com/AmiyaMihari/Cognitive-Humanoid-Real-Time-Interactive-Streamer.git
cd Cognitive-Humanoid-Real-Time-Interactive-Streamer
```

## 2. Instalación automática (recomendada)

**Linux / macOS:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
- La forma más fácil: **doble clic en `setup.bat`** (abre todo solo).
- O desde PowerShell:
  ```powershell
  ./setup.ps1
  ```
  > Si Windows bloquea la ejecución del script, córrelo una vez así:
  > `powershell -ExecutionPolicy Bypass -File .\setup.ps1`

El script instala `uv`, Python 3.12, crea el entorno virtual (`venv`), instala
todas las dependencias y crea tu archivo `.env` a partir de la plantilla.

## 3. Configurar tu token

Abre el archivo **`.env`** (lo creó el script) y completa tu clave:

```ini
OPENAI_API_KEY=sk-...   # requerido: el módulo "mind" lo usa para responder
HF_TOKEN=               # opcional: el modelo de voz es público, déjalo vacío
```

El archivo `.env` está en `.gitignore`, así que tu token nunca se sube al
repositorio.

## 4. Ejecutar el proyecto

Activa el entorno y lanza la app de demostración:

**Linux / macOS:**
```bash
source venv/bin/activate
streamlit run app.py
```

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
streamlit run app.py
```

La primera ejecución descarga los modelos de voz (≈3.3 GB) y los guarda en caché;
las siguientes arrancan en segundos.

> En Linux, el script instala un hook que **activa el entorno automáticamente**
> al entrar a la carpeta del proyecto (para **bash** vía `~/.bashrc` y para
> **fish** vía `conf.d`), así que puedes saltarte el paso de
> `source venv/bin/activate`.

## Actualizar tras cambios (`git pull`)

Las librerías **no se suben a GitHub** (el `venv/` está en `.gitignore`). Lo que
viaja en el repo es **`requirements.txt`**: la lista de dependencias. Así que,
cuando hagas `git pull` y alguien (o tú mismo desde otra máquina) haya añadido
una librería nueva, vuelves a sincronizar tu venv con un comando:

```bash
git pull

# La forma simple: volver a correr el script (es idempotente, solo instala lo nuevo)
./setup.sh                 # en Windows: setup.bat  (o ./setup.ps1)

# O directamente, si prefieres:
uv pip install --python venv/bin/python -r requirements.txt   # venv\Scripts\python.exe en Windows
```

> Para un espejo **exacto** (que además desinstale lo que se haya quitado de
> `requirements.txt`), usa `uv pip sync requirements.txt` en lugar de `install`.

### Cuando TÚ añades una librería nueva

Para que el cambio llegue a las otras máquinas, tiene que quedar en
`requirements.txt`:

```bash
uv pip install --python venv/bin/python <libreria>   # 1. instálala en tu venv
# 2. añade su línea (con versión) a requirements.txt
git add requirements.txt && git commit -m "deps: add <libreria>" && git push
```

## Instalación manual (alternativa)

Si prefieres no usar el script, instala [`uv`](https://docs.astral.sh/uv/) y:

```bash
uv python install 3.12
uv venv venv --python 3.12
uv pip install --python venv/bin/python -r requirements.txt   # venv\Scripts\python.exe en Windows
cp .env.example .env        # Copy-Item .env.example .env  en Windows
```

## Problemas comunes

- **El script no se ejecuta en Windows:**
  Usa `powershell -ExecutionPolicy Bypass -File .\setup.ps1`.
- **`uv: command not found` tras instalarlo:**
  Abre una terminal nueva (el instalador agrega `uv` al `PATH`) o vuelve a correr
  el script.
- **Error de autenticación al responder:**
  Falta o es inválida la `OPENAI_API_KEY` en `.env`.
- **La transcripción corre en CPU en vez de GPU:**
  Verifica `nvidia-smi`. El sistema cae a CPU automáticamente si CUDA no
  inicializa; consulta `docs/reference/senses/sense_ear/cuda.md`.
- **Problemas de permisos en Linux:**
  Usa `chmod +x setup.sh` antes de ejecutarlo.

## Soporte

Para dudas, problemas o sugerencias:
- Abre un [Issue](https://github.com/AmiyaMihari/Cognitive-Humanoid-Real-Time-Interactive-Streamer/issues) en el repositorio
- Contacta directamente a [AmiyaMihari](https://github.com/AmiyaMihari)

¡Gracias por utilizar y contribuir a C.H.R.I.S.!

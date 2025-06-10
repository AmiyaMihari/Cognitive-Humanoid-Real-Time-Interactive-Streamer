# Guía de Contribución a C.H.R.I.S.

¡Gracias por tu interés en contribuir a Cognitive Humanoid Real-Time Interactive Streamer (C.H.R.I.S.)! Todas las contribuciones son bienvenidas, excepto las relacionadas con el núcleo del proyecto (gestión del modelo de lenguaje y sus parámetros), ya que esas áreas son exclusivas de los administradores.

---

## ¿Qué contribuciones son bienvenidas?

- Mejoras a los módulos de Text to Speech, Speech to Text, visión artificial, integración con VTube Studio, Twitch, Minecraft, etc.
- Corrección de errores y mejoras de rendimiento.
- Mejoras en la documentación, ejemplos y tutoriales.
- Nuevas funcionalidades, siempre fuera de la gestión directa del LLM y sus parámetros.

**Nota:** Las contribuciones al núcleo de gestión del LLM (modelo de lenguaje y sus parámetros) sólo pueden ser realizadas por administradores. Sin embargo, se tomarán sugerencias dadas por la comunidad respecto a los modelos y parámetros a usar.

---

## Requisitos

- Sistema operativo: Windows o Linux
- Python 3.10 o superior
- `git`
- Recomendado: crear un entorno virtual (`venv`)

---

## ¿Cómo clonar y configurar el proyecto?

```bash
# Clona el repositorio
git clone https://github.com/AmiyaMihari/Cognitive-Humanoid-Real-Time-Interactive-Streamer.git

cd Cognitive-Humanoid-Real-Time-Interactive-Streamer

# Crea un entorno virtual (opcional pero recomendado)
python -m venv venv
# Activa el entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate

# Instala las dependencias
pip install -r requirements.txt
```

---

## Convenciones de código

- Todo el código debe estar en Python.
- Usa tipado estático donde sea posible.
- Sigue la guía de estilo [PEP8](https://peps.python.org/pep-0008/).
- Incluye docstrings en funciones y clases.
- Escribe comentarios claros y útiles.
- Nombra tus variables y funciones de forma descriptiva.
- Se recomienda usar herramientas como `black` y `flake8` para el formateo y linting.

---

## Formato de commits

Este proyecto utiliza [Conventional Commits](https://www.conventionalcommits.org/).

```
<tipo>[alcance opcional]: <descripción breve>
```

**Tipos más usados:**
- feat: Nueva funcionalidad
- fix: Corrección de bug
- docs: Cambios en la documentación
- style: Cambios de formato (sin afectar la lógica del código)
- refactor: Refactorización
- test: Agrega o corrige pruebas
- chore: Tareas de mantenimiento

**Ejemplo:**
```
feat(TTS): añade soporte para voces personalizadas
fix(STT): corrige error de reconocimiento en ambientes ruidosos
docs: añade instrucciones de instalación en el README
```

---

## ¿Cómo abrir un Issue o Pull Request?

### Issues

- Ve a la pestaña "Issues" del repositorio.
- Crea un nuevo Issue.
- Describe el problema, mejora o propuesta de la forma más clara y detallada posible.
- Adjunta logs, capturas o ejemplos si aplica.

### Pull Requests

1. Haz un fork del repositorio y crea una rama descriptiva para tu contribución.
2. Realiza tus cambios siguiendo las convenciones de código y formato de commits.
3. Antes de enviar, verifica que el proyecto sigue funcionando y que las pruebas pasan.
4. Abre el Pull Request hacia la rama principal (`main`) desde tu fork.
5. Describe claramente los cambios realizados.
6. Espera revisión de los administradores.

---

## Pruebas

- Incluye pruebas para cualquier funcionalidad nueva o corrección.
- Las pruebas deben estar en la carpeta `tests/` y seguir la convención de nombres `test_<modulo>.py`.
- Se recomienda usar [pytest](https://docs.pytest.org/).
- Antes de enviar un Pull Request, ejecuta todas las pruebas con:
  ```bash
  pytest
  ```

---

¿Tienes dudas? Contacta a [AmiyaMihari](https://github.com/AmiyaMihari) en GitHub.

¡Gracias por contribuir!
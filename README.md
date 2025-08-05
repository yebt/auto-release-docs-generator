# Generador de Changelogs y Listado de Vídeos con OpenAI Responses API

Este script automatiza la generación de dos tipos de changelogs (comercial y técnico) y de un listado de vídeos para tutoriales, a partir del historial de commits entre dos etiquetas Git. Utiliza la API de Responses de OpenAI y muestra indicadores de progreso (spinners) mediante la librería Halo.

---

## 🛠️ Requisitos

- Python 3.8 o superior
- Git
- Una cuenta de OpenAI con acceso a la API de Responses
- Las siguientes librerías de Python:
  - `python-dotenv`
  - `openai` (cliente oficial)
  - `halo`

---

## 📦 Instalación

1. **Clona este repositorio**

   ```bash
   git clone https://tu-repo.git
   cd tu-repo
   ```


2. **Crea un entorno virtual**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instala dependencias**

   ```bash
   pip install -r requirements.txt
   ```

   > **requirements.txt**
   >
   > ```text
   > python-dotenv
   > openai
   > halo
   > ```

---

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```dotenv
OPENAI_API_KEY=tu_api_key_de_openai
OUTPUT_DIR=/ruta/al/directorio/de/salidas
```

* `OPENAI_API_KEY`: clave secreta de tu cuenta OpenAI.
* `OUTPUT_DIR`: ruta donde se crearán las carpetas de cada release.

---

## 🚀 Uso

```bash
./generate_release.py \
  --repo-dir /ruta/a/tu/repo \
  --branch main \
  --from-tag 3.4.2 \
  --to-tag   3.5.1
```

* `--repo-dir` : Ruta del repositorio Git.
* `--branch`   : Nombre de la rama (p. ej. `main`).
* `--from-tag` : Tag inicial (p. ej. `3.4.2`).
* `--to-tag`   : Tag final (p. ej. `3.5.1`).

Al ejecutarse, el script:

1. Carga la configuración y valida que existan `OPENAI_API_KEY` y `OUTPUT_DIR`.
2. Cambia al directorio del repositorio.
3. Obtiene el Git log entre los dos tags en la rama indicada.
4. Crea una carpeta de release en `OUTPUT_DIR`, llamada `release_<to-tag>_<timestamp>`.
5. Genera:

   * `CHANGELOG_comercial.md` (resumen accesible para el área comercial).
   * `CHANGELOG_tecnico.md`   (detallado para el equipo técnico).
   * `Listado_videos.md`      (sugerencias de vídeos/tutoriales).
6. Muestra mensajes de éxito o fallo con spinners de Halo.

---

## 📁 Estructura de Salida

Dentro de `OUTPUT_DIR` encontrarás:

```
/ruta/de/salidas/
└── release_3.5.1_20250805_143210/
    ├── CHANGELOG_comercial.md
    ├── CHANGELOG_tecnico.md
    └── Listado_videos.md
```

* **CHANGELOG\_comercial.md**: Puntos clave para el equipo de ventas.
* **CHANGELOG\_tecnico.md**: Detalles de cada commit y su impacto técnico.
* **Listado\_videos.md**: Lista de vídeos sugeridos para tutoriales.

---

## 📝 Ejemplo de CHANGELOG\_comercial.md

```markdown
# Changelog Comercial (v3.4.2 → v3.5.1)

- **Nueva pasarela de pagos**: Ahora los clientes pueden pagar con tarjetas internacionales sin configuraciones adicionales.
- **Mejoras en el dashboard**: Se han reorganizado los widgets para mostrar métricas clave de un vistazo.
- **Optimización de carga**: Las páginas principales cargan en un 30 % menos de tiempo, mejorando la experiencia de usuario.
```

---

## 🔒 Licencia

Este proyecto está bajo la [MIT License](LICENSE).
¡Contribuciones y feedback bienvenidos!

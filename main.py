#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import datetime

from dotenv import load_dotenv
from openai import OpenAI

def load_config() -> tuple[OpenAI, str]:
    """
    Carga .env y devuelve:
      - Un cliente OpenAI configurado.
      - El directorio base de salida (OUTPUT_DIR).
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: No se encontró OPENAI_API_KEY en las variables de entorno.", file=sys.stderr)
        sys.exit(1)
    output_base = os.getenv("OUTPUT_DIR", "")
    if not output_base:
        print("❌ ERROR: No se encontró OUTPUT_DIR en las variables de entorno.", file=sys.stderr)
        sys.exit(1)
    # Asegurarse de que el directorio base existe
    os.makedirs(output_base, exist_ok=True)
    client = OpenAI(api_key=api_key)
    return client, os.path.abspath(output_base)

def get_git_log(branch: str, from_tag: str, to_tag: str) -> str:
    """Obtiene el git log entre dos tags en la rama especificada."""
    cmd = [
        "git", "log",
        f"{from_tag}..{to_tag}",
        branch,
        "--pretty=format:%h %ad %an%n%s%n%b%n---",
        "--date=short"
    ]
    try:
        return subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al ejecutar git log: {e}", file=sys.stderr)
        sys.exit(1)

def call_openai(client: OpenAI, prompt: str, model: str = "gpt-4o") -> str:
    """
    Llama a la API de Responses y devuelve el texto generado.
    Usa `instructions` para el rol system y `input` para el prompt de usuario.
    """
    resp = client.responses.create(
        model=model,
        instructions="Eres un asistente que genera documentos claros y estructurados.",
        input=prompt
    )
    return resp.output_text

def save_text(folder: str, filename: str, content: str):
    """Guarda contenido en un archivo dentro de la carpeta indicada."""
    path = os.path.join(folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ Generado {path}")

def main():
    parser = argparse.ArgumentParser(
        description="Genera changelogs y listado de vídeos usando Responses API, "
                    "entre dos tags de una rama Git."
    )
    parser.add_argument("--repo-dir", required=True,
                        help="Directorio del repositorio Git")
    parser.add_argument("--branch",   required=True, help="Nombre de la rama (ej. main)")
    parser.add_argument("--from-tag", required=True, help="Tag inicial (ej. 3.4.2)")
    parser.add_argument("--to-tag",   required=True, help="Tag final   (ej. 3.5.1)")
    args = parser.parse_args()

    # Carga configuración y cliente
    client, output_base = load_config()

    # Cambiar al directorio del repositorio
    if not os.path.isdir(args.repo_dir):
        print(f"❌ ERROR: El directorio {args.repo_dir} no existe.", file=sys.stderr)
        sys.exit(1)
    os.chdir(args.repo_dir)
    print(f"ℹ️  Ejecutando en repo: {os.getcwd()}")

    # 1) Obtener git log
    git_log = get_git_log(args.branch, args.from_tag, args.to_tag)

    # 2) Crear carpeta de release dentro del OUTPUT_DIR
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    release_folder = os.path.join(output_base, f"release_{args.to_tag}_{ts}")
    os.makedirs(release_folder, exist_ok=True)

    # 3) Changelog para Comercial
    prompt_comercial = f"""
Toma este git log entre {args.from_tag} y {args.to_tag} en la rama {args.branch}:

{git_log}

Genera un CHANGELOG breve orientado al área COMERCIAL. Incluye:
- Resumen de cada cambio en un lenguaje accesible.
- Puntos clave que el equipo comercial debe saber para comunicar a los clientes.
- No incluyas información técnica innecesaria.
"""
    changelog_com = call_openai(client, prompt_comercial)
    save_text(release_folder, "CHANGELOG_comercial.md", changelog_com)

    # 4) Changelog para Técnico
    prompt_tecnico = f"""
Toma el mismo git log:

{git_log}

Genera un CHANGELOG detallado orientado al EQUIPO TÉCNICO. Incluye:
- Descripción de cada commit.
- Referencias a módulos, archivos o rutas si aplica.
- Impacto técnico de los cambios.
"""
    changelog_tech = call_openai(client, prompt_tecnico)
    save_text(release_folder, "CHANGELOG_tecnico.md", changelog_tech)

    # 5) Listado de Vídeos para Tutoriales
    prompt_videos = f"""
Con base en estos cambios:

{git_log}

Elabora un LISTADO de vídeos necesarios para tutoriales de cliente. Para cada vídeo:
- Título (en español, ej. "Explicación de gestión de reservas")
- Descripción de los módulos y características que se deben explicar.
- Orden sugerido si hay dependencias.
"""
    video_list = call_openai(client, prompt_videos)
    save_text(release_folder, "Listado_videos.md", video_list)

    print(f"\n✅ ¡Listo! Todos los documentos se han guardado en: {release_folder}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
import datetime

from dotenv import load_dotenv
from openai import OpenAI
from halo import Halo

def load_config() -> tuple[OpenAI, str]:
    """
    Carga .env y devuelve:
      - Un cliente OpenAI configurado.
      - El directorio base de salida (OUTPUT_DIR).
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    output_base = os.getenv("OUTPUT_DIR")
    if not api_key:
        print("❌ ERROR: No se encontró OPENAI_API_KEY en las variables de entorno.", file=sys.stderr)
        sys.exit(1)
    if not output_base:
        print("❌ ERROR: No se encontró OUTPUT_DIR en las variables de entorno.", file=sys.stderr)
        sys.exit(1)
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
    return subprocess.check_output(cmd, text=True)

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

def main():
    parser = argparse.ArgumentParser(
        description="Genera changelogs y listado de vídeos usando Responses API, "
                    "entre dos tags de una rama Git, mostrando spinners y alerts con Halo."
    )
    parser.add_argument("--repo-dir", required=True,
                        help="Directorio del repositorio Git")
    parser.add_argument("--branch",   required=True, help="Nombre de la rama (ej. main)")
    parser.add_argument("--from-tag", required=True, help="Tag inicial (ej. 3.4.2)")
    parser.add_argument("--to-tag",   required=True, help="Tag final   (ej. 3.5.1)")
    args = parser.parse_args()

    # Carga configuración y cliente
    spinner = Halo(text="Cargando configuración…", spinner="dots")
    spinner.start()
    try:
        client, output_base = load_config()
        spinner.succeed("Configuración cargada.")
    except Exception as e:
        spinner.fail(f"Error al cargar configuración: {e}")
        sys.exit(1)

    # Cambiar al directorio del repositorio
    spinner = Halo(text=f"Cambiando a {args.repo_dir}…", spinner="dots")
    spinner.start()
    if not os.path.isdir(args.repo_dir):
        spinner.fail(f"El directorio {args.repo_dir} no existe.")
        sys.exit(1)
    os.chdir(args.repo_dir)
    spinner.succeed(f"Repositorio: {os.getcwd()}")

    # 1) Obtener git log
    spinner = Halo(text=f"Obteniendo git log {args.from_tag}..{args.to_tag}…", spinner="dots")
    spinner.start()
    try:
        git_log = get_git_log(args.branch, args.from_tag, args.to_tag)
        spinner.succeed("Git log obtenido.")
    except subprocess.CalledProcessError as e:
        spinner.fail(f"Error al obtener git log: {e}")
        sys.exit(1)

    # 2) Crear carpeta de release dentro del OUTPUT_DIR
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    release_folder = os.path.join(output_base, f"release_{args.to_tag}_{ts}")
    os.makedirs(release_folder, exist_ok=True)

    # 3) Changelog para Comercial
    spinner = Halo(text="Generando CHANGELOG (comercial)…", spinner="dots")
    spinner.start()
    prompt_comercial = f"""
Toma este git log entre {args.from_tag} y {args.to_tag} en la rama {args.branch}:

{git_log}

Genera un CHANGELOG breve orientado al área COMERCIAL. Incluye:
- Resumen de cada cambio en un lenguaje accesible.
- Puntos clave que el equipo comercial debe saber para comunicar a los clientes.
- No incluyas información técnica innecesaria.
"""
    try:
        changelog_com = call_openai(client, prompt_comercial)
        save_text(release_folder, "CHANGELOG_comercial.md", changelog_com)
        spinner.succeed("CHANGELOG comercial generado.")
    except Exception as e:
        spinner.fail(f"Error al generar CHANGELOG comercial: {e}")
        sys.exit(1)

    # 4) Changelog para Técnico
    spinner = Halo(text="Generando CHANGELOG (técnico)…", spinner="dots")
    spinner.start()
    prompt_tecnico = f"""
Toma el mismo git log:

{git_log}

Genera un CHANGELOG detallado orientado al EQUIPO TÉCNICO. Incluye:
- Descripción de cada commit.
- Referencias a módulos, archivos o rutas si aplica.
- Impacto técnico de los cambios.
"""
    try:
        changelog_tech = call_openai(client, prompt_tecnico)
        save_text(release_folder, "CHANGELOG_tecnico.md", changelog_tech)
        spinner.succeed("CHANGELOG técnico generado.")
    except Exception as e:
        spinner.fail(f"Error al generar CHANGELOG técnico: {e}")
        sys.exit(1)

    # 5) Listado de Vídeos para Tutoriales
    spinner = Halo(text="Generando listado de vídeos…", spinner="dots")
    spinner.start()
    prompt_videos = f"""
Con base en estos cambios:

{git_log}

Elabora un LISTADO de vídeos necesarios para tutoriales de cliente. Para cada vídeo:
- Título (en español, ej. "Explicación de gestión de reservas")
- Descripción de los módulos y características que se deben explicar.
- Orden sugerido si hay dependencias.
"""
    try:
        video_list = call_openai(client, prompt_videos)
        save_text(release_folder, "Listado_videos.md", video_list)
        spinner.succeed("Listado de vídeos generado.")
    except Exception as e:
        spinner.fail(f"Error al generar listado de vídeos: {e}")
        sys.exit(1)

    # Fin
    Halo(text="¡Proceso completado!", spinner="success").succeed(f"Documentos guardados en:\n{release_folder}")

if __name__ == "__main__":
    main()


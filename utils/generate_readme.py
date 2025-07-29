import os
from pathlib import Path

EXCLUDE_DIRS = {"__pycache__", "venv", ".git", ".idea", ".vscode", "site-packages", "dist", "build", "node_modules"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}

README_PATH = "README.md"
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # dos niveles arriba (desde utils/)
MAX_DEPTH = 3

def is_excluded(name):
    return name in EXCLUDE_DIRS or name in EXCLUDE_FILES or name.startswith('.')

def get_structure(path, depth=0):
    if depth > MAX_DEPTH:
        return []

    entries = []
    for item in sorted(path.iterdir()):
        if is_excluded(item.name):
            continue

        prefix = "   " * depth
        if item.is_dir():
            entries.append(f"{prefix}- {item.name}/")
            entries.extend(get_structure(item, depth + 1))
        elif item.is_file():
            entries.append(f"{prefix}- {item.name}")
    return entries

def build_readme():
    structure = get_structure(PROJECT_ROOT)
    readme_content = (
        "# Soccer Central Web App\n\n"
        "Este proyecto contiene la nueva plataforma de análisis y scouting de datos futbolísticos.\n"
        "A continuación se detalla la estructura del proyecto:\n\n"
        "```plaintext\n" +
        "\n".join(structure) +
        "\n```\n"
    )
    with open(PROJECT_ROOT / README_PATH, "w") as f:
        f.write(readme_content)
    print(f"README.md actualizado con estructura desde {PROJECT_ROOT}")

if __name__ == "__main__":
    build_readme()

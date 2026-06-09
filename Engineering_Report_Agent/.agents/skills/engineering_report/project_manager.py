import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROJECTS_DIR = ROOT / "projects"


def create_project(slug):
    project_dir = PROJECTS_DIR / slug
    for child in ("raw", "override", "work", "output"):
        (project_dir / child).mkdir(parents=True, exist_ok=True)
    readme = project_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            f"# {slug}\n\n"
            "## 目录说明\n\n"
            "- `raw/`：原始项目资料。\n"
            "- `override/`：人工修正资料。\n"
            "- `work/`：自动上下文和中间文件。\n"
            "- `output/`：最终成果。\n",
            encoding="utf-8",
        )
    print(f"Project initialized: {project_dir}")


def main():
    parser = argparse.ArgumentParser(description="Create isolated engineering report project folders.")
    parser.add_argument("slug", help="Project folder name, for example hg_dongpo_pipe")
    args = parser.parse_args()
    create_project(args.slug)


if __name__ == "__main__":
    main()


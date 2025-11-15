import argparse
import os
import sys
from urllib.parse import urlparse
from urllib.request import urlopen

VALID_MODES = {"local", "remote"}


def validate_repo(repo: str, mode: str):
    if mode == "remote":
        parsed = urlparse(repo)
        if not (parsed.scheme and parsed.netloc):
            raise ValueError(f"Некорректный URL: {repo}")

    if mode == "local":
        if not os.path.exists(repo):
            raise ValueError(f"Файл или директория не найдены: {repo}")


def validate_output(filename: str):
    if not filename.endswith((".png", ".jpg", ".svg")):
        raise ValueError(
            f"Имя выходного файла должно оканчиваться на .png, .jpg или .svg: {filename}"
        )


def load_cargo_toml(path_or_url: str, mode: str) -> str:
    if mode == "local":
        cargo_path = (
            path_or_url if path_or_url.endswith("Cargo.toml")
            else os.path.join(path_or_url, "Cargo.toml")
        )

        if not os.path.exists(cargo_path):
            raise ValueError(f"Cargo.toml не найден: {cargo_path}")

        with open(cargo_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        try:
            with urlopen(path_or_url) as resp:
                return resp.read().decode("utf-8")
        except Exception as e:
            raise ValueError(f"Ошибка загрузки файла по URL: {e}")


def parse_dependencies(toml_text: str):
    deps = []
    in_deps = False

    for line in toml_text.splitlines():
        stripped = line.strip()

        # Начало секции
        if stripped == "[dependencies]":
            in_deps = True
            continue

        if stripped.startswith("[") and stripped != "[dependencies]" and in_deps:
            break

        if in_deps and stripped and not stripped.startswith("#"):
            if "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                deps.append(key)

    return deps


def parse_args():
    parser = argparse.ArgumentParser(description="Этап 2 — Сбор данных")
    parser.add_argument("--package", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--mode", required=True, choices=VALID_MODES)
    parser.add_argument("--output", required=True)
    parser.add_argument("--filter", default="")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        validate_repo(args.repo, args.mode)
        validate_output(args.output)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        toml_text = load_cargo_toml(args.repo, args.mode)
        deps = parse_dependencies(toml_text)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    print("Параметры запуска:")
    print(f"  package = {args.package}")
    print(f"  repo    = {args.repo}")
    print(f"  mode    = {args.mode}")
    print(f"  output  = {args.output}")
    print(f"  filter  = {args.filter}")

    print("\nПрямые зависимости:")
    if deps:
        for d in deps:
            print(f"  - {d}")
    else:
        print("  Нет зависимостей.")


if __name__ == "__main__":
    main()

import sys
import json
import subprocess

from src.utils.python_finder import get_python_executable

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

FUNC_TAGS = [
    "UI Framework", "Web Framework", "Data Science", "Dev Tools",
    "Network", "Database", "CLI", "File & IO", "Automation", "Crypto",
]

LANG_TAGS = [
    "Python", "Node.js", "Java", "Rust", "Go", "C/C++", "Dotnet",
]

_PKG_TAGS = {
    "tkinter": ("UI Framework", "Python"),
    "customtkinter": ("UI Framework", "Python"),
    "pyqt": ("UI Framework", "Python"),
    "pyqt5": ("UI Framework", "Python"),
    "pyqt6": ("UI Framework", "Python"),
    "pyside": ("UI Framework", "Python"),
    "pyside2": ("UI Framework", "Python"),
    "pyside6": ("UI Framework", "Python"),
    "kivy": ("UI Framework", "Python"),
    "wxpython": ("UI Framework", "Python"),
    "dearpygui": ("UI Framework", "Python"),
    "pygame": ("UI Framework", "Python"),
    "flet": ("UI Framework", "Python"),
    "flask": ("Web Framework", "Python"),
    "django": ("Web Framework", "Python"),
    "fastapi": ("Web Framework", "Python"),
    "tornado": ("Web Framework", "Python"),
    "sanic": ("Web Framework", "Python"),
    "bottle": ("Web Framework", "Python"),
    "aiohttp": ("Web Framework", "Python"),
    "uvicorn": ("Web Framework", "Python"),
    "gunicorn": ("Web Framework", "Python"),
    "starlette": ("Web Framework", "Python"),
    "quart": ("Web Framework", "Python"),
    "numpy": ("Data Science", "Python"),
    "pandas": ("Data Science", "Python"),
    "scipy": ("Data Science", "Python"),
    "matplotlib": ("Data Science", "Python"),
    "seaborn": ("Data Science", "Python"),
    "plotly": ("Data Science", "Python"),
    "bokeh": ("Data Science", "Python"),
    "scikit-learn": ("Data Science", "Python"),
    "sklearn": ("Data Science", "Python"),
    "tensorflow": ("Data Science", "Python"),
    "torch": ("Data Science", "Python"),
    "keras": ("Data Science", "Python"),
    "xgboost": ("Data Science", "Python"),
    "lightgbm": ("Data Science", "Python"),
    "jupyter": ("Data Science", "Python"),
    "ipython": ("Data Science", "Python"),
    "notebook": ("Data Science", "Python"),
    "polars": ("Data Science", "Python"),
    "pytest": ("Dev Tools", "Python"),
    "black": ("Dev Tools", "Python"),
    "ruff": ("Dev Tools", "Python"),
    "mypy": ("Dev Tools", "Python"),
    "pylint": ("Dev Tools", "Python"),
    "flake8": ("Dev Tools", "Python"),
    "isort": ("Dev Tools", "Python"),
    "pyinstaller": ("Dev Tools", "Python"),
    "setuptools": ("Dev Tools", "Python"),
    "wheel": ("Dev Tools", "Python"),
    "pip": ("Dev Tools", "Python"),
    "conda": ("Dev Tools", "Python"),
    "poetry": ("Dev Tools", "Python"),
    "uv": ("Dev Tools", "Python"),
    "sphinx": ("Dev Tools", "Python"),
    "mkdocs": ("Dev Tools", "Python"),
    "pre-commit": ("Dev Tools", "Python"),
    "tox": ("Dev Tools", "Python"),
    "nox": ("Dev Tools", "Python"),
    "hatch": ("Dev Tools", "Python"),
    "requests": ("Network", "Python"),
    "httpx": ("Network", "Python"),
    "urllib3": ("Network", "Python"),
    "websocket": ("Network", "Python"),
    "websockets": ("Network", "Python"),
    "paramiko": ("Network", "Python"),
    "fabric": ("Network", "Python"),
    "socketio": ("Network", "Python"),
    "sqlalchemy": ("Database", "Python"),
    "psycopg": ("Database", "Python"),
    "pymysql": ("Database", "Python"),
    "sqlite3": ("Database", "Python"),
    "redis": ("Database", "Python"),
    "pymongo": ("Database", "Python"),
    "alembic": ("Database", "Python"),
    "peewee": ("Database", "Python"),
    "tortoise": ("Database", "Python"),
    "asyncpg": ("Database", "Python"),
    "click": ("CLI", "Python"),
    "argparse": ("CLI", "Python"),
    "typer": ("CLI", "Python"),
    "rich": ("CLI", "Python"),
    "prompt-toolkit": ("CLI", "Python"),
    "colorama": ("CLI", "Python"),
    "tqdm": ("CLI", "Python"),
    "halo": ("CLI", "Python"),
    "openpyxl": ("File & IO", "Python"),
    "xlrd": ("File & IO", "Python"),
    "xlwt": ("File & IO", "Python"),
    "pillow": ("File & IO", "Python"),
    "pyyaml": ("File & IO", "Python"),
    "toml": ("File & IO", "Python"),
    "json5": ("File & IO", "Python"),
    "csvkit": ("File & IO", "Python"),
    "chardet": ("File & IO", "Python"),
    "python-magic": ("File & IO", "Python"),
    "selenium": ("Automation", "Python"),
    "playwright": ("Automation", "Python"),
    "pyautogui": ("Automation", "Python"),
    "pynput": ("Automation", "Python"),
    "schedule": ("Automation", "Python"),
    "celery": ("Automation", "Python"),
    "rq": ("Automation", "Python"),
    "dramatiq": ("Automation", "Python"),
    "cryptography": ("Crypto", "Python"),
    "pycryptodome": ("Crypto", "Python"),
    "hashlib": ("Crypto", "Python"),
    "passlib": ("Crypto", "Python"),
    "jwt": ("Crypto", "Python"),
    "express": ("Web Framework", "Node.js"),
    "react": ("UI Framework", "Node.js"),
    "vue": ("UI Framework", "Node.js"),
    "angular": ("UI Framework", "Node.js"),
    "next": ("Web Framework", "Node.js"),
    "nuxt": ("Web Framework", "Node.js"),
    "svelte": ("UI Framework", "Node.js"),
    "webpack": ("Dev Tools", "Node.js"),
    "vite": ("Dev Tools", "Node.js"),
    "rollup": ("Dev Tools", "Node.js"),
    "esbuild": ("Dev Tools", "Node.js"),
    "typescript": ("Dev Tools", "Node.js"),
    "ts-node": ("Dev Tools", "Node.js"),
    "tsx": ("Dev Tools", "Node.js"),
    "eslint": ("Dev Tools", "Node.js"),
    "prettier": ("Dev Tools", "Node.js"),
    "jest": ("Dev Tools", "Node.js"),
    "mocha": ("Dev Tools", "Node.js"),
    "vitest": ("Dev Tools", "Node.js"),
    "lodash": ("File & IO", "Node.js"),
    "axios": ("Network", "Node.js"),
    "dayjs": ("File & IO", "Node.js"),
    "zod": ("Dev Tools", "Node.js"),
    "maven": ("Dev Tools", "Java"),
    "gradle": ("Dev Tools", "Java"),
    "spring-boot": ("Web Framework", "Java"),
    "junit": ("Dev Tools", "Java"),
    "mockito": ("Dev Tools", "Java"),
    "lombok": ("Dev Tools", "Java"),
    "jackson": ("File & IO", "Java"),
    "gson": ("File & IO", "Java"),
    "slf4j": ("Dev Tools", "Java"),
    "serde": ("File & IO", "Rust"),
    "tokio": ("Network", "Rust"),
    "actix": ("Web Framework", "Rust"),
    "axum": ("Web Framework", "Rust"),
    "clap": ("CLI", "Rust"),
    "reqwest": ("Network", "Rust"),
    "rustfmt": ("Dev Tools", "Rust"),
    "cargo": ("Dev Tools", "Rust"),
    "rustup": ("Dev Tools", "Rust"),
    "gin": ("Web Framework", "Go"),
    "echo": ("Web Framework", "Go"),
    "fiber": ("Web Framework", "Go"),
    "gorm": ("Database", "Go"),
    "cobra": ("CLI", "Go"),
    "viper": ("File & IO", "Go"),
    "gofmt": ("Dev Tools", "Go"),
    "golint": ("Dev Tools", "Go"),
    "delve": ("Dev Tools", "Go"),
    "cmake": ("Dev Tools", "C/C++"),
    "make": ("Dev Tools", "C/C++"),
    "gcc": ("Dev Tools", "C/C++"),
    "clang": ("Dev Tools", "C/C++"),
    "llvm": ("Dev Tools", "C/C++"),
    "vcpkg": ("Dev Tools", "C/C++"),
    "conan": ("Dev Tools", "C/C++"),
    "boost": ("File & IO", "C/C++"),
    "opencv": ("Data Science", "C/C++"),
    "qt": ("UI Framework", "C/C++"),
    "nuget": ("Dev Tools", "Dotnet"),
    "xunit": ("Dev Tools", "Dotnet"),
    "nunit": ("Dev Tools", "Dotnet"),
    "moq": ("Dev Tools", "Dotnet"),
    "entityframework": ("Database", "Dotnet"),
    "aspnetcore": ("Web Framework", "Dotnet"),
    "serilog": ("Dev Tools", "Dotnet"),
}


def get_installed_packages():
    try:
        py = get_python_executable()
        output = subprocess.check_output(
            [py, "-m", "pip", "list", "--format=json"], text=True, creationflags=_SUBPROCESS_FLAGS
        )
        return json.loads(output)
    except Exception:
        return []


INSTALL_TAGS = ["Installed", "Not Installed"]


def get_categorized_packages(func_tag: str = "", lang_tag: str = "", install_tag: str = ""):
    installed_pkgs = get_installed_packages()
    installed_set = {p["name"].lower() for p in installed_pkgs}
    installed_map = {p["name"].lower(): p for p in installed_pkgs}

    all_known = set(_PKG_TAGS.keys())
    all_names = installed_set | all_known

    result = []
    for name_lower in all_names:
        tags = _PKG_TAGS.get(name_lower, ("Other", "Python"))
        f_tag, l_tag = tags
        is_installed = name_lower in installed_set

        if func_tag and f_tag != func_tag:
            continue
        if lang_tag and l_tag != lang_tag:
            continue
        if install_tag == "Installed" and not is_installed:
            continue
        if install_tag == "Not Installed" and is_installed:
            continue

        if is_installed:
            p = installed_map[name_lower]
            entry = {"name": p["name"], "version": p["version"], "func_tag": f_tag, "lang_tag": l_tag, "install_tag": "Installed"}
        else:
            entry = {"name": name_lower, "version": "", "func_tag": f_tag, "lang_tag": l_tag, "install_tag": "Not Installed"}
        result.append(entry)

    return sorted(result, key=lambda x: x["name"].lower())


def install_package(name):
    try:
        py = get_python_executable()
        result = subprocess.run(
            [py, "-m", "pip", "install", name],
            capture_output=True, text=True, creationflags=_SUBPROCESS_FLAGS,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def uninstall_package(name):
    try:
        py = get_python_executable()
        result = subprocess.run(
            [py, "-m", "pip", "uninstall", "-y", name],
            capture_output=True, text=True, creationflags=_SUBPROCESS_FLAGS,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

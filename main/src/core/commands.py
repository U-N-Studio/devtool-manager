import sys
import os
import subprocess
import shutil

from src.core.command_probes import probe_command

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

_COMMAND_DEFS = [
    {"name": "git", "version_args": ["--version"], "help_args": ["--help"], "description": "分布式版本控制系统", "env_vars": ["GIT_HOME", "GIT_EXEC_PATH", "GIT_EDITOR", "GIT_CONFIG_GLOBAL"]},
    {"name": "svn", "version_args": ["--version", "--quiet"], "help_args": ["help"], "description": "Apache 集中式版本控制", "env_vars": ["SVN_HOME"]},
    {"name": "hg", "version_args": ["--version"], "help_args": ["--help"], "description": "Mercurial 分布式版本控制", "env_vars": ["HGRCPATH"]},
    {"name": "java", "version_args": ["-version"], "help_args": ["-help"], "description": "Java 运行时 (JRE/JDK)", "env_vars": ["JAVA_HOME", "JRE_HOME", "JDK_HOME", "CLASSPATH", "JAVA_OPTS", "JAVA_TOOL_OPTIONS"]},
    {"name": "javac", "version_args": ["-version"], "help_args": ["-help"], "description": "Java 编译器", "env_vars": ["JAVA_HOME", "JDK_HOME"]},
    {"name": "mvn", "version_args": ["--version"], "help_args": ["--help"], "description": "Apache Maven 构建工具", "env_vars": ["MAVEN_HOME", "M2_HOME"]},
    {"name": "gradle", "version_args": ["--version"], "help_args": ["--help"], "description": "Gradle 构建系统", "env_vars": ["GRADLE_HOME", "GRADLE_USER_HOME"]},
    {"name": "ant", "version_args": ["-version"], "help_args": ["-help"], "description": "Apache Ant 构建工具", "env_vars": ["ANT_HOME"]},
    {"name": "python", "version_args": ["--version"], "help_args": ["--help"], "description": "Python 解释器", "env_vars": ["PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONIOENCODING", "PYTHONUTF8"]},
    {"name": "pip", "version_args": ["--version"], "help_args": ["--help"], "description": "Python 包安装器", "env_vars": ["PIP_INDEX_URL", "PIP_TARGET"]},
    {"name": "conda", "version_args": ["--version"], "help_args": ["--help"], "description": "Conda 包与环境管理器", "env_vars": ["CONDA_PREFIX", "CONDA_DEFAULT_ENV"]},
    {"name": "poetry", "version_args": ["--version"], "help_args": ["--help"], "description": "Python 依赖管理工具", "env_vars": ["POETRY_HOME"]},
    {"name": "uv", "version_args": ["--version"], "help_args": ["--help"], "description": "快速 Python 包安装器", "env_vars": []},
    {"name": "node", "version_args": ["--version"], "help_args": ["--help"], "description": "Node.js JavaScript 运行时", "env_vars": ["NODE_HOME", "NODE_PATH", "NODE_OPTIONS"]},
    {"name": "npm", "version_args": ["--version"], "help_args": ["--help"], "description": "Node 包管理器", "env_vars": ["NPM_CONFIG_PREFIX", "NPM_CONFIG_REGISTRY", "NPM_HOME"]},
    {"name": "npx", "version_args": ["--version"], "help_args": ["--help"], "description": "Node 包执行器", "env_vars": []},
    {"name": "yarn", "version_args": ["--version"], "help_args": ["--help"], "description": "Yarn 包管理器", "env_vars": ["YARN_HOME"]},
    {"name": "pnpm", "version_args": ["--version"], "help_args": ["--help"], "description": "高性能 npm 替代", "env_vars": ["PNPM_HOME"]},
    {"name": "bun", "version_args": ["--version"], "help_args": ["--help"], "description": "Bun JavaScript 运行时与打包器", "env_vars": ["BUN_INSTALL"]},
    {"name": "go", "version_args": ["version"], "help_args": ["help"], "description": "Go 编程语言", "env_vars": ["GOROOT", "GOPATH", "GOBIN", "GOOS", "GOARCH"]},
    {"name": "rustc", "version_args": ["--version"], "help_args": ["--help"], "description": "Rust 编译器", "env_vars": ["RUSTUP_HOME", "RUST_SRC_PATH"]},
    {"name": "cargo", "version_args": ["--version"], "help_args": ["--help"], "description": "Rust 包管理器", "env_vars": ["CARGO_HOME"]},
    {"name": "rustup", "version_args": ["--version"], "help_args": ["--help"], "description": "Rust 工具链安装器", "env_vars": ["RUSTUP_HOME"]},
    {"name": "gcc", "version_args": ["--version"], "help_args": ["--help"], "description": "GNU C 编译器", "env_vars": ["MINGW_HOME", "GCC_HOME"]},
    {"name": "g++", "version_args": ["--version"], "help_args": ["--help"], "description": "GNU C++ 编译器", "env_vars": ["MINGW_HOME", "GCC_HOME"]},
    {"name": "clang", "version_args": ["--version"], "help_args": ["--help"], "description": "LLVM C/C++ 编译器", "env_vars": ["CLANG_HOME", "LLVM_HOME"]},
    {"name": "cmake", "version_args": ["--version"], "help_args": ["--help"], "description": "CMake 构建系统", "env_vars": ["CMAKE_HOME"]},
    {"name": "make", "version_args": ["--version"], "help_args": ["--help"], "description": "GNU Make 构建工具", "env_vars": ["MAKE_HOME"]},
    {"name": "dotnet", "version_args": ["--version"], "help_args": ["--help"], "description": ".NET SDK/CLI", "env_vars": ["DOTNET_HOME", "DOTNET_ROOT", "NUGET_PACKAGES"]},
    {"name": "docker", "version_args": ["--version"], "help_args": ["--help"], "description": "Docker 容器引擎", "env_vars": ["DOCKER_HOME", "DOCKER_CONFIG", "DOCKER_HOST"]},
    {"name": "docker-compose", "version_args": ["--version"], "help_args": ["--help"], "description": "Docker Compose 编排工具", "env_vars": ["COMPOSE_HOME", "COMPOSE_FILE"]},
    {"name": "adb", "version_args": ["version"], "help_args": ["help"], "description": "Android 调试桥", "env_vars": ["ANDROID_HOME", "ANDROID_SDK_ROOT", "ANDROID_PLATFORM_TOOLS"]},
    {"name": "ffmpeg", "version_args": ["-version"], "help_args": ["-help"], "description": "多媒体处理框架", "env_vars": ["FFMPEG_HOME"]},
    {"name": "ssh", "version_args": ["-V"], "help_args": ["-h"], "description": "OpenSSH 客户端", "env_vars": ["SSH_HOME", "HOME"]},
    {"name": "curl", "version_args": ["--version"], "help_args": ["--help"], "description": "URL 数据传输工具", "env_vars": []},
    {"name": "wget", "version_args": ["--version"], "help_args": ["--help"], "description": "非交互式网络下载器", "env_vars": []},
    {"name": "7z", "version_args": [], "help_args": [], "description": "7-Zip 压缩工具", "env_vars": [], "version_hint": "7z | findstr /i \"7-Zip\""},
]

_CMD_DEFS_MAP = {d["name"]: d for d in _COMMAND_DEFS}

_cache = {}


def clear_cache():
    _cache.clear()


def _run_cmd(args, timeout=5):
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            creationflags=_SUBPROCESS_FLAGS,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return output.strip()
    except Exception:
        return None


def _extract_params(help_text, max_items=15):
    if not help_text:
        return []
    params = []
    seen = set()
    for line in help_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-") or stripped.startswith("/"):
            parts = stripped.split()
            if parts:
                token = parts[0]
                if token not in seen:
                    seen.add(token)
                    desc = " ".join(parts[1:]) if len(parts) > 1 else ""
                    if len(desc) > 60:
                        desc = desc[:57] + "..."
                    params.append({"flag": token, "desc": desc})
                    if len(params) >= max_items:
                        break
    return params


def _resolve_env_values(env_var_names):
    result = []
    for name in env_var_names:
        value = os.environ.get(name, "")
        result.append({"name": name, "value": value, "set": bool(value)})
    return result


def get_command_names():
    return [d["name"] for d in _COMMAND_DEFS]


def load_command_detail(name: str) -> dict:
    if name in _cache:
        return _cache[name]

    cmd_def = _CMD_DEFS_MAP.get(name, {})
    path = shutil.which(name)
    installed = path is not None

    version = ""
    if installed and cmd_def.get("version_args"):
        output = _run_cmd([name] + cmd_def["version_args"])
        if output:
            first_line = output.splitlines()[0] if output.splitlines() else output
            version = first_line.strip()

    params = []
    if installed and cmd_def.get("help_args"):
        output = _run_cmd([name] + cmd_def["help_args"], timeout=3)
        if output:
            params = _extract_params(output)

    env_vars = _resolve_env_values(cmd_def.get("env_vars", []))

    result = {
        "name": name,
        "installed": installed,
        "version": version,
        "path": path or "",
        "description": cmd_def.get("description", ""),
        "params": params,
        "env_vars": env_vars,
        "config_sections": [],
    }
    _cache[name] = result

    if installed:
        result["config_sections"] = probe_command(name)

    return result

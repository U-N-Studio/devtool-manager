import sys
import os
import subprocess
import shutil

_SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0


def _run_version_cmd(args, timeout=5):
    try:
        result = subprocess.run(
            args, capture_output=True, text=True, timeout=timeout,
            creationflags=_SUBPROCESS_FLAGS,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return output.strip()
    except Exception:
        return None


def _find_executable(name):
    return shutil.which(name)


def get_java_info():
    info = {"installed": False, "version": None, "home": None, "compiler": None, "details": []}

    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        info["home"] = java_home

    output = _run_version_cmd(["java", "-version"])
    if output:
        info["installed"] = True
        for line in output.splitlines():
            if "version" in line.lower():
                info["version"] = line.strip()
                break
        info["details"].append(f"java: {output.splitlines()[0] if output.splitlines() else output}")

    output = _run_version_cmd(["javac", "-version"])
    if output:
        info["compiler"] = output.strip()
        info["details"].append(f"javac: {output.strip()}")

    output = _run_version_cmd(["jar", "--version"])
    if output:
        info["details"].append(f"jar: {output.strip()}")

    return info


def get_python_info():
    info = {"installed": False, "version": None, "home": None, "details": []}

    info["version"] = sys.version
    info["installed"] = True
    info["home"] = os.environ.get("PYTHONHOME") or os.path.dirname(sys.executable)

    output = _run_version_cmd([sys.executable, "-m", "pip", "--version"])
    if output:
        info["details"].append(output)

    for tool in ("conda", "poetry", "uv"):
        path = _find_executable(tool)
        if path:
            output = _run_version_cmd([tool, "--version"])
            if output:
                first_line = output.splitlines()[0]
                info["details"].append(f"{tool}: {first_line}")

    return info


def get_android_info():
    info = {"installed": False, "sdk": None, "ndk": None, "details": []}

    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if sdk and os.path.isdir(sdk):
        info["sdk"] = sdk
        info["installed"] = True
        info["details"].append(f"SDK: {sdk}")

    ndk = os.environ.get("ANDROID_NDK_HOME")
    if ndk and os.path.isdir(ndk):
        info["ndk"] = ndk
        info["details"].append(f"NDK: {ndk}")

    output = _run_version_cmd(["adb", "version"])
    if output:
        info["installed"] = True
        first_line = output.splitlines()[0] if output.splitlines() else output
        info["details"].append(f"adb: {first_line}")

    for tool in ("gradle",):
        path = _find_executable(tool)
        if path:
            output = _run_version_cmd([tool, "--version"])
            if output:
                for line in output.splitlines():
                    if "version" in line.lower() or "gradle" in line.lower():
                        info["details"].append(f"gradle: {line.strip()}")
                        break

    return info


def get_node_info():
    info = {"installed": False, "version": None, "home": None, "details": []}

    output = _run_version_cmd(["node", "--version"])
    if output:
        info["installed"] = True
        info["version"] = output.strip()
        info["details"].append(f"node: {output.strip()}")

    output = _run_version_cmd(["npm", "--version"])
    if output:
        info["details"].append(f"npm: {output.strip()}")

    for tool in ("yarn", "pnpm", "bun"):
        path = _find_executable(tool)
        if path:
            output = _run_version_cmd([tool, "--version"])
            if output:
                info["details"].append(f"{tool}: {output.strip()}")

    return info


def get_go_info():
    info = {"installed": False, "version": None, "home": None, "details": []}

    output = _run_version_cmd(["go", "version"])
    if output:
        info["installed"] = True
        info["version"] = output.strip()
        info["details"].append(output.strip())

    goroot = os.environ.get("GOROOT")
    if goroot:
        info["home"] = goroot
        info["details"].append(f"GOROOT: {goroot}")

    gopath = os.environ.get("GOPATH")
    if gopath:
        info["details"].append(f"GOPATH: {gopath}")

    return info


def get_rust_info():
    info = {"installed": False, "version": None, "home": None, "details": []}

    output = _run_version_cmd(["rustc", "--version"])
    if output:
        info["installed"] = True
        info["version"] = output.strip()
        info["details"].append(output.strip())

    output = _run_version_cmd(["cargo", "--version"])
    if output:
        info["details"].append(output.strip())

    output = _run_version_cmd(["rustup", "--version"])
    if output:
        first_line = output.splitlines()[0] if output.splitlines() else output
        info["details"].append(first_line)

    return info


TOOL_INFO_FUNCS = {
    "Java": get_java_info,
    "Python": get_python_info,
    "Android": get_android_info,
    "Node.js": get_node_info,
    "Go": get_go_info,
    "Rust": get_rust_info,
}


def get_tool_info(category: str):
    func = TOOL_INFO_FUNCS.get(category)
    if func:
        return func()
    return {"installed": False, "details": []}

const { execSync, exec } = require("child_process");
const path = require("path");
const fs = require("fs");

const HKLM_ENV =
  "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment";
const HKCU_ENV = "Environment";

const ENV_CATEGORIES = {
  Java: [
    "JAVA_HOME", "JRE_HOME", "JDK_HOME", "CLASSPATH",
    "JAVA_OPTS", "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS",
    "GRADLE_HOME", "MAVEN_HOME", "M2_HOME", "ANT_HOME",
  ],
  Python: [
    "PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONIOENCODING",
    "PYTHONUTF8", "PYTHONHASHSEED", "PIP_INDEX_URL", "PIP_TARGET",
    "CONDA_PREFIX", "VIRTUAL_ENV", "POETRY_HOME",
  ],
  Android: [
    "ANDROID_HOME", "ANDROID_SDK_ROOT", "ANDROID_NDK_HOME",
    "ANDROID_SDK_HOME", "ANDROID_AVD_HOME",
    "ANDROID_PLATFORM_TOOLS", "ANDROID_BUILD_TOOLS",
  ],
  "Node.js": [
    "NODE_HOME", "NODE_PATH", "NPM_CONFIG_PREFIX",
    "NPM_CONFIG_REGISTRY", "NPM_TOKEN", "NPM_HOME",
    "YARN_HOME", "PNPM_HOME", "BUN_INSTALL",
  ],
  Go: ["GOROOT", "GOPATH", "GOBIN", "GOOS", "GOARCH", "GOMODCACHE"],
  Rust: ["RUSTUP_HOME", "CARGO_HOME", "RUST_SRC_PATH"],
  "C/C++": [
    "MINGW_HOME", "MSYS2_HOME", "CYGWIN_HOME",
    "GCC_HOME", "CLANG_HOME", "LLVM_HOME",
    "CMAKE_HOME", "MAKE_HOME", "VCPKG_ROOT", "CONAN_HOME",
  ],
  Dotnet: [
    "DOTNET_HOME", "DOTNET_ROOT", "DOTNET_INSTALL_DIR",
    "NUGET_PACKAGES", "NUGET_HTTP_CACHE",
  ],
  Docker: [
    "DOCKER_HOME", "DOCKER_CONFIG", "DOCKER_HOST",
    "COMPOSE_HOME", "COMPOSE_FILE", "COMPOSE_PROJECT_NAME",
  ],
  Git: ["GIT_HOME", "GIT_INSTALL_ROOT", "GIT_EXEC_PATH", "GIT_EDITOR", "GIT_CONFIG_GLOBAL"],
  IDE: [
    "IDEA_HOME", "IDEA_PROPERTIES", "WEBIDE_HOME",
    "VSCODE_HOME", "VSCODE_EXTENSIONS",
    "PYCHARM_HOME", "ANDROID_STUDIO_HOME",
  ],
  Proxy: [
    "HTTP_PROXY", "HTTPS_PROXY", "FTP_PROXY",
    "NO_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "no_proxy",
  ],
  Path: ["PATH", "PATHEXT"],
  System: [
    "COMPUTERNAME", "USERNAME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH",
    "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "OS",
    "PROCESSOR_ARCHITECTURE", "NUMBER_OF_PROCESSORS",
    "TEMP", "TMP", "COMSPEC", "PSMODULEPATH",
  ],
};

const PATH_KEYWORDS = {
  Java: ["java", "jdk", "jre", "oracle", "openjdk", "gradle", "maven", "ant"],
  Python: ["python", "pip", "conda", "venv", "virtualenv", "poetry"],
  Android: ["android", "sdk", "ndk", "adb", "gradle", "avd"],
  "Node.js": ["node", "npm", "npx", "yarn", "pnpm", "bun"],
  Go: ["go", "golang", "goroot", "gopath"],
  Rust: ["rust", "cargo", "rustup"],
};

function readRegistryVars(hive, keyPath) {
  const hiveName = hive === "HKLM" ? "HKEY_LOCAL_MACHINE" : "HKEY_CURRENT_USER";
  try {
    const output = execSync(
      `reg query "${hiveName}\\${keyPath}" /reg:64`,
      { encoding: "utf8", windowsHide: true, timeout: 5000 }
    );
    const result = {};
    for (const line of output.split("\n")) {
      const match = line.trim().match(/^\s*(\S+)\s+REG_\w+\s+(.+)$/);
      if (match) {
        result[match[1].toUpperCase()] = match[2].trim();
      }
    }
    return result;
  } catch {
    return {};
  }
}

function broadcastEnvChange() {
  try {
    execSync(
      `powershell -NoProfile -Command "[System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer([System.Runtime.InteropServices.Marshal]::ReadInt32([System.Diagnostics.Process]::GetCurrentProcess().Handle,0),[System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer).Invoke(0xFFFF,0x001A,0,'Environment',0x0002,5000,[Ref]0)"`,
      { windowsHide: true, timeout: 10000 }
    );
  } catch {
    // fallback: notify via setx
  }
}

function setRegistryVar(name, value, source) {
  const hiveName = source === "system" ? "HKEY_LOCAL_MACHINE" : "HKEY_CURRENT_USER";
  const keyPath = source === "system" ? HKLM_ENV : HKCU_ENV;
  try {
    execSync(`reg add "${hiveName}\\${keyPath}" /v "${name}" /t REG_EXPAND_SZ /d "${value}" /f /reg:64`, {
      windowsHide: true,
      timeout: 5000,
    });
    broadcastEnvChange();
    return true;
  } catch {
    return false;
  }
}

function deleteRegistryVar(name, source) {
  const hiveName = source === "system" ? "HKEY_LOCAL_MACHINE" : "HKEY_CURRENT_USER";
  const keyPath = source === "system" ? HKLM_ENV : HKCU_ENV;
  try {
    execSync(`reg delete "${hiveName}\\${keyPath}" /v "${name}" /f /reg:64`, {
      windowsHide: true,
      timeout: 5000,
    });
    broadcastEnvChange();
    return true;
  } catch {
    return false;
  }
}

function classifyEnvVar(name, systemVars, userVars) {
  const upper = name.toUpperCase();
  if (upper in systemVars) return "system";
  if (upper in userVars) return "user";
  return "system";
}

function getCategorizedEnvVars() {
  const allVars = { ...process.env };
  const systemVars = readRegistryVars("HKLM", HKLM_ENV);
  const userVars = readRegistryVars("HKCU", HKCU_ENV);

  const pathValue = allVars.PATH || "";
  const pathSource = classifyEnvVar("PATH", systemVars, userVars);
  const pathEntries = pathValue.split(";").filter((e) => e.trim()).map((e) => ({
    name: "PATH",
    value: e.trim(),
    source: pathSource,
    isPathEntry: true,
  }));

  const pathByCat = {};
  for (const entry of pathEntries) {
    const lower = entry.value.toLowerCase();
    for (const [catName, keywords] of Object.entries(PATH_KEYWORDS)) {
      if (keywords.some((kw) => lower.includes(kw))) {
        (pathByCat[catName] ||= []).push(entry);
        break;
      }
    }
  }

  const result = {};
  for (const [catName, varNames] of Object.entries(ENV_CATEGORIES)) {
    if (catName === "Path") continue;
    const items = [];
    for (const varName of varNames) {
      const upper = varName.toUpperCase();
      if (upper in allVars) {
        const source = classifyEnvVar(upper, systemVars, userVars);
        items.push({ name: varName, value: allVars[upper], source });
      }
    }
    if (pathByCat[catName]) items.push(...pathByCat[catName]);
    if (items.length) result[catName] = items;
  }

  const pathItems = [];
  for (const varName of ["PATH", "PATHEXT"]) {
    const upper = varName.toUpperCase();
    if (!(upper in allVars)) continue;
    const source = classifyEnvVar(upper, systemVars, userVars);
    if (upper === "PATH") {
      for (const entry of pathEntries) pathItems.push(entry);
    } else {
      pathItems.push({ name: varName, value: allVars[upper], source });
    }
  }
  if (pathItems.length) result["Path"] = pathItems;

  const categorizedNames = new Set();
  for (const varNames of Object.values(ENV_CATEGORIES)) {
    for (const v of varNames) categorizedNames.add(v.toUpperCase());
  }

  const otherSystem = [];
  const otherUser = [];
  for (const [name, value] of Object.entries(allVars).sort()) {
    if (categorizedNames.has(name.toUpperCase())) continue;
    const source = classifyEnvVar(name, systemVars, userVars);
    const entry = { name, value, source };
    if (source === "user") otherUser.push(entry);
    else otherSystem.push(entry);
  }
  if (otherSystem.length) result["Other (System)"] = otherSystem;
  if (otherUser.length) result["Other (User)"] = otherUser;

  return result;
}

function addPathEntry(entry, source) {
  const allVars = { ...process.env };
  const currentPath = allVars.PATH || "";
  const newPath = currentPath ? `${currentPath};${entry}` : entry;
  return setRegistryVar("PATH", newPath, source);
}

function deletePathEntry(entry, source) {
  const allVars = { ...process.env };
  const currentPath = allVars.PATH || "";
  const entries = currentPath.split(";").filter((e) => e.trim() !== entry.trim());
  const newPath = entries.join(";");
  return setRegistryVar("PATH", newPath, source);
}

function register(ipcMain) {
  ipcMain.handle("env:getCategorized", () => getCategorizedEnvVars());
  ipcMain.handle("env:set", (_, name, value, source) => setRegistryVar(name, value, source));
  ipcMain.handle("env:delete", (_, name, source) => deleteRegistryVar(name, source));
  ipcMain.handle("env:addPath", (_, entry, source) => addPathEntry(entry, source));
  ipcMain.handle("env:deletePath", (_, entry, source) => deletePathEntry(entry, source));
}

module.exports = { register };

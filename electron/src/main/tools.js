const { execSync } = require("child_process");

function runVersionCmd(args, timeout = 5000) {
  try {
    const result = execSync(args.join(" "), {
      encoding: "utf8",
      windowsHide: true,
      timeout,
      stdio: ["pipe", "pipe", "pipe"],
    });
    return result.trim();
  } catch (e) {
    const output = (e.stdout || "") + (e.stderr || "");
    return output.trim() || null;
  }
}

function getJavaInfo() {
  const info = { installed: false, version: null, home: null, compiler: null, details: [] };
  const javaHome = process.env.JAVA_HOME;
  if (javaHome) info.home = javaHome;

  const output = runVersionCmd(["java", "-version"]);
  if (output) {
    info.installed = true;
    for (const line of output.split("\n")) {
      if (line.toLowerCase().includes("version")) { info.version = line.trim(); break; }
    }
    info.details.push(`java: ${output.split("\n")[0]}`);
  }

  const javacOut = runVersionCmd(["javac", "-version"]);
  if (javacOut) { info.compiler = javacOut.trim(); info.details.push(`javac: ${javacOut.trim()}`); }

  const jarOut = runVersionCmd(["jar", "--version"]);
  if (jarOut) info.details.push(`jar: ${jarOut.trim()}`);

  return info;
}

function getPythonInfo() {
  const info = { installed: false, version: null, home: null, details: [] };
  const output = runVersionCmd(["python", "--version"]);
  if (output) { info.installed = true; info.version = output.trim(); info.details.push(output.trim()); }

  const pipOut = runVersionCmd(["python", "-m", "pip", "--version"]);
  if (pipOut) info.details.push(pipOut.trim());

  for (const tool of ["conda", "poetry", "uv"]) {
    const vOut = runVersionCmd([tool, "--version"]);
    if (vOut) info.details.push(`${tool}: ${vOut.split("\n")[0]}`);
  }
  return info;
}

function getAndroidInfo() {
  const info = { installed: false, sdk: null, ndk: null, details: [] };
  const sdk = process.env.ANDROID_HOME || process.env.ANDROID_SDK_ROOT;
  if (sdk) { info.sdk = sdk; info.installed = true; info.details.push(`SDK: ${sdk}`); }
  const ndk = process.env.ANDROID_NDK_HOME;
  if (ndk) { info.ndk = ndk; info.details.push(`NDK: ${ndk}`); }

  const adbOut = runVersionCmd(["adb", "version"]);
  if (adbOut) { info.installed = true; info.details.push(`adb: ${adbOut.split("\n")[0]}`); }

  const gradleOut = runVersionCmd(["gradle", "--version"]);
  if (gradleOut) {
    for (const line of gradleOut.split("\n")) {
      if (line.toLowerCase().includes("version") || line.toLowerCase().includes("gradle")) {
        info.details.push(`gradle: ${line.trim()}`); break;
      }
    }
  }
  return info;
}

function getNodeInfo() {
  const info = { installed: false, version: null, home: null, details: [] };
  const output = runVersionCmd(["node", "--version"]);
  if (output) { info.installed = true; info.version = output.trim(); info.details.push(`node: ${output.trim()}`); }

  const npmOut = runVersionCmd(["npm", "--version"]);
  if (npmOut) info.details.push(`npm: ${npmOut.trim()}`);

  for (const tool of ["yarn", "pnpm", "bun"]) {
    const vOut = runVersionCmd([tool, "--version"]);
    if (vOut) info.details.push(`${tool}: ${vOut.trim()}`);
  }
  return info;
}

function getGoInfo() {
  const info = { installed: false, version: null, home: null, details: [] };
  const output = runVersionCmd(["go", "version"]);
  if (output) { info.installed = true; info.version = output.trim(); info.details.push(output.trim()); }
  if (process.env.GOROOT) { info.home = process.env.GOROOT; info.details.push(`GOROOT: ${process.env.GOROOT}`); }
  if (process.env.GOPATH) info.details.push(`GOPATH: ${process.env.GOPATH}`);
  return info;
}

function getRustInfo() {
  const info = { installed: false, version: null, home: null, details: [] };
  const output = runVersionCmd(["rustc", "--version"]);
  if (output) { info.installed = true; info.version = output.trim(); info.details.push(output.trim()); }
  const cargoOut = runVersionCmd(["cargo", "--version"]);
  if (cargoOut) info.details.push(cargoOut.trim());
  const rustupOut = runVersionCmd(["rustup", "--version"]);
  if (rustupOut) info.details.push(rustupOut.split("\n")[0]);
  return info;
}

const TOOL_INFO_FUNCS = {
  Java: getJavaInfo, Python: getPythonInfo, Android: getAndroidInfo,
  "Node.js": getNodeInfo, Go: getGoInfo, Rust: getRustInfo,
};

function register(ipcMain) {
  ipcMain.handle("tools:getInfo", (_, category) => {
    const func = TOOL_INFO_FUNCS[category];
    return func ? func() : { installed: false, details: [] };
  });
}

module.exports = { register };

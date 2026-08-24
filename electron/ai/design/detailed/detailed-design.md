# DevTool Manager — 详细设计

## env.js 详细设计

### readRegistryVars(hive, keyPath)
- 调用 `reg query "HIVE\keyPath" /reg:64`
- 解析输出：每行匹配 `NAME  REG_TYPE  VALUE`
- 返回 `{ NAME: VALUE }` 大写键

### getCategorizedEnvVars()
1. 读取 process.env → allVars
2. readRegistryVars("HKLM", HKLM_ENV) → systemVars
3. readRegistryVars("HKCU", HKCU_ENV) → userVars
4. 拆分 PATH → pathEntries[]
5. 按 PATH_KEYWORDS 归类 → pathByCat
6. 遍历 ENV_CATEGORIES，组装每个分类的 items
7. 未归类变量 → Other (System) / Other (User)
8. 返回 `{ [category]: items[] }`

### setRegistryVar / deleteRegistryVar
- `reg add` / `reg delete`，带 `/reg:64` 标志
- 成功后调用 broadcastEnvChange()

## packages.js 详细设计

### PKG_TAGS 映射
- 键: 包名小写
- 值: [func_tag, lang_tag]
- 约 150 条已知包

### getCategorizedPackages(funcTag, langTag, installTag)
1. `pip list --format=json` → installedPkgs
2. 合并 installedSet ∪ knownSet → allNames
3. 遍历 allNames，为每个包查找 PKG_TAGS 或默认 ("Other", "Python")
4. 按 3 个 tag 筛选
5. 已安装包取 name+version，未安装包 version=""
6. 排序返回

## tools.js 详细设计

### runVersionCmd(args, timeout=5000)
- execSync(args.join(" "), { windowsHide:true, timeout })
- 捕获 stdout+stderr，返回 trim 后结果
- 超时/失败返回 null

### 各工具检测
- getJavaInfo: java -version, javac -version, jar --version, JAVA_HOME
- getPythonInfo: python --version, pip --version, conda/poetry/uv --version
- getAndroidInfo: ANDROID_HOME, ANDROID_NDK_HOME, adb version, gradle --version
- getNodeInfo: node --version, npm --version, yarn/pnpm/bun --version
- getGoInfo: go version, GOROOT, GOPATH
- getRustInfo: rustc --version, cargo --version, rustup --version

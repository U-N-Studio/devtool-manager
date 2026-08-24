# DevTool Manager — 需求文档 (PRD)

## 产品概述

DevTool Manager 是 Windows 桌面应用，帮助开发者查看和管理：
1. **环境变量** — 系统/用户变量、PATH 条目、注册表增删改
2. **包管理** — pip 包，三维标签筛选（功能 / 语言 / 安装状态）
3. **工具版本** — Java、Python、Android、Node.js、Go、Rust 版本检测

## 目标用户

- 管理多个 SDK/运行时的 Windows 开发者
- 需要统一环境配置的团队
- 排查环境/PATH 问题的运维工程师

## 功能需求

### FR-1: 环境变量管理
| ID | 需求 | 优先级 |
|----|------|--------|
| FR-1.1 | 按平台分类显示环境变量（Java/Python/Android/Node.js/Go/Rust/C-C++/Dotnet/Docker/Git/IDE/Proxy/Path/System） | P0 |
| FR-1.2 | 每行显示变量名、值、来源（system/user） | P0 |
| FR-1.3 | 编辑环境变量值 | P0 |
| FR-1.4 | 删除环境变量（需确认） | P0 |
| FR-1.5 | 新增环境变量（名称、值、来源） | P0 |
| FR-1.6 | PATH 按分号拆分，每条显示为独立行 | P0 |
| FR-1.7 | PATH 条目按关键词自动归类到对应分类 | P1 |
| FR-1.8 | 增删单条 PATH 条目 | P0 |
| FR-1.9 | 注册表写入后广播 WM_SETTINGCHANGE | P0 |
| FR-1.10 | 分类匹配时显示工具信息卡（版本/路径） | P1 |

### FR-2: 包管理
| ID | 需求 | 优先级 |
|----|------|--------|
| FR-2.1 | 列出所有已知包（已安装+目录），每包3个tag：func_tag, lang_tag, install_tag | P0 |
| FR-2.2 | 按功能标签筛选（UI Framework/Web Framework/Data Science/Dev Tools/Network/Database/CLI/File & IO/Automation/Crypto） | P0 |
| FR-2.3 | 按语言标签筛选（Python/Node.js/Java/Rust/Go/C-C++/Dotnet） | P0 |
| FR-2.4 | 按安装状态筛选（Installed/Not Installed） | P0 |
| FR-2.5 | 三个筛选器独立且可组合 | P0 |
| FR-2.6 | 分页：每页50条，Prev/Next 导航 | P0 |
| FR-2.7 | 未安装行显示 Add 按钮，执行 pip install | P0 |
| FR-2.8 | 已安装行显示 Del 按钮，执行 pip uninstall -y | P0 |
| FR-2.9 | 通过名称输入框自定义安装包 | P1 |

### FR-3: 工具版本检测
| ID | 需求 | 优先级 |
|----|------|--------|
| FR-3.1 | 检测 Java 版本、JAVA_HOME、javac、jar | P1 |
| FR-3.2 | 检测 Python 版本、pip、conda、poetry、uv | P1 |
| FR-3.3 | 检测 Android SDK/NDK 路径、adb、gradle | P1 |
| FR-3.4 | 检测 Node.js 版本、npm、yarn、pnpm、bun | P1 |
| FR-3.5 | 检测 Go 版本、GOROOT、GOPATH | P1 |
| FR-3.6 | 检测 Rust 版本、cargo、rustup | P1 |

## 非功能需求

| ID | 需求 | 优先级 |
|----|------|--------|
| NFR-1 | 仅支持 Windows（winreg / reg.exe / WM_SETTINGCHANGE） | P0 |
| NFR-2 | 暗色主题 UI | P1 |
| NFR-3 | 所有子进程调用使用 CREATE_NO_WINDOW / windowsHide | P0 |
| NFR-4 | 响应式布局，最小 800×500 | P1 |
| NFR-5 | 包列表快速渲染（分页，单次≤50个widget） | P0 |

# 架构总览

## 项目简介

DevTool Manager 是一个基于 CustomTkinter 的 Python 环境 & 包管理 GUI 工具。支持查看 Python/Pip 版本、环境变量、已安装包列表，以及包的安装与卸载。

## 项目结构

```
main/
├── src/
│   ├── core/          # 核心逻辑：env.py, packages.py
│   ├── ui/            # GUI：app.py (CustomTkinter)
│   └── utils/         # 工具：logger.py, python_finder.py
├── config/            # 应用配置 (default.json)
├── tests/             # 测试
├── ai/                # Agent 工程化体系
│   ├── project/       # 项目上下文 (AGENTS.md + conventions + context)
│   ├── agents/        # Agent 角色定义 (planner/coder/reviewer)
│   ├── tools/         # 工具能力声明 (file/shell/search/vcs)
│   ├── workflows/     # 开发场景模板 (feature/bugfix/refactor)
│   ├── prompts/       # 提示词模板 (system + task)
│   └── architecture/  # ADR & 架构文档
├── main.py            # 入口
├── start.bat/ps1      # 启动脚本
├── build.bat/ps1      # 打包脚本 (PyInstaller)
└── pyproject.toml     # 项目元数据
```

## 分支策略

| Branch | Purpose |
|--------|---------|
| main   | 稳定发布 |
| dev    | 开发迭代 |

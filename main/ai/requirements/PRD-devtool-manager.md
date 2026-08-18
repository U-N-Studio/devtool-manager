# PRD: DevTool Manager

## 功能需求

### FR-01: 环境信息查看
- 显示 Python 版本、Pip 版本、平台、可执行文件路径
- 显示全部环境变量列表

### FR-02: 包管理
- 查看已安装包列表（名称、版本）
- 安装指定包
- 卸载指定包

### FR-03: GUI 界面
- Tab 页切换 Environment / Packages
- Refresh 按钮刷新数据
- 现代外观（CustomTkinter）

## 非功能需求

### NFR-01: 性能
- GUI 启动时间 < 3s
- 刷新操作 < 2s

### NFR-02: 可分发
- 支持打包为单文件 exe（Windows）
- exe 无需安装 Python 即可运行

### NFR-03: 兼容性
- 支持 Python 3.9+
- 支持 Windows 10/11

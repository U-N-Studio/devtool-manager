# DevTool Manager — 需求测试用例

## TC-1: 环境变量管理

### TC-1.1 查看分类环境变量
- **前置**: 系统已设置 JAVA_HOME
- **步骤**: 选择 Java 分类
- **预期**: 显示 JAVA_HOME 行，source=system，值为实际路径

### TC-1.2 编辑环境变量
- **前置**: 选中任意变量
- **步骤**: 点击 Edit → 输入新值 → 确认
- **预期**: 注册表值更新，新终端可读到新值

### TC-1.3 删除环境变量
- **前置**: 选中任意变量
- **步骤**: 点击 Del → 确认删除
- **预期**: 注册表值删除，变量从列表消失

### TC-1.4 新增环境变量
- **步骤**: 点击 Add → 输入名称/值/来源 → 确认
- **预期**: 新变量出现在列表，注册表已写入

### TC-1.5 PATH 条目拆分
- **前置**: PATH 含多条路径
- **步骤**: 选择 Path 分类
- **预期**: 每条路径显示为独立行，带 PATH> 标识

### TC-1.6 增删 PATH 条目
- **步骤**: 添加/删除单条 PATH 条目
- **预期**: PATH 值正确更新，其他条目不变

## TC-2: 包管理

### TC-2.1 三维筛选组合
- **步骤**: Function=Dev Tools, Language=Python, Status=Installed
- **预期**: 仅显示已安装的 Python Dev Tools 包（如 pytest, black, ruff）

### TC-2.2 分页导航
- **前置**: 筛选结果 > 50 条
- **步骤**: 点击 Next → Prev
- **预期**: 页面切换正确，显示 1-50/总数

### TC-2.3 安装包
- **步骤**: 在 Not Installed 行点击 Add → 确认
- **预期**: 包安装成功，刷新后状态变为 Installed

### TC-2.4 卸载包
- **步骤**: 在 Installed 行点击 Del → 确认
- **预期**: 包卸载成功，刷新后状态变为 Not Installed

## TC-3: 工具版本检测

### TC-3.1 Java 信息卡
- **前置**: 已安装 JDK
- **步骤**: 选择 Java 分类
- **预期**: 信息卡显示 java version、javac version、JAVA_HOME

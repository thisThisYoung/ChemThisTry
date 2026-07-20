# ChemThisTry 智能体操作指南（Agent Operation Guide）

> 面向 AI 智能体 / 自动化脚本的能力接口手册。
> 本文档说明如何让一个语言模型（或外部程序）像用户一样操作 ChemThisTry：
> 新建数据表、填充数据、绘图、曲线拟合、执行命令、读写 `.ctt` 工程文件。

ChemThisTry 提供**三条**互补的智能体接入通道，覆盖「应用运行时内」和「离线文件」两种场景：

| 通道 | 运行位置 | 面向对象 | 适用场景 |
|------|----------|----------|----------|
| **A. 内置 AI Chat Agent 模式** | 应用进程内（渲染进程） | 应用内置的对话助手 | 用户在软件里用自然语言驱动当前打开的工程 |
| **B. MCP Server** | 独立 Node 进程（stdio） | 外部 MCP 客户端（Claude Desktop / Cline / Continue 等） | 在应用之外读写 `.ctt` 文件、批量生成工程 |
| **C. 插件 API / 命令** | 应用进程内（插件） | 第三方插件、程序化调用 | 扩展命令、视图、导出格式，供 A 通道的 `run_command` 调用 |

三者共享同一套「能力模型」（数据表、列、图表、拟合），因此工具命名与语义高度一致。

---

## 1. 能力总览

| 能力 | A：AI Chat 工具 | B：MCP 工具 | 底层实现 |
|------|-----------------|-------------|----------|
| 列出文档 | `list_documents` | `read_project` | `useProjectStore.docs` / `.ctt` |
| 读取数据表 | `get_sheet_data` | `read_sheet` | `useDatasetStore.getDataset` |
| 新建数据表 | `create_sheet` | `add_sheet` / `create_project` | `addDoc('sheet')` + `importText` |
| 追加列 | `add_column` | （随 `add_sheet` 一次写入） | `addColumn`/`setCell` |
| 公式列 | `add_formula_column` | — | `addFormulaColumn` |
| 描述统计 | `describe_column` | — | `lib/stats.ts describe()` |
| 绘图 | `create_graph` | `add_graph` | `addGraphFromSheet` |
| 曲线拟合 | `fit_curve` | — | Python 侧车 `chem:fit` |
| 打开文档 | `open_document` | — | `useWorkspaceStore.openDoc` |
| 导出 CSV | （见 `run_command`） | `export_sheet_csv` | `useDatasetStore.exportCSV` |
| 列出/执行命令 | `list_commands` / `run_command` | — | `commandRegistry` / `runCommand` |

> 说明：MCP 通道操作的是**磁盘上的 `.ctt` 文件**（离线、无 UI），不涉及拟合、统计、侧车等需要运行时的能力；A 通道操作的是**当前正在运行的工程**，拥有全部运行时能力。

---

## 2. 通道 A —— 内置 AI Chat Agent 模式

### 2.1 开启方式

1. 打开 **Preferences**（首选项为「左侧分组导航 + 右侧内容」的主从式面板；顶部有搜索框可直接输入「AI」定位）；
2. 在左侧「智能 / AI」分组下点 **AI 助手（AI）** 标签页；
3. 填入模型服务的 Base URL / API Key / 模型名（需 OpenAI 兼容、**支持 function/tool calling**）；
4. 勾选 **Agent mode**。

设置持久化于 `localStorage` 键 `chemthis.aiSettings`（字段 `agentMode: boolean`）。保存后 `saveAiSettings()` 会调用 `aiChat.reloadSettings()` 让单例即时生效。

> 首选项面板的标签页集合为 `general | ai | plugins | graph | export | shortcuts | about`（类型 `PrefTab`，见 `src/store/preferencesStore.ts`），默认停在 `general`。除 AI 外，其余标签页的用户偏好持久化于 `localStorage` 键 `chemthis.userPrefs`（结构见 §5.5），与智能体工具互不影响。注意：在手机 Web 端（`useResponsiveStore.isPhoneWeb` 为 true）时，`ai` / `plugins` / `shortcuts` 三个标签页会被 `PreferencesModal` 过滤隐藏，仅保留 `general | graph | export | about`，避免在窄屏暴露桌面专属功能。

### 2.2 运行机制

- 代码位置：`src/lib/aiChat.ts` 的 `runAgentLoop()`，工具层在 `src/lib/ai/tools.ts`。
- 开启 Agent 模式后，`send()` 走非流式的 tool-calling 循环（最多 `MAX_AGENT_ITERATIONS = 8` 轮）：
  1. 以 `AGENT_SYSTEM_PROMPT` + 历史 + 用户输入构造请求，携带 `tools: TOOL_SCHEMAS`、`tool_choice: 'auto'`；
  2. 若模型返回 `tool_calls`，逐个用 `runTool(name, args)` 执行，把结果作为 `role:'tool'` 消息回灌；
  3. 界面上以 ✅/⚠️ 活动轨迹实时呈现每一步（`describeToolCall`）；
  4. 模型返回不含工具调用的普通文本即为最终答复。
- 工具直接操作 zustand store / 命令注册表 / 侧车 IPC，**不新增任何主进程接口**——智能体走的正是用户点按钮时走的同一套状态通路。
- 数据表、列均**按人类可读的名称寻址**（大小写不敏感），也可用内部 id。

### 2.3 工具清单（11 个）

以下为暴露给模型的 `TOOL_SCHEMAS`。参数中标注 `*` 为必填。

#### `list_documents`
列出当前工程内所有文档（sheet/graph/sketch/molecule/canvas），返回每项的 `id / type / name`。**引用文档前先调它探明现状。**

#### `get_sheet_data`
读取数据表的列与单元格。
- `sheet*`：表名或 id
- `maxRows`：返回行数上限（默认 200）
返回：每列 `name / unit / type / derived? / values`，以及 `rowCount`。

#### `create_sheet`
新建数据表，可选预填数据；自动打开为标签页。
- `name`：表名（省略则自动编号）
- `columns`：`[{ name*, unit?, values*: (number|string)[] }]`（省略则建空表）
返回：`sheetId / sheetName`。

#### `add_column`
向已有表追加一列；行数不足会自动补行。
- `sheet*` / `name*` / `values*` / `unit?`

#### `add_formula_column`
添加派生（公式）列，表达式按列名引用其它列，如 `2*Time + Signal`、`log(Y)`。
- `sheet*` / `expr*` / `name?`
表达式无法求值时返回错误信息。

#### `describe_column`
计算某数值列的描述统计：`n / mean / sd / se / min / max / median / sum`。
- `sheet*` / `column*`

#### `create_graph`
从数据表建图并打开。
- `sheet*`：源表
- `xColumn*`：X 轴列
- `yColumns*`：一个或多个 Y 轴列（`string[]`）
- `chartType`：图型（默认 `line`，取值见 §5.1）
返回：`graphId / graphName`。

#### `fit_curve`
用 Python 侧车（scipy）对两列 (X, Y) 拟合。
- `sheet*` / `xColumn*` / `yColumn*` / `model*`
- `custom`：当 `model="custom"` 时的自定义表达式，如 `a*x + b`
内置模型：`linear`、`exponential`、`gaussian`、`power`、`logistic` 等（见 §5.2）。会自动过滤非有限点，少于 2 点报错。返回拟合参数与 R²。
> 依赖 Python 侧车可用；侧车缺失时该工具不可用。

#### `open_document`
按 id 或名称打开一个已存在的文档为活动标签页。
- `document*`

#### `list_commands`
列出所有已注册的应用命令（`id + title`），供 `run_command` 使用。**注意**：`commandRegistry` 主要由**插件**贡献（见通道 C）；应用自带的「新建表/图」等动作在命令面板里，未必都进入该注册表。

#### `run_command`
按 id 执行已注册命令，可传参数。用于专用工具未覆盖的动作。
- `commandId*` / `args?`

### 2.4 对话示例

> 用户：「帮我建一张一级反应动力学表，时间 0–50 s，画浓度对时间的散点图，再用指数模型拟合。」

智能体会依次：`create_sheet`（填入 time / concentration 两列）→ `create_graph`（chartType=`scatter`）→ `fit_curve`（model=`exponential`），并在活动轨迹里逐步显示 ✅。

---

## 3. 通道 B —— MCP Server（读写 `.ctt` 文件）

### 3.1 概述

`mcp/chemthistry-mcp.mjs` 是一个独立的、基于 **stdio 的 JSON-RPC 2.0 MCP 服务器**，让任意 MCP 客户端在**不启动 ChemThisTry 应用**的情况下读写 `.ctt` 工程文件。它是**基于文件**的通道，而非连接运行中应用的实时桥。

### 3.2 运行要求与后端

- Node ≥ 22.5（内置 `node:sqlite`）。
- SQLite 后端选择：**优先 `node:sqlite` 的 `DatabaseSync`**（零依赖、免编译、无需 `--experimental-sqlite`）；失败时回退到 `better-sqlite3`。
  > 背景：本机为 arm64，项目内置的 `better-sqlite3` 二进制是 x86_64，直接加载会 `ERR_DLOPEN_FAILED`。故默认使用 Node 内建的 `node:sqlite`。
- `.ctt` 读取：先嗅探 SQLite 魔数，否则按旧版 JSON 信封解析；写入时清理 `-wal`/`-shm` 旁文件、`PRAGMA journal_mode=WAL` 并在提交后 `wal_checkpoint(TRUNCATE)`。

### 3.3 启动

```bash
npm run mcp        # 启动 MCP 服务器（stdio）
npm run mcp:test   # 端到端冒烟测试（17 断言，含 .ctt 往返）
```

### 3.4 客户端配置

以 Claude Desktop / Cline / Continue 为例，在其 MCP 配置中加入：

```jsonc
{
  "mcpServers": {
    "chemthistry": {
      "command": "node",
      "args": ["/绝对路径/ChemThisTry/mcp/chemthistry-mcp.mjs"]
    }
  }
}
```

### 3.5 工具清单（7 个）

所有工具的路径参数均需**绝对路径**。参数 `*` 为必填。

| 工具 | 作用 | 关键参数 |
|------|------|----------|
| `list_projects` | 列出目录下的 `.ctt` 文件（名/路径/大小/修改时间） | `directory*` |
| `read_project` | 读取工程摘要：工程名 + 所有文档(id/type/name) + 各数据集(列 + 行数) | `file*` |
| `read_sheet` | 读取某数据表的列与值 | `file*` / `sheet*` / `maxRows?`(默认 500) |
| `create_project` | 新建空 `.ctt`（已存在且 `overwrite!=true` 时报错） | `file*` / `projectName?` / `overwrite?` |
| `add_sheet` | 向 `.ctt` 加一张数据表（含列数据） | `file*` / `columns*` / `name?` |
| `add_graph` | 向 `.ctt` 加一张绑定到表的图 | `file*` / `sheet*` / `xColumn*` / `yColumns*` / `chartType?` |
| `export_sheet_csv` | 返回某表的 CSV 文本（表头 + 数据行） | `file*` / `sheet*` |

`columns` 结构与通道 A 一致：`[{ name*, unit?, values*: (number|string)[] }]`。

### 3.6 JSON-RPC 会话示例

```jsonc
// 1. 握手
{"jsonrpc":"2.0","id":1,"method":"initialize"}
// 2. 列工具
{"jsonrpc":"2.0","id":2,"method":"tools/list"}
// 3. 新建工程
{"jsonrpc":"2.0","id":3,"method":"tools/call",
 "params":{"name":"create_project","arguments":{"file":"/tmp/demo.ctt","projectName":"Demo"}}}
// 4. 加表
{"jsonrpc":"2.0","id":4,"method":"tools/call",
 "params":{"name":"add_sheet","arguments":{"file":"/tmp/demo.ctt","name":"Kinetics",
   "columns":[{"name":"t","unit":"s","values":[0,10,20,30,40]},
              {"name":"C","unit":"mM","values":[10,7.4,5.5,4.1,3.0]}]}}}
// 5. 加图
{"jsonrpc":"2.0","id":5,"method":"tools/call",
 "params":{"name":"add_graph","arguments":{"file":"/tmp/demo.ctt","sheet":"Kinetics",
   "xColumn":"t","yColumns":["C"],"chartType":"scatter-line"}}}
```

工具结果封装在 `result.content[0].text`（JSON 字符串）；出错时 `result.isError = true`，`text` 为纯错误文本（非 JSON）。

---

## 4. 通道 C —— 插件 API 与命令

通道 A 的 `list_commands`/`run_command` 之所以能扩展，靠的是插件系统。要新增可被智能体调用的动作，写一个插件并 `registerCommand`。

### 4.1 关键接口（`src/plugins/`）

- `registry.ts`：四个注册表
  - `commandRegistry: Map<id, CommandDef>` —— 命令（菜单/命令面板/程序化）
  - `viewerRegistry: Map<docType, ViewerDef>` —— 文档类型 → 视图组件
  - `exportFormatRegistry` —— 导出格式
  - `menuContribs` —— 原生菜单「Plugins」区
- `runCommand(id, args?)` —— 执行命令；`registerCommand(def)` —— 注册。
- `makeApi()` / `window.ChemThisTry`（`index.ts`）—— 暴露给插件的 API 面。
- 插件示例：`src/plugins/examples/exportJsonPlugin.ts`（命令 id `example:exportJson`）。
- 类型：`src/plugins/types.ts`、`src/plugins/api.d.ts`。

### 4.2 最小插件骨架

```ts
export default {
  id: 'my-plugin',
  activate(api) {
    api.registerCommand({
      id: 'my-plugin:hello',
      title: 'Say Hello',
      run: async (args) => { /* ... 操作 store / 导出 / 弹窗 ... */ },
    })
  },
}
```

注册后，通道 A 的智能体即可 `list_commands` 看到 `my-plugin:hello`，并用 `run_command` 执行。

---

## 5. 底层能力映射（供开发/扩展参考）

智能体工具最终都落到这些运行时原语上。

### 5.1 图表类型（`GraphBinding['chartType']`）

```
scatter, line, scatter-line, step, bar, stacked-bar, area, stacked-area,
histogram, errorbar, scatter3d, surface, box, heatmap, pie, funnel,
bubble, bar-cat
```

### 5.2 拟合模型（Python 侧车 `chem:fit`）

内置：`linear`、`exponential`、`gaussian`、`power`、`logistic` 等；`model="custom"` 时用 `custom` 传自定义表达式（变量 `x`，参数 `a,b,c,...`），如 `a*exp(-b*x)+c`。IPC 封装见 `src/lib/chemFit.ts` 的 `fitCurveIpc(req)`，`FitRequest = { x, y, model, p0?, custom?, name?, fix?, bounds? }`。

### 5.3 zustand Store 原语

- `useProjectStore`：`addDoc(type, name?)`、`addGraphFromSheet(datasetId, xCol, yCols[], chartType, yAxisSide?, errorCols?, dimension?, zCol?, seriesDatasets?)`、`docsByType`、`removeDoc`、`renameDoc`、`setGraphPlot`、`setMolecule`、`setCanvasContent`、`setStructure`。
- `useDatasetStore`：`createDataset`、`getDataset`、`addColumn`、`addRows`、`setCell`、`addFormulaColumn`、`setColumnMeta`、`importText`、`exportCSV`、`rowCount`、`seedKinetics`。
- `useWorkspaceStore`：`openDoc`、`closeDoc`、`splitPane`、`closePane`、`moveTab`。

### 5.4 `.ctt` 工程文件结构

SQLite（better-sqlite3 / node:sqlite），表：
- `meta(key, value)` —— 工程名、主题、版本等；
- `docs(id, ord, json)` —— 每个文档一行；
- `datasets(id, ord, json)` —— 每个数据集一行（`sheet` 的 `doc.id === dataset.id`，1:1）；
- `panes(ord, json)` —— 工作区分屏；载入时至少需要 1 个 pane。

兼容旧版：文件若非 SQLite 魔数，按 JSON 信封解析。定义见 `electron/projectDb.ts`；应用侧再水合见 `src/store/persistence.ts`。

### 5.5 用户首选项（`localStorage: chemthis.userPrefs`）

与工程数据（`.ctt`）和 AI 设置（`chemthis.aiSettings`）分离的**应用级用户偏好**，由 `src/lib/userPrefs.ts` 以单个 JSON blob 读写；载入时对嵌套对象做浅合并回退到默认值。**智能体工具当前不直接读写它**，但扩展命令 / 插件（通道 C）或未来工具可据此读取用户默认。

```ts
interface UserPrefs {
  skipDeleteConfirm: boolean                 // 删除文档时跳过确认
  moleculerControlScheme: 'default' | ...     // Moleculer 3D 交互方案
  graphDefaults: {                            // GraphViewer 新建图的默认外观
    chartType, axisFontSize, axisFontFamily,
    labelFontSize, showLegend, showGrid, palette
  }
  exportDefaults: {                           // 导出默认
    format: 'png'|'svg'|'pdf'|'eps'|'tiff',
    dpi, transparent, embedFonts, marginMm
  }
}
```

- 变更时派发 `PREFS_CHANGED_EVENT`，各面板监听后即时刷新（`saveUserPrefs({ ...getUserPrefs(), ...partial })` 做增量合并，避免覆盖其它分区）。
- `resetUserPrefs(section?)`：不带参数恢复全部，`section` 取 `'general' | 'graph' | 'export'` 时仅恢复对应分区。
- 首选项面板中的「图表默认 / 导出默认 / 快捷键 / 关于」分区即读写该结构；快捷键页为**只读一览**（全局快捷键的展示表，不改键位）。（手机 Web 端隐藏「快捷键」分区，见上文 §2.1 注释。）

---

## 6. 该用哪个通道？

- **在软件里，让助手操作当前工程** → 通道 A（开启 Agent mode）。拥有拟合、统计、命令等全部运行时能力。
- **在软件外，批量/离线生成或读取 `.ctt`**（如 CI、脚本、其它 AI 客户端）→ 通道 B（MCP server）。纯文件操作，无需启动应用。
- **要新增一个可被智能体调用的动作/导出/视图** → 通道 C（写插件 `registerCommand`），随后即可被通道 A 的 `run_command` 调用。

---

## 7. 相关源码索引

| 主题 | 文件 |
|------|------|
| AI 工具层（11 工具 + 分发器） | `src/lib/ai/tools.ts` |
| AI Chat 客户端 + Agent 循环 | `src/lib/aiChat.ts` |
| Agent 模式开关 UI / 首选项面板（分组导航 + 搜索 + 分区恢复默认） | `src/components/settings/PreferencesModal.tsx` |
| 首选项标签页枚举（`PrefTab`） | `src/store/preferencesStore.ts` |
| 用户偏好读写（`UserPrefs` / `resetUserPrefs`） | `src/lib/userPrefs.ts` |
| 内置帮助内容（含「关于」页） | `src/lib/helpContent.ts`、`src/components/help/HelpModal.tsx` |
| MCP 服务器 | `mcp/chemthistry-mcp.mjs` |
| MCP 冒烟测试 | `mcp/smoke-test.mjs` |
| MCP 说明 | `mcp/README.md` |
| 插件注册表 / API | `src/plugins/registry.ts`、`src/plugins/index.ts`、`src/plugins/types.ts` |
| 示例插件 | `src/plugins/examples/exportJsonPlugin.ts` |
| 数据 / 工程 / 工作区 store | `src/store/datasetStore.ts`、`projectStore.ts`、`workspaceStore.ts`、`persistence.ts` |
| 拟合 IPC | `src/lib/chemFit.ts` ｜ 描述统计 `src/lib/stats.ts` |
| `.ctt` 持久化 | `electron/projectDb.ts` |

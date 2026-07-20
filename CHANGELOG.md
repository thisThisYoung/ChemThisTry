# 更新日志 (CHANGELOG)

本文件记录 ChemThisTry 的更新信息，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/) 约定。
格式分类：**新增 (Added)**、**修复 (Fixed)**、**变更 (Changed)**、**早期已完成 (Earlier)**。

---

## [0.1.1] - 2026-07-20

### 新增 (Added)
- **Web 版与移动端预览（手机无需安装即可使用）**：通过 `npm run build:web` 产出纯前端静态网站（`dist-web/`），配合 `vite preview --host` 可在手机浏览器经局域网地址直接打开；亦可部署至 CloudStudio 等静态托管获得公网链接。
- **移动端体验优化**：
  - 手机 Web 端自动跳过欢迎页，直接载入示例工程（Kinetics Example），无需创建工程即可浏览全部模块。
  - 左侧工具箱支持上下滚动；顶部水平工具栏支持左右滑动（隐藏滚动条、touch 平滑滚动），小屏不再因内容过宽而溢出版面。
  - 右上角「文档」按钮改为可再次点击关闭帮助面板（原仅能打开）。
  - 首选项面板在手机端隐藏 AI / 插件 / 快捷键 三个分区，仅保留 通用 / 图表 / 导出 / 关于，避免冗余与桌面专属功能暴露。
- **桌面端自动更新（electron-updater）**：
  - 主进程新增 `electron/update.ts`，基于 `electron-updater` 监听 GitHub Releases 更新源（`publish: github`，owner `thisThisYoung` / repo `ChemThisTry`），通过 `update:status` IPC 向渲染进程推送 检查中 / 已是最新 / 有可用更新 / 下载进度 / 已下载 / 错误 等状态。
  - 渲染端新增 `useUpdateStore`（Zustand）与浮动通知组件 `UpdateNotifier`：检测更新后弹出提示，支持「下载并安装」「稍后」与错误可关闭；Web 端自动禁用（`enabled=false`，不发起任何 IPC，优雅降级）。
  - 首选项「关于」页（AboutTab）新增「检查更新」按钮与状态行：有更新时显示「下载」或「打开下载页」（按平台而异），已下载时显示「重启并安装」或「打开下载页」。
  - 平台策略：Windows（NSIS）与 Linux（AppImage，读取 `APPIMAGE` 环境变量）可就地自动下载安装；**未签名 macOS 与 DEB/RPM 无法自替换**，UI 改为「打开下载页」并跳转对应 GitHub Release Tag（`app:open-release` 校验 `https://` 后 `shell.openExternal`）。首次检查的网络/离线错误被抑制，避免启动即报错。
  - i18n：en / zh-CN / zh-TW 新增 `update.*` 系列键（13 个）；`electron-builder.js` 由 `publish: null` 改为 GitHub 发布源。

### 修复 (Fixed)
- **移动端布局溢出**：系统地加固了从 `app-root` 到各 viewer 主体的整条 `overflow-x` 护栏（约 12 个容器 `max-width:100%; overflow-x:hidden; box-sizing:border-box`），修复 GraphViewer / Moleculer / Canvas 以及顶部主面板的内容溢出；底部面板列宽改为固定比例（42% / 58%）防止 Outliner 把 Properties 挤溢出。
- **移动端欢迎页误显示**：Web 端原本因 `web-bridge` 注入伪 `window.electron` 而误走桌面启动逻辑弹出欢迎页；现改为以真正的 Web 标记 `window.__CTT_IS_WEB__` 判断，Web 端直接进入示例工程。

---

## [未发布] - 2026-07-17

### 新增 (Added)
- **项目管理器支持文件夹树**：左侧 Project Explorer 现可新建文件夹与任意层级的子文件夹；文档按所在文件夹归类，以递归树展示（不再按文档类型分组成扁平列表）。
  - 顶部 `＋ 新建文档` 下拉（sheet / graph / sketch / molecule / canvas 五种类型），新建文档落入当前“活动文件夹”。
  - 顶部 `＋ 新建文件夹`；文件夹行内 `＋` 可建子文件夹；点击文件夹行切换展开/收起，并同时将其设为“活动文件夹”（后续新建项落入其中）。
  - 右键菜单：文件夹支持 重命名 / 新建子文件夹 / 删除；文档支持 重命名 / 关闭标签页 / 删除。
  - 拖拽：文档或文件夹可拖入任意文件夹，或拖到某文档之前按兄弟顺序插入。
  - 保存（`.ctt`）与重载自动保持整个文件夹树结构；旧工程（无 `rootOrder`）自动兼容归一化。
- 数据层：`ProjectFolder { id, name, parentId, childOrder }` 与 `ProjectDoc.folderId`；`useProjectStore` 新增 `addFolder` / `removeFolder`（递归级联删文档并关标签页）/ `renameFolder` / `setDocFolder` / `moveNode`（含后代循环护栏）。
- **Project Explorer 头部重做为 Obsidian 风格**：标题下方（侧栏底部图标栏）为 6 个图标按钮（取代原先头部工具栏与内联排序下拉）。
  - **排序**：单个按钮，点击弹出菜单（标题“排序方式”+ 键列表：手动 / 名称 / 类型 / 创建时间，当前键右侧打勾），分隔线下方“顺序”行提供 ↑升序 / ↓降序（手动模式下禁用）；选择排序键即关闭菜单并生效；弹层现锚定在底部栏上方（`bottom:44px`）。
  - **显示当前文件**：定位当前活动标签页所打开的文档，自动展开其所在文件夹层级、将父文件夹设为活动文件夹，并高亮并滚动到该行（约 1.5s 后取消高亮）。
  - **全部折叠 / 全部展开**：单个切换按钮，标题按状态在两者间切换（所有文件夹均展开时显示折叠图标，否则显示展开图标）。
  - **新建文件夹**：在活动文件夹下新建文件夹并进入重命名（沿用此前底部栏按钮）。
  - **文档 / 偏好设置**：分别打开 Help 与 Preferences 面板（复用 `useHelpStore` / `usePreferencesStore` 的 `setOpen(true)`）。
  - 排序键：手动（默认，保持拖拽顺序）、名称、类型、创建时间；任何排序下文件夹始终置顶（手动按拖拽顺序，其余按名称），其下文档按所选键排序；非手动排序时拖拽重排自动禁用，切回手动恢复。
  - `ProjectDoc` 新增 `createdAt`（毫秒时间戳，新建时写入，旧工程加载默认 0）；`explorerSort { key, dir }` 纳入 `useProjectStore` 并随 `.ctt` 持久化。
  - 7 个语言文件新增 `explorer.sort*` 系列键，以及 `explorer.title / sortBy / sortOrder / showCurrent / collapseAll / expandAll / documentation / preferences`。
- **Project Explorer 底部新增“关系图谱”面板**：Obsidian 风格的网络图，展示文档之间的关联，位于文档树与底部图标栏之间。
  - 可折叠（点击标题栏折叠/展开），且高度可拖拽（顶部拖拽条，范围约 90–480px）；折叠时仅保留标题栏，文档树自动占据剩余空间。
  - 节点为全部文档，按类型着色（与快捷新建栏配色一致）；力导向布局（`force`），支持拖拽节点、滚轮缩放漫游。
  - 边（关联）完全从既有数据派生，无需新增字段：`graph → sheet` 读自 `GraphBinding.datasetId`（回退 `PlotConfig.datasetId`）；`canvas → sketch/molecule/graph` 解析画布 `content` 的 Fabric JSON 中 `linked` 对象的 `sourceDocId` + `sourceType`（`sketcher`/`moleculer`/`graph`）。
  - 当前活动标签页对应的文档节点会高亮（更大尺寸 + 白色描边）；点击任意节点直接打开该文档。
  - 即使文档之间**没有任何关联**，只要存在文档，每个文档仍作为一个节点（点）渲染，不再显示“暂无关联”空态；仅当项目完全没有任何文档时才提示“暂无文档”。
  - 标题改为全大写以与 Project Explorer 其他区块标题统一（如英文 `RELATIONSHIPS`，过长时缩为单词）；样式复用 `.explorer-title` 的 `text-transform: uppercase` + `letter-spacing: 0.5px`。
  - 新增 `src/lib/relGraph.ts`（数据提取助手，含安全解析）与 `src/components/layout/RelGraphPanel.tsx`（ECharts `graph` 系列面板）；7 个语言文件新增 `explorer.relGraph / explorer.relGraphEmpty / explorer.relGraphResize`。
- **关系图谱交互打磨（丝滑度）**：此前切换页面时 `setOption` 使用 `notMerge: true`，力导向布局每次从头重排导致节点“突变/跳动”。现改为**合并模式（merge）**并引入 `posCache` 位置缓存——力导布局稳定后记录各节点坐标，后续更新以缓存坐标作初值重播种，切换活动页/重绘仅平滑过渡（新增 `animationDurationUpdate` / `animationEasingUpdate`），不再整体重排。
- **关系图谱交互修正（用户反馈）**：
  - 拖拽条方向修正：拖拽柄位于面板**顶部**，向上拖应增大面板、向下拖应缩小；原 `+d` 导致边界移动与鼠标方向相反，改为 `-d`，边界随光标移动。
  - 移除标题栏左侧的折叠（快速隐藏）按钮 `▾`/`▸`，面板改为常驻展开（仅保留顶部高度拖拽条与标题）。
  - 节点名称默认不显示，仅在**鼠标悬浮**于该点时才显示（label 默认 `show:false`，`emphasis.label.show:true`）。
  - 打开文档改为**双击**节点（`chart.on('dblclick')`），单击不再触发跳转。
  - 面板顶部补充分隔横线（`border-top`），与底部图标栏风格一致；并移除标题栏残留的 `cursor:pointer`（折叠已去掉）。
- **GraphViewer 属性面板新增“坐标轴截断/断裂（Axis Break）”功能（X / Y）**：2D 模式下在属性面板的图例/网格/对数轴同一组里提供 `Truncate X / Y` 复选框；勾选后展开两个数值输入 **截断起点 (Break from)** 与 **截断终点 (Break to)**，定义要在轴上“跳过的区间”。勾选启用后，该轴被视觉分裂为上下两段、中间绘制锯齿断裂符号（`//`），被截断区间内的数据被压缩跳过，使主体数据放大显示（与 Origin 的 Axis Break 一致），而非单纯裁剪到数据范围。`PlotConfig.truncateX / truncateY` 类型改为 `{ enabled, from, to }`（原 boolean 已移除）；DataViewer 绘图控制台不再显示该开关。此项同时修复了此前把“截断”误解为“范围裁剪到数据极值”的实现。
- **新增雷达图（Radar）**：`chartType` 新增 `radar`。X 列作为雷达各轴（按数据顺序、同值去重），每个被选中的 Y 列成为一条雷达系列；沿用既有 X/Y 选取与图例/标题逻辑。`graphRender.ts` 新增 `buildRadarOption`，并在 `buildGraphOption` 早返回链中接入。
- **GraphViewer 大纲（Outliner）双击跳转源数据**：双击大纲中任意子元素（数据系列 `s:<colId>` / 拟合曲线），自动将工作区切换到该图层来源数据集对应的 DataViewer（系列层支持 `seriesDatasets` 逐系列数据源覆盖）；双击行附带“打开源数据”提示。
- **首选项（Preferences）大幅扩展**：「通用 / AI / 插件」三页升级为「外观 / 图表 / 导出 / AI 与插件 / 关于」分组导航（左侧菜单 + 右侧内容，master-detail），顶部新增**设置搜索框**（按中英文关键词实时过滤分区），每个分区头部带「恢复默认」按钮（图表 / 导出各自按分区重置，关于页「恢复全部默认」）。
  - **图表默认（Graph Defaults）**：默认图表类型、坐标轴字号 / 字体、标签字号、默认色板、图例 / 网格默认开关，持久化到 `localStorage`（嵌套对象与旧数据浅合并，缺字段自动补默认）。
  - **导出默认（Export Defaults）**：默认格式（PNG / SVG / PDF / EPS / TIFF）、DPI、页边距、透明背景、嵌入字体（PDF/EPS），同样持久化并支持分区重置。
  - **快捷键（Shortcuts）页**：表格列出 11 条应用级全局快捷键（命令面板 ⌘/Ctrl+K、打开 / 保存 / 另存、关闭标签、首选项、拆分窗格、主题、文档 F1、缩放等）。
  - **关于（About）页**：显示版本号（取自 `package.json`）、Apache-2.0 许可证、技术栈与贡献指引。
  - 修复 `GeneralTab` 原部分写入会清空新增嵌套字段的隐患，改为与完整首选项合并后写回，并监听 `PREFS_CHANGED_EVENT` 在「恢复全部」后即时同步。
- **Help 帮助文档新增「关于（About）」页**：位于帮助侧边栏，含版本信息（`{{VERSION}}` 运行时由 `package.json` 注入）、官网与源码链接（[GitHub](https://github.com/thisThisYoung/ChemThisTry)）、Apache-2.0 许可证、技术栈、反馈与贡献；GitHub 链接可点击跳转。顺带让帮助文档支持可点击外链（`[文字](https://...)` → 新标签打开，仅限 http/https）。

### 修复 (Fixed)
- **双 Y 轴切换（左→右）缺陷**：此前切换左轴为右轴时，仅 tick 标签随行移动、轴标题不跟随，且水平网格线消失（仅剩竖直网格）。现改为——竖直网格由底部 X 轴持有（不再依赖被置 `splitLine:false` 的右轴），保证双轴时水平线仍可见；右轴标题随系列一同落在右侧（`name` 与 tick 同步到位）。
- **默认四边坐标轴**：上下左右四条坐标轴默认均绘制（边线默认显示）；仅在“承载轴标题”的一边显示 tick 与刻度标签（如底部 X 轴、左/右 Y 轴），无标题的边（默认顶部、无右系列时的右侧）仅显示轴线、隐藏刻度标签，满足“四轴均显示但仅标题所在处显示 ticks”的需求。行为可由 `PlotConfig.axes {top,bottom,left,right}` 微调。
- **关系图谱 sheet 节点配色与图标不一致**：此前 `RelGraphPanel` 的 sheet 节点硬编码蓝色 `#2f6fed`，与项目其他位置（Project Explorer 树、顶栏 New 菜单、命令面板、欢迎页）sheet 图标所用的主题强调色 `var(--accent)` 不一致；其余四类（graph/sketch/molecule/canvas）两处配色恰好相同。现改为运行时解析 `--accent` 作为 sheet 节点色，与图标完全对应，且随主题切换同步。

### 变更 (Changed)
- **移除“新建文档”按钮**：Project Explorer 不再提供通用“新建文档”入口（文档仍可通过欢迎页 / 菜单 / 命令面板 / 各视图内部入口创建）。侧栏底部图标栏现为 6 个按钮：排序 / 显示当前文件 / 全部折叠展开 / 新建文件夹 / 文档 / 偏好设置（头部仅保留标题）。

### 修复 (Fixed)
- **状态栏 Python 指示器**：此前硬编码为“未连接”，现改为挂载时通过 `chem:ping` IPC 探测 sidecar 真实能力（RDKit / SciPy / ASE / CairoSVG），每 20s 复探；连接时显示绿色“● Python: 已连接 <版本>”，未连接显示灰色“○ Python: 未连接”。
- **状态栏“已保存”指示器**：此前硬编码为“已保存”，现改为依据 `useProjectStore` 中 `docs` 的 `modified` 标记真实派生——存在未保存修改时显示琥珀色“● 未保存”，否则绿色“○ 已保存”。
- **文档右键菜单本地化**：原硬编码英文 Rename / Close Tab / Delete 改为 `explorer.renameDoc` / `explorer.closeTab` / `common.delete`，与文件夹菜单保持一致；7 个语言文件均补对应键。
- **文件夹移动逻辑**：修复 `moveNode` 移动文件夹后未同步其 `parentId` 的隐患——该隐患会导致反向移动时被循环护栏沿陈旧 `parentId` 误判为非法（自我后代）而拦截。
- **工程加载类型错误**：修复 `loadProject` 归一化旧工程文档时因 `(v as object)` 展开丢失 `ProjectDoc` 类型导致的 `TS2322` 编译错误。

### 早期已完成 (Earlier)
- `.ctt` 文件关联与双击打开。
- 图片拖入打开（含 SVG 向量导入到当前 Canvas）。
- 语言切换器移至主题右侧。
- 保存后误报“未保存”的问题修复。

---

> 版本号见 `package.json`（`version` 字段）。正式发布时请将“未发布”小节替换为对应版本号与发布日期。

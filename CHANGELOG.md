# 更新日志 (CHANGELOG)

本文件记录 ChemThisTry 的更新信息，遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/) 约定。
格式分类：**新增 (Added)**、**修复 (Fixed)**、**变更 (Changed)**、**早期已完成 (Earlier)**。

***

## [0.1.6] - 2026-10-19

### 新增 (Added)

* **Articler 模块**：新增应用内科研图文文档编辑器。可从分子编辑器、数据图（GraphViewer）、3D 分子（Moleculer）、流程图（FlowViewer）与矢量画布（Canvas）一键插入结果图，并导出为 Word（.docx）文档。

***

## [0.1.5] - 2026-09-01

### 新增 (Added)

* **应用内 Agent「把当前页面作为上下文」开关（默认关闭）**：设置 → AI 新增 `Include current page as context` 选项。开启后，每次与 Agent 对话自动把「当前活动文档（pane）的截图 + 数据摘要」作为上下文附加发送——复用文档切换器缩略图基础设施（`captureViewerThumb` / html2canvas）截图，按文档类型生成数据摘要（表：列名/单位/标签 + 前 30 行；图：标题/图型/轴标题/系列 + 底层数据集摘要；草图/分子：结构文本；画布/流程图：对象/节点数）。与用户手动 ＋ 选取的图片叠加；无活动文档时不发送。详见 `docs/AGENT_GUIDE.md` §2.2。

* **应用内 Help 文档补齐 v0.1.3–0.1.5 功能变动**：Sketcher 新增「渲染与文字」小节（渲染设置浮动面板、字号/字体、单原子 Atom Label、LaTeX 文字、结构操作全链路、键型/取代基/工具栏快捷键）；Canvas 新增「高级编辑」小节（真裁剪、LaTeX 文字、表格工具、绕九宫格参考点旋转、顶点编辑、隔离模式）；Moleculer 新增「多帧轨迹」小节（Gaussian `.out/.log/.gjf`、VASP `XDATCAR/POSCAR/CONTCAR`、多分子 SDF 多帧载入 + 帧滑块/播放/0.2×–20× + 持久化）；键盘快捷键表新增 `Shift+Tab`；Project Explorer 行为说明（光标跟随、文件名净化）；Preferences 补「把当前页面作为上下文」说明。

* **导出到 PowerPoint（插入已打开的演示文稿）**：当前视图可一键导出为 PNG 并插入到已打开的 PowerPoint 演示文稿（macOS 经 AppleScript、Windows 经 Office COM，未运行 PowerPoint 时回退剪贴板），菜单文字统一为「→ PPT」。

* **Project Explorer 框选与右键新建**：文档树空白处拖动可框选（marquee）多个文档；多选文档可整体拖入文件夹移动；右键文档树空白处新增「新建文档」入口。

* **DataViewer 公式、查找替换与对齐**：单元格支持公式/函数计算；新增查找与替换功能；数据单元格文本支持竖直居中对齐；选中单元格按 F2 进入编辑模式。

* **GraphViewer 工具栏工具扩充**：曲线拟合从属性面板移入工具栏工具；新增基线（Baseline）/ 差分（Difference）/ 放大镜（Magnifier）/ 切线（Tangent）/ 文本标注 工具；支持横纵坐标角度（倾斜轴）设置；图例支持单行或单列排列。

* **Sketcher Esc 清除工具**：按 Esc 清除当前选中的绘图工具并返回选择态。

* **Moleculer 图标与导出优化**：加氢原子 / 删除原子、角度 / 二面角图标重做；晶胞粗细随工程持久化；「导出 .mlcl」与「导出结构」合并为统一导出入口。

* **Canvas 文本对齐与大图导出**：文本工具新增对齐选项；明确导出 PNG 尺寸上限并优化大图导出稳定性。

* **ActionTracker 插件**：新增浮层实时显示鼠标点击与键盘按键操作（类 Screencast Keys 风格）。

### 修复 (Fixed)

* **Project Explorer 光标跟随**：新建/导入文档后，Project Explorer 的选中光标自动移动到新文档（高亮选中 + 键盘光标对准 + 必要时展开父文件夹并滚动到可见）。覆盖全部用户主动创建文档的入口——PE 内「新建」菜单（Shift+A）、上方快捷新建栏、File → New、命令面板、欢迎页、File → Import（分子文件）、Sketcher 导出 3D 结构为新分子文档、**拖放文件到窗口**（分子 / 数据文件，与 File → Import 同构）、**控制台运行 Python 生成图表**（新建 sheet + graph 文档）、**画布导出为新 canvas 文档**。实现为 `projectStore` 的跨组件信号 `pendingSelectDocId`（创建入口写入、ProjectExplorer 经 `useEffect` 消费并清零），单一机制统一所有入口。

* **Project Explorer 选中即按 F2 重命名**：选中单个文档或文件夹且焦点位于 Project Explorer 内时按 F2 即可进入行内重命名（此前 F2 仅在右键菜单打开时生效，且要求光标位于 PE 区域）；焦点在画布等其它面板时交给该面板自身的 F2（如画布 Outliner 重命名），互不冲突。`Ctrl/Cmd+F2` 仍保留为批量重命名。

* **System 国际化跟随**：水平菜单栏与撤销历史栈（stack）现已跟随语言切换，不再残留英文文案。

* **Sketcher 顶栏灰色按钮**：修复部分顶部工具栏按钮显示为灰色但实际可点击的视觉/交互不一致问题。

* **DataViewer 编辑体验修复**：修复表头单元格吞掉首个按键输入；Backspace 不再无确认删除选中单元格整行（改为仅清除内容并弹确认）；数据单元格不再因单次点击误入编辑模式（调整为需双击 / Enter 进入编辑）。

* **GraphViewer 主题持久化**：主题设置随工程保存，重新打开自动恢复。

* **Canvas 图片说明导入**：从图片导入到 Canvas 时不再把图片说明（caption）作为文本显示出来。

* **Canvas 大图更新失效**：修复绘制约 12 张图后画布停止更新、「立即更新」按钮无效的问题。

### 变更 (Changed)

* **关系图谱下方提示栏移除**：Project Explorer 底部的 `explorer-selhint` 页脚（含空闲态多选提示与选中态操作指引）已移除，关系图谱下方不再显示任何提示文字。

* **Moleculer 导出入口合并**：「导出 .mlcl」与「导出结构」合并为统一导出入口，减少重复菜单项。

***

## [0.1.4] - 2026-08-28

### 新增 (Added)

* **GraphViewer**: 系列外观新增「纵坐标偏移」(Y Offset) 属性，控制每个系列相对自身纵轴的上下偏移（不改坐标轴范围、不影响其它系列）；复制/粘贴样式天然兼容（随 `seriesStyles` 深拷贝往返）。

* **Project Explorer**: 右键菜单显示快捷键提示并执行——重命名 `F2`、关闭标签页 `⌘/Ctrl+W`、删除 `X`、复制/粘贴 `⌘/Ctrl+C/V`、复制/粘贴样式 `⌘/Ctrl+Shift+C/V`、全选 `⌘/Ctrl+A`（菜单打开时在 `window` 捕获阶段注册、命中即 `stopImmediatePropagation`，避免与全局监听重复触发）。

* **深色主题**: 画布、GraphViewer、DataViewer、Project Explorer 背景统一跟随主题（亮色中性灰 / 暗色深色）；修正 Sketcher 暗黑模式下结构式（碳原子等）因硬编码黑色 SVG 属性而不可见的问题。

* **国际化**: 7 语种（en / zh-CN / zh-TW / ja / fr / es / da）补齐 Y Offset、Project Explorer 快捷键与文档名净化相关键。

### 修复 (Fixed)

* **工程文档名净化**: 单条 / 批量重命名在提交时剔除文件名非法字符（英文冒号 `/ \ : * ? " < > |` 及控制字符）；默认 Kinetics 示例图名由 `Graph 1: Kinetics Example` 修正为 `Graph 1 - Kinetics Example`。

* **GraphViewer 坐标轴**: 用户填写的刻度间隔（xTickStep / yTickStep）落盘到 ECharts `axis.interval` 前加正数守卫——负数取绝对值、0 / 未填回退自动，杜绝非法 interval 导致刻度错乱。

### 变更 (Changed)

* **跨平台桌面构建**: 原生模块 `better-sqlite3` 不能交叉编译，Windows / Linux 安装包须在对应 OS 本机执行 `npm install`（重编原生 `.node`）+ `npm run dist:win` / `npm run dist:linux`（详见 DEPLOY.md §11）；`electron-builder.js` 对 host ≠ target 直接拒绝，除非自备目标平台预编译原生二进制并设置 `CTT_ALLOW_CROSSBUILD=1`。

***

## [0.1.3] - 2026-08-18

### 新增 (Added)

* **System 模块**

  * Shift+Tab 跨窗格循环切换页面（按文档顺序跨 pane 切换，含输入框守卫）。

  * 视口持久化：Canvas 与 GraphViewer 的平移/缩放位置随工程保存，重新打开自动恢复。

  * 直接双击 `.ctt` 打开时自动恢复首个文档标签页（修复 "no document open" 空白）。

  * 撤销历史合并窗口改为手势感知（相邻操作 >50ms 视为新手势先 flush，拖拽爆发仍合并，保留重做）。

  * 控制台（ConsolePanel）桌面端拆为两列：左侧 History 常驻，右侧 Terminal/AI 标签切换；移动端保留原堆叠。

  * 删除快捷键 `X`（无修饰键、非输入态）派发 `ctt:delete-selected`，Canvas / FlowViewer 监听删除选中对象。

* **Sketcher 模块**

  * 可拖动「Render settings」浮动面板（视口内钳制，仅 ✕ 关闭）。

  * 默认渲染字号 18px（经 `editor.setOptions` 设置，避免 `ketcher.setSettings` 丢弃字号）。

  * Apply 保持面板打开；Show Hydrogen Labels 默认 Off。

  * 选中单原子可编辑 Atom Label（受控输入，写入结构）。

  * 文字 / 简单对象经 V3000 molfile 持久化，重载自动往返保留。

  * Canvas 导入的 sketch 改为可编辑 Fabric 组（路径 / 圆 / 文本可在画布内独立编辑）。

* **Canvas / 绘图模块**

  * 钢笔：未选中对象时沿现有路径绘制改为新建锚点，避免误改旧路径。

  * 剪刀：仅光标直接悬停锚点高亮（移除常驻全锚点显示）；剪切时叠加 smart guide。

  * 属性面板九宫格参考点吸附到活动参考点（九点落到网格交点）。

  * 绘图区 smart guide 迟滞防抖、矩形圆角控制点（独立副本防原型污染）、修复「置于底层」被白页遮挡。

  * 消除加载后 world(0,0) 处的幽灵页面标记点（载体矩形强制不可见）。

* **Outliner / Project Explorer**

  * 文档树多选（Ctrl/⌘ 切换、Shift 范围选）；Ctrl/⌘+F2 批量重命名（前缀 + 序号）；`M` 移入当前活动文件夹。

* **成组隔离模式**：双击分组进入隔离模式编辑，提供退出按钮。

* **Moleculer**：多帧时间线（帧滑块 / 播放 / 速度 0.2×–5× / 持久化）已完善。

* **FlowViewer**：连线扇出减少共享 handle 重叠、连接预览改 S 曲线、拖拽跳过 obstacle 重建提性能、`onConnect` 几何选默认锚点。

* **国际化**：7 语种（en / zh-CN / zh-TW / fr / es / ja / da）补齐 v0.1.3 相关键，切换语言无缺失回退。

### 新增 (Added) — 2026-08-12 起追加

* **Canvas 图片「真裁剪」（PPT 式）**：裁剪不再只是遮罩——点「完成」后将裁剪窗口烘焙进图片（写入 `cropX/cropY` + 收缩 `width/height`，缩放不变不拉伸），图片边界框真正收缩到裁剪区域；支持多次累积裁剪、圆角保留、一键「重置裁剪」恢复源图；裁剪可撤销。裁剪框精确覆盖图片（`getCenterPoint` 定位）、手柄拖拽对边固定、工具条跟随裁剪框下方、按钮加大。

* **Canvas 隔离模式扩展**：双击任意对象进入隔离编辑（外部对象变半透明且不可选中），表格单元格文字等可正常编辑，退出按钮返回。

* **Canvas 文字工具支持 LaTeX 公式**：源码实时编辑 + 渲染预览，可随时改回源码；大公式渲染性能优化。

* **Canvas 表格工具**：左侧工具箱 Add 菜单新增「表格」（快捷键 B，行列可配置），表格为单对象 Textbox 方案便于隔离编辑。

* **Canvas 旋转绕九宫格参考点**：属性面板数值 + 画布拖拽手柄统一绕活动参考点旋转（参考点随对象旋转感知）。

* **Canvas direct-select 顶点编辑重构**：锚点/控制点缩小、Shift 跨路径锚点多选、框选只选锚点（去掉整对象蓝框）、圆角把手扩展到多边形/星形。

* **Canvas Outliner 增强**：右键菜单补全（新建文件夹 / 移动 / 复制粘贴 / 删除）、空白处右键「添加图形」、拖入文件夹后把手修复、选中文件夹内对象只选该对象、图层操作不脱离文件夹。

* **Canvas 智能参考线（smart guides）打磨**：吸附滞回死区（Schmitt 触发 + 锁定吸附点）、磁吸抖动根治（stale aCoords 反馈振荡）、对象多时性能优化。

* **Canvas 页面设置弹层分页（Tab）**；删除「出血 + 裁切标记」，透明导出保留。

* **Sketcher 左侧工具箱完整镜像 Ketcher 左栏**：全部分组折叠（flyout 单行展开）、自定义电荷/自由基/双自由基图标、常用分子片段（8 个环）内置、模板库入口。

* **Sketcher 结构操作全链路打通**：芳香化 / 去芳香化 / CIP / 结构检查（Check）/ 计算值（calculated-values）/ 显式氢（explicit-H）全部经 `structService` 直调修通，自建结果弹窗（质量组成逐元素展示）。

* **Sketcher 字体多选下拉**（根治 Ketcher 渲染硬编码字体）、**文字上下标快捷键**（Ctrl/⌘+= 下标、Ctrl/⌘+Shift+= 上标）、下标字号默认=正常字号。

* **Sketcher 键型 / 取代基数字快捷键**：悬停化学键按 `1–5` 就地改键型（单/双/三/楔/虚）、悬停原子按 `0–9` 生长取代基（7=双键氧）、空白处按 `1/2/3` 切换单键/双键/三键工具。

* **Sketcher 其余快捷键**：Space 选中最后操作的分子片段（选择也算操作）、V 键矩形选择（与全局 Shift+Tab 解冲突）、Shift+A 两段式添加。

* **Sketcher 工具栏按钮快捷键标注**：保存 `⌘S`、复制/剪切/粘贴 `⌘C/X/V`、撤销 `⌘Z`、重做 `⌘⇧Z`/`Ctrl+Y`、键型工具 `1/2/3`（mac 显示 ⌘、其他平台 Ctrl+）。

* **Sketcher 文字持久化**（KET 双字段保存）、Atom Label 自定义元素符号、SMILES 加载修通（含坐标重建，杜绝原子塌缩）。

* **Sketcher 设置面板**：移除 Server / 3D Viewer 冗余 Tab、样式下拉移入设置、与画布侧面板布局对齐；缩放速度调优、切页返回画布铺满（修 letterbox 与多余滚动条）。

* **DataViewer Excel 式粘贴**：选中单元格后 Ctrl/⌘+V，剪贴板二维数据（Tab/逗号/分号自动识别）从该格开始填充，越界自动扩展行列，单步撤销（store `pasteRange` 单事务）。

* **DataViewer 自动填充把手**：框选右下角蓝色把手，两格拖动等差填充、一格复制填充；支持向右扩展（新列以首列作基准）；排序/筛选状态不错位（显示行 `row-index`+`col-id` 映射存储行）；拖动时实时高亮将填充区域。

* **DataViewer 编辑体验**：单元格编辑跨应用切换保持（窗口失焦不再退出编辑）、输入中途点击其他单元格先保存当前输入（`onCellEditingStopped` + `newValue` 确定性兜底）。

* **Moleculer 支持 Gaussian 输出**：`.out/.log` 多步优化（Standard/Input orientation 坐标块）= 多帧时间轴、`.gjf` 输入单帧。

* **Moleculer 支持 VASP 输出**：`XDATCAR` 逐离子步解析（Direct 分数坐标×晶格→笛卡尔）= 多帧；`POSCAR/CONTCAR/XDATCAR` 无后缀文件按名称 + 内容嗅探自动识别（文件选择器移除 accept 扩展名过滤）。

* **Moleculer 多分子 SDF**（`$$$$` 分隔）按多帧载入；时间轴播放速度上限提升至 20×。

* **全局撤销体系重做**：DataViewer / Moleculer / GraphViewer 撤销失效修复（移除空撤销处理器拦截，快捷键回退全局历史）；图表配置（`setGraphPlot`）补入撤销栈；菜单 / 命令面板 / 顶栏按钮 / 快捷键的撤销重做统一按当前视图路由（画布与结构式走各自本地栈）；菜单与按钮的可用状态反映当前视图。

* **Canvas 撤销栈大修**：撤销语义修正（一次撤销即生效，自动弹掉「操作后状态」冗余快照）、初始状态入栈、撤销结果持久化（切页/重开不丢）、快速连按不污染栈、异常不再导致撤销永久失效。

* **新建工程向导简化**：不再要求填写工程名称（保存后自动采用文件名；状态栏 `📄 xxx.ctt` 双击仍可改名，同步最近打开列表）。

* **Shift+Tab 切换器**：缩略图修复（DataViewer/Sketcher/FlowViewer 预览、缩放裁切、懒抓取未激活页、Canvas/GraphViewer 捕获优先级）、方向键导航、包含全部项目文档。

* **应用内 AI 新增结构式与 3D 分子操作**：AI Chat 工具 13 → 17，新增 `add_sketch` / `read_sketch`（Sketcher 结构式文档读写，MOLfile V2000 / KET + 视口）与 `add_molecule` / `read_molecule`（Moleculer 3D 分子文档读写，cif/xyz/mol/pdb/sdf/mlcl + view/bonds），创建后自动打开为活动标签页，单步可撤销；与 MCP 同名工具语义一致。

* **其他**：`X` 删除快捷键确认弹窗、标签栏死区消除、DataViewer 预览绕过渲染引擎兼容性问题（Canvas 2D 手绘缩略图）。

### 修复 (Fixed)

* 撤销记录因固定合并窗口导致的连续操作被吞并问题（改为手势感知合并）。

* 双击 `.ctt` 直接打开后内容被欢迎屏遮盖 / 显示空白（统一在 `openProjectByPath` 隐藏欢迎屏 + 渲染端主动拉取路径，race-free）。

* **表格 / 图表 / 分子视图撤销无反应**：DataViewer / Moleculer / GraphViewer 注册的空撤销处理器吞掉快捷键（其修改早已入全局栈却无法撤销）。

* **图表配置永不入撤销栈**：`setGraphPlot` 只写 store 未 push 历史。

* **画布撤销多项**：拖动对象撤销无效、删除需多次、撤销后切页丢失、快速连按错乱、`loadFromJSON` 失败导致撤销与自动保存永久失效。

* **图片裁剪**：裁剪框错位（右下角压住图片中心）、拖手柄对边跟着动、完成后图片被拉伸到原长宽、点「完成」无反应、工具条位置与按钮尺寸。

* **结构式编辑器**：芳香化 / 去芳香化 / 结构检查 / 计算值 / 显式氢点按钮无反应（隐藏工具栏禁用 + `structService` 调用方式）、字体下拉空白、SMILES 加载原子塌缩、切页返回画布两侧空白列 / 多余滚动条、状态栏缩放 % 跳回 100%。

* **数据表**：编辑中途点击别处输入丢失（`cellEditingStopped` 事件字段实为 `newValue`）、切应用后编辑退出（`onBlurCapture` 拦截窗口失焦）、粘贴不生效（document 级 capture 监听）。

* **Shift+Tab 切换器缩略图**：DataViewer/Sketcher/FlowViewer 空白、缩放裁切异常、未激活页无预览、Canvas/GraphViewer 预览不完整、html2canvas 崩溃（AG Grid 不支持 CSS `color(srgb…)`）。

* **其他**：加载后 world(0,0) 幽灵点、标签栏死区、控制台分隔条不可拖动、双 Y 轴切换轴标题不跟随、四边坐标轴 tick 渲染、图表导出样式丢失（`seriesStyles` 缺失）、状态栏 Python/已保存指示器、文档右键菜单本地化、文件夹移动 `parentId` 同步、工程加载类型错误。

***

## [0.1.2] - 2026-08-04

### 新增 (Added)

* **全新流程图插件（FlowViewer）〔重点新增〕**：独立的流程图模块，可作为插件在应用中打开，用于绘制出版级流程图 / 示意框图。基于 `@xyflow/react 12.11.2`，支持节点 / 边编辑、从连接点拉出快捷新建目标节点；排版工具含对齐（左 / 右 / 顶 / 底 / 水平居中 / 竖直居中）、按间距分布（水平 / 垂直）、水平 / 垂直翻转；工具栏按钮悬停显示已绑定快捷键、新增翻转按钮（⌘/Ctrl+Shift+H / V）；导出 Canvas 时箭头改真实 `<path>` 三角、文字补 `dominant-baseline="middle"`；文档配色集中 `src/lib/docColors.ts`（`DOC_TYPE_COLOR`）；非英文界面显示本地化译名。

* **全局撤销 / 重做**：应用级历史栈（`historyStore` 结构化快照 + 250ms 合并窗），覆盖文档增删改、画布对象编辑、图表属性调整等；⌘/Ctrl+Z 撤销、⇧+⌘/Ctrl+Z 重做。

* **DataViewer 数据整理增强**：排序 / 筛选 / 缺失值处理改走自定义对话框写回 `columns[].values`（可撤销）；排序时缺失值恒置末尾，筛选支持多规则 AND，缺失值支持删除行 / 固定值填充 / 均值 / 中位数 / 线性插值（`datasetStore.sortRows` / `filterRows` / `handleMissing`）。

* **GraphViewer 模板系统 + LaTeX 渲染**：① 内置 4 个只读预设模板（`BUILTIN_TEMPLATES`，仅带主题），并支持 localStorage 保存自定义模板（紧凑子集：图表类型 / 维度、系列样式、标题 / 轴标签、图例 / 网格、对数轴、几何与 14 个轴字段），`applyTemplate(...,true)` 重风格化。② 标题与 X/Y 轴名支持 LaTeX（`$...$` → KaTeX → 栅格化注入，PDF/EPS/SVG/PNG 一致）；分类轴刻度标签支持 LaTeX（SVG 渲染器特殊处理、注入 `<image>`）；3D 网格不做轴名 LaTeX。

* **Canvas 9 点参考点（RefPoint）**：模块级参考点系统（9 宫格 `REF_POINTS/REF_FRACTION/REF_POINT_LABEL` + `RefPointPicker`），固定参考点后缩放 / 尺寸编辑锚定该点（兼容 scale 与几何烘焙两条路径），状态存 `localStorage('ctt-canvas-refPoint'，默认 tl)`，7 语言 i18n。

* **Sketcher ACS1996 风格 + CDX 导入**：绘图遵循 ACS 1996 配色与线宽规范；支持导入 `.cdx` / `.cdxml` 矢量结构文件。

* **Moleculer 3D 增强**：① 电荷密度体绘制（volumetric，须 register-then-rebuild 避免被 `removeAllShapes` 清掉）；② 多帧轨迹播放（换结构先 `removeVolumeData`）；③ Cartoon / Ribbon 二级结构（须 `spec.cartoon={ribbon:true}`）；④ 分子表面 SAS / SES / VDW（可调不透明度，默认 0.6）；⑤ orthographic 投影 + 仅 CIF 扩胞 + 透明背景，导出 PNG ≤4096²。

* **新建工程向导模板扩充**：`StartWizard` 新增 结构编辑器(Sketcher) / 分子视图(Moleculer) / 画布(Canvas) 三个首页模板，与「空白」「动力学示例」并列共 5 个起始模板（`src/lib/startProjects.ts`）。

* **工具栏 / 工具箱快捷键提示**：Canvas 与 Flow 工具栏按钮 tooltip 显示已绑定快捷键，格式 `名称（键）`（半角括号）；FlowViewer 新增翻转按钮（Ctrl/⌘+Shift+H/V），复用 `canvas.flipHorizontal/Vertical` i18n；新增 `canvas.curvature` 等键（7 语言）。

* **应用内 AI Chat 多模态图片上传**：控制台 AI 标签页 ImagePlus 按钮、一次多选；待发缩略图可逐个移除；发送时浏览器端降采样（最长边 ≤1568px、转 JPEG 0.8）后以多模态片段随消息发出，普通流式与 Agent 工具循环两路径均支持；用户气泡回显图片、支持「仅发图」。需视觉模型（如 `gpt-4o`）。`ChatMessage.images` / `send(text, images?, onStream?)` / `toApiContent` / `readImageFile`。

* **通道 A（应用内 AI Chat）Canvas 工具**：`src/lib/ai/tools.ts` 工具 11 → 13，新增 `add_canvas`（建画布并可选写入 Fabric JSON、自动打开）与 `read_canvas`（按 id/name 读内容与对象数），走运行中 store（`addDoc` / `setCanvasContent` / `openDoc`）。

* **MCP 暴露 Canvas**：`mcp/chemthistry-mcp.mjs` 工具 13 → 15，新增 `add_canvas` / `read_canvas`（读写 `.ctt`，与通道 A 同名语义一致但后端不同）；冒烟测试 32 断言通过。

* **应用内 Help「Image Upload」小节**：英文源 + 6 语言译文（zh-CN / zh-TW / fr / es / ja / da）的 AI Chat 章节补图片上传说明。

### 修复 (Fixed)

* **Shift+A 按光标区域分流**：改用 `getRegionAtPoint` / `getRegionUnderPointer` 在按键瞬间实时命中测试光标位置（不再用 `getActiveRegion()`，hover 不刷新），修复悬停误判弹错菜单。

* **流程图图标颜色一致化**：抽出 `DOC_TYPE_COLOR`（`docColors.ts`），项目管理器树与关系图谱共用，Flow 两边均为 `#5b6bd6`。

* **动力学示例 GraphViewer 空白**：按列 **id** 绑定（原误用列名导致曲线 / 误差棒解析失败）。

* **分布算法改为按间距(gap)均分**：首尾物体边缘锚定、中间等间隙铺开，修复大小不一时「中点均分」间隙不均；Canvas `distribute` 与 Flow `distributeNodes` 两处统一（修正 Flow 的 off-by-one）。

* **工具栏补齐快捷键 + Flow 翻转按钮**：Canvas / Flow 工具栏按钮 title 显示已绑定快捷键（单一来源拼接，避免不一致）；FlowViewer 新增翻转按钮（Ctrl/⌘+Shift+H/V）。

### 变更 (Changed)

* **Canvas 文本格式栏移除「加粗斜体（B/I）」独立按钮**：加粗 + 斜体组合表达，移除后 B/I 各自高亮。

* **Moleculer「标准右手视图」换图标**：`RotateCcw` → `Axis3d`（3D 坐标轴），与「重置视图」区分。

* **流程图节点连接快捷新建菜单移除「表格」**：过滤 `table`（流程图节点无意义）。

* **分组柱状图 UI 入口移除**：builder / 类型保留以兼容旧档。

### 早期已完成 (Earlier)

* `.ctt` 文件关联与双击打开。

* 图片拖入打开（含 SVG 向量导入到当前 Canvas）。

* 语言切换器移至主题右侧。

* 保存后误报「未保存」修复。

## [0.1.1] - 2026-07-20

### 新增 (Added)

* **Web 版与移动端预览（手机无需安装即可使用）**：通过 `npm run build:web` 产出纯前端静态网站（`dist-web/`），配合 `vite preview --host` 可在手机浏览器经局域网地址直接打开；亦可部署至 CloudStudio 等静态托管获得公网链接。

* **移动端体验优化**：

  * 手机 Web 端自动跳过欢迎页，直接载入示例工程（Kinetics Example），无需创建工程即可浏览全部模块。

  * 左侧工具箱支持上下滚动；顶部水平工具栏支持左右滑动（隐藏滚动条、touch 平滑滚动），小屏不再因内容过宽而溢出版面。

  * 右上角「文档」按钮改为可再次点击关闭帮助面板（原仅能打开）。

  * 首选项面板在手机端隐藏 AI / 插件 / 快捷键 三个分区，仅保留 通用 / 图表 / 导出 / 关于，避免冗余与桌面专属功能暴露。

* **桌面端自动更新（electron-updater）**：

  * 主进程新增 `electron/update.ts`，基于 `electron-updater` 监听 GitHub Releases 更新源（`publish: github`，owner `thisThisYoung` / repo `ChemThisTry`），通过 `update:status` IPC 向渲染进程推送 检查中 / 已是最新 / 有可用更新 / 下载进度 / 已下载 / 错误 等状态。

  * 渲染端新增 `useUpdateStore`（Zustand）与浮动通知组件 `UpdateNotifier`：检测更新后弹出提示，支持「下载并安装」「稍后」与错误可关闭；Web 端自动禁用（`enabled=false`，不发起任何 IPC，优雅降级）。

  * 首选项「关于」页（AboutTab）新增「检查更新」按钮与状态行：有更新时显示「下载」或「打开下载页」（按平台而异），已下载时显示「重启并安装」或「打开下载页」。

  * 平台策略：Windows（NSIS）与 Linux（AppImage，读取 `APPIMAGE` 环境变量）可就地自动下载安装；**未签名 macOS 与 DEB/RPM 无法自替换**，UI 改为「打开下载页」并跳转对应 GitHub Release Tag（`app:open-release` 校验 `https://` 后 `shell.openExternal`）。首次检查的网络/离线错误被抑制，避免启动即报错。

  * i18n：en / zh-CN / zh-TW 新增 `update.*` 系列键（13 个）；`electron-builder.js` 由 `publish: null` 改为 GitHub 发布源。

* **项目管理器支持文件夹树**：左侧 Project Explorer 现可新建文件夹与任意层级的子文件夹；文档按所在文件夹归类，以递归树展示（不再按文档类型分组成扁平列表）。

  * 顶部 `＋ 新建文档` 下拉（sheet / graph / sketch / molecule / canvas 五种类型），新建文档落入当前“活动文件夹”。

  * 顶部 `＋ 新建文件夹`；文件夹行内 `＋` 可建子文件夹；点击文件夹行切换展开/收起，并同时将其设为“活动文件夹”（后续新建项落入其中）。

  * 右键菜单：文件夹支持 重命名 / 新建子文件夹 / 删除；文档支持 重命名 / 关闭标签页 / 删除。

  * 拖拽：文档或文件夹可拖入任意文件夹，或拖到某文档之前按兄弟顺序插入。

  * 保存（`.ctt`）与重载自动保持整个文件夹树结构；旧工程（无 `rootOrder`）自动兼容归一化。

* 数据层：`ProjectFolder { id, name, parentId, childOrder }` 与 `ProjectDoc.folderId`；`useProjectStore` 新增 `addFolder` / `removeFolder`（递归级联删文档并关标签页）/ `renameFolder` / `setDocFolder` / `moveNode`（含后代循环护栏）。

* **Project Explorer 头部重做为 Obsidian 风格**：标题下方（侧栏底部图标栏）为 6 个图标按钮（取代原先头部工具栏与内联排序下拉）。

  * **排序**：单个按钮，点击弹出菜单（标题“排序方式”+ 键列表：手动 / 名称 / 类型 / 创建时间，当前键右侧打勾），分隔线下方“顺序”行提供 ↑升序 / ↓降序（手动模式下禁用）；选择排序键即关闭菜单并生效；弹层现锚定在底部栏上方（`bottom:44px`）。

  * **显示当前文件**：定位当前活动标签页所打开的文档，自动展开其所在文件夹层级、将父文件夹设为活动文件夹，并高亮并滚动到该行（约 1.5s 后取消高亮）。

  * **全部折叠 / 全部展开**：单个切换按钮，标题按状态在两者间切换（所有文件夹均展开时显示折叠图标，否则显示展开图标）。

  * **新建文件夹**：在活动文件夹下新建文件夹并进入重命名（沿用此前底部栏按钮）。

  * **文档 / 偏好设置**：分别打开 Help 与 Preferences 面板（复用 `useHelpStore` / `usePreferencesStore` 的 `setOpen(true)`）。

  * 排序键：手动（默认，保持拖拽顺序）、名称、类型、创建时间；任何排序下文件夹始终置顶（手动按拖拽顺序，其余按名称），其下文档按所选键排序；非手动排序时拖拽重排自动禁用，切回手动恢复。

  * `ProjectDoc` 新增 `createdAt`（毫秒时间戳，新建时写入，旧工程加载默认 0）；`explorerSort { key, dir }` 纳入 `useProjectStore` 并随 `.ctt` 持久化。

  * 7 个语言文件新增 `explorer.sort*` 系列键，以及 `explorer.title / sortBy / sortOrder / showCurrent / collapseAll / expandAll / documentation / preferences`。

* **Project Explorer 底部新增“关系图谱”面板**：Obsidian 风格的网络图，展示文档之间的关联，位于文档树与底部图标栏之间。

  * 可折叠（点击标题栏折叠/展开），且高度可拖拽（顶部拖拽条，范围约 90–480px）；折叠时仅保留标题栏，文档树自动占据剩余空间。

  * 节点为全部文档，按类型着色（与快捷新建栏配色一致）；力导向布局（`force`），支持拖拽节点、滚轮缩放漫游。

  * 边（关联）完全从既有数据派生，无需新增字段：`graph → sheet` 读自 `GraphBinding.datasetId`（回退 `PlotConfig.datasetId`）；`canvas → sketch/molecule/graph` 解析画布 `content` 的 Fabric JSON 中 `linked` 对象的 `sourceDocId` + `sourceType`（`sketcher`/`moleculer`/`graph`）。

  * 当前活动标签页对应的文档节点会高亮（更大尺寸 + 白色描边）；点击任意节点直接打开该文档。

  * 即使文档之间**没有任何关联**，只要存在文档，每个文档仍作为一个节点（点）渲染，不再显示“暂无关联”空态；仅当项目完全没有任何文档时才提示“暂无文档”。

  * 标题改为全大写以与 Project Explorer 其他区块标题统一（如英文 `RELATIONSHIPS`，过长时缩为单词）；样式复用 `.explorer-title` 的 `text-transform: uppercase` + `letter-spacing: 0.5px`。

  * 新增 `src/lib/relGraph.ts`（数据提取助手，含安全解析）与 `src/components/layout/RelGraphPanel.tsx`（ECharts `graph` 系列面板）；7 个语言文件新增 `explorer.relGraph / explorer.relGraphEmpty / explorer.relGraphResize`。

* **关系图谱交互打磨（丝滑度）**：此前切换页面时 `setOption` 使用 `notMerge: true`，力导向布局每次从头重排导致节点“突变/跳动”。现改为**合并模式（merge）**并引入 `posCache` 位置缓存——力导布局稳定后记录各节点坐标，后续更新以缓存坐标作初值重播种，切换活动页/重绘仅平滑过渡（新增 `animationDurationUpdate` / `animationEasingUpdate`），不再整体重排。

* **关系图谱交互修正（用户反馈）**：

  * 拖拽条方向修正：拖拽柄位于面板**顶部**，向上拖应增大面板、向下拖应缩小；原 `+d` 导致边界移动与鼠标方向相反，改为 `-d`，边界随光标移动。

  * 移除标题栏左侧的折叠（快速隐藏）按钮 `▾`/`▸`，面板改为常驻展开（仅保留顶部高度拖拽条与标题）。

  * 节点名称默认不显示，仅在**鼠标悬浮**于该点时才显示（label 默认 `show:false`，`emphasis.label.show:true`）。

  * 打开文档改为**双击**节点（`chart.on('dblclick')`），单击不再触发跳转。

  * 面板顶部补充分隔横线（`border-top`），与底部图标栏风格一致；并移除标题栏残留的 `cursor:pointer`（折叠已去掉）。

* **GraphViewer 属性面板新增“坐标轴截断/断裂（Axis Break）”功能（X / Y）**：2D 模式下在属性面板的图例/网格/对数轴同一组里提供 `Truncate X / Y` 复选框；勾选后展开两个数值输入 **截断起点 (Break from)** 与 **截断终点 (Break to)**，定义要在轴上“跳过的区间”。勾选启用后，该轴被视觉分裂为上下两段、中间绘制锯齿断裂符号（`//`），被截断区间内的数据被压缩跳过，使主体数据放大显示（与 Origin 的 Axis Break 一致），而非单纯裁剪到数据范围。`PlotConfig.truncateX / truncateY` 类型改为 `{ enabled, from, to }`（原 boolean 已移除）；DataViewer 绘图控制台不再显示该开关。此项同时修复了此前把“截断”误解为“范围裁剪到数据极值”的实现。

* **新增雷达图（Radar）**：`chartType` 新增 `radar`。X 列作为雷达各轴（按数据顺序、同值去重），每个被选中的 Y 列成为一条雷达系列；沿用既有 X/Y 选取与图例/标题逻辑。`graphRender.ts` 新增 `buildRadarOption`，并在 `buildGraphOption` 早返回链中接入。

* **GraphViewer 大纲（Outliner）双击跳转源数据**：双击大纲中任意子元素（数据系列 `s:<colId>` / 拟合曲线），自动将工作区切换到该图层来源数据集对应的 DataViewer（系列层支持 `seriesDatasets` 逐系列数据源覆盖）；双击行附带“打开源数据”提示。

* **首选项（Preferences）大幅扩展**：「通用 / AI / 插件」三页升级为「外观 / 图表 / 导出 / AI 与插件 / 关于」分组导航（左侧菜单 + 右侧内容，master-detail），顶部新增**设置搜索框**（按中英文关键词实时过滤分区），每个分区头部带「恢复默认」按钮（图表 / 导出各自按分区重置，关于页「恢复全部默认」）。

  * **图表默认（Graph Defaults）**：默认图表类型、坐标轴字号 / 字体、标签字号、默认色板、图例 / 网格默认开关，持久化到 `localStorage`（嵌套对象与旧数据浅合并，缺字段自动补默认）。

  * **导出默认（Export Defaults）**：默认格式（PNG / SVG / PDF / EPS / TIFF）、DPI、页边距、透明背景、嵌入字体（PDF/EPS），同样持久化并支持分区重置。

  * **快捷键（Shortcuts）页**：表格列出 11 条应用级全局快捷键（命令面板 ⌘/Ctrl+K、打开 / 保存 / 另存、关闭标签、首选项、拆分窗格、主题、文档 F1、缩放等）。

  * **关于（About）页**：显示版本号（取自 `package.json`）、Apache-2.0 许可证、技术栈与贡献指引。

  * 修复 `GeneralTab` 原部分写入会清空新增嵌套字段的隐患，改为与完整首选项合并后写回，并监听 `PREFS_CHANGED_EVENT` 在「恢复全部」后即时同步。

* **Help 帮助文档新增「关于（About）」页**：位于帮助侧边栏，含版本信息（`{{VERSION}}` 运行时由 `package.json` 注入）、官网与源码链接（[GitHub](https://github.com/thisThisYoung/ChemThisTry)）、Apache-2.0 许可证、技术栈、反馈与贡献；GitHub 链接可点击跳转。顺带让帮助文档支持可点击外链（`[文字](https://...)` → 新标签打开，仅限 http/https）。

### 修复 (Fixed)

* **移动端布局溢出**：系统地加固了从 `app-root` 到各 viewer 主体的整条 `overflow-x` 护栏（约 12 个容器 `max-width:100%; overflow-x:hidden; box-sizing:border-box`），修复 GraphViewer / Moleculer / Canvas 以及顶部主面板的内容溢出；底部面板列宽改为固定比例（42% / 58%）防止 Outliner 把 Properties 挤溢出。

* **移动端欢迎页误显示**：Web 端原本因 `web-bridge` 注入伪 `window.electron` 而误走桌面启动逻辑弹出欢迎页；现改为以真正的 Web 标记 `window.__CTT_IS_WEB__` 判断，Web 端直接进入示例工程。

* **双 Y 轴切换（左→右）缺陷**：此前切换左轴为右轴时，仅 tick 标签随行移动、轴标题不跟随，且水平网格线消失（仅剩竖直网格）。现改为——竖直网格由底部 X 轴持有（不再依赖被置 `splitLine:false` 的右轴），保证双轴时水平线仍可见；右轴标题随系列一同落在右侧（`name` 与 tick 同步到位）。

* **默认四边坐标轴**：上下左右四条坐标轴默认均绘制（边线默认显示）；仅在“承载轴标题”的一边显示 tick 与刻度标签（如底部 X 轴、左/右 Y 轴），无标题的边（默认顶部、无右系列时的右侧）仅显示轴线、隐藏刻度标签，满足“四轴均显示但仅标题所在处显示 ticks”的需求。行为可由 `PlotConfig.axes {top,bottom,left,right}` 微调。

* **关系图谱 sheet 节点配色与图标不一致**：此前 `RelGraphPanel` 的 sheet 节点硬编码蓝色 `#2f6fed`，与项目其他位置（Project Explorer 树、顶栏 New 菜单、命令面板、欢迎页）sheet 图标所用的主题强调色 `var(--accent)` 不一致；其余四类（graph/sketch/molecule/canvas）两处配色恰好相同。现改为运行时解析 `--accent` 作为 sheet 节点色，与图标完全对应，且随主题切换同步。

* **GraphViewer 导出样式丢失（桌面端/Web 端）**：此前在 GraphViewer 中修改系列样式（颜色 / 线型 / 线宽 / 标记）后导出，导出文件仍使用默认样式。根因为导出用的 `currentPlotConfig()` 返回值缺失 `seriesStyles` 字段，导出路径重建 ECharts 实例时该字段为 `undefined` 从而回退到默认调色板与线型；而屏幕渲染走的是携带 `seriesStyles` 的内联 `plotConfig`，故屏幕显示正常。已将其补回 `currentPlotConfig()` 返回值，现 2D 的 SVG / EPS / PDF / PNG 导出与屏幕样式完全一致（画布导出与 3D 导出走屏幕实例 `getDataURL`，本就不受影响）。

* **状态栏 Python 指示器**：此前硬编码为“未连接”，现改为挂载时通过 `chem:ping` IPC 探测 sidecar 真实能力（RDKit / SciPy / ASE / CairoSVG），每 20s 复探；连接时显示绿色“● Python: 已连接 <版本>”，未连接显示灰色“○ Python: 未连接”。

* **状态栏“已保存”指示器**：此前硬编码为“已保存”，现改为依据 `useProjectStore` 中 `docs` 的 `modified` 标记真实派生——存在未保存修改时显示琥珀色“● 未保存”，否则绿色“○ 已保存”。

* **文档右键菜单本地化**：原硬编码英文 Rename / Close Tab / Delete 改为 `explorer.renameDoc` / `explorer.closeTab` / `common.delete`，与文件夹菜单保持一致；7 个语言文件均补对应键。

* **文件夹移动逻辑**：修复 `moveNode` 移动文件夹后未同步其 `parentId` 的隐患——该隐患会导致反向移动时被循环护栏沿陈旧 `parentId` 误判为非法（自我后代）而拦截。

* **工程加载类型错误**：修复 `loadProject` 归一化旧工程文档时因 `(v as object)` 展开丢失 `ProjectDoc` 类型导致的 `TS2322` 编译错误。

### 变更 (Changed)

* **移除“新建文档”按钮**：Project Explorer 不再提供通用“新建文档”入口（文档仍可通过欢迎页 / 菜单 / 命令面板 / 各视图内部入口创建）。侧栏底部图标栏现为 6 个按钮：排序 / 显示当前文件 / 全部折叠展开 / 新建文件夹 / 文档 / 偏好设置（头部仅保留标题）。

***

> 版本号见 `package.json`（`version` 字段）。新功能开发期间请累积在对应版本的"未发布"小节；正式发布时将该小节标题替换为版本号与发布日期。


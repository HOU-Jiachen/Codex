# 水土保持报告 Agent 运行逻辑与功能简介

## 1 定位

本 agent 面向生产建设项目水土保持方案报告书/报告表编制，核心目标是把项目资料、规范依据、工程量、预测参数、措施和投资数据转化为可排版的 Word 报告。

## 2 输入资料位置

- 项目根目录：可放置本项目专用资料，如批复、主体设计、最终报告、合同、图纸说明、Word/PDF 文档等。
- `projects/<项目简称>/raw/`：推荐的项目隔离资料目录，用于多项目运行。
- `standards_templates/`：放置长期复用的水土保持规范、标准、地方文件、报告模板和优秀样例。
- `.agents/skills/engineering_report/knowledge/`：可放置长期复用资料，如水土保持规划、公报、规范依据、地方文件、常用模板资料等。
- `PROJECT_CONTEXT_OVERRIDE.md`：可选人工修正文件，用于补充或覆盖自动抽取结果；不要直接手写 `PROJECT_CONTEXT.md`。
- `PROJECT_CONTEXT_OVERRIDE.example.md`：人工补充模板。复制为 `PROJECT_CONTEXT_OVERRIDE.md` 后填写，字段优先级高于自动抽取结果。

## 3 核心运行流程

1. 自动读取 `DATA_COLLECTION_CHECKLIST.md`，明确报告生成所需资料清单。
2. 运行 `context_builder.py`，扫描根目录、`standards_templates/` 和 `knowledge/` 中的 PDF、DOCX、TXT、MD。
2.1 如更新了报告模板，运行 `template_profile_builder.py` 提取模板章节结构；扫描版模板需先 OCR。
3. 自动生成：
   - `PROJECT_CONTEXT.md`：项目自动上下文，含关键字段、资料覆盖度和证据摘录。
   - `PROJECT_CONTEXT_SOURCES.json`：结构化来源、字段、覆盖度和预检查状态。
   - `MATERIAL_GAP_REPORT.md`：资料缺口预检查报告。
4. 读取 `PROJECT_CONTEXT_SOURCES.json` 中的 `preflight`。
5. 若 `preflight.blocked = true`，暂停生成，向用户展示缺失资料清单，并让用户选择：
   - `继续运行`：生成缺失标注版初稿。
   - `补充材料`：暂停生成，并提示优先/次要补充资料。
6. 若资料满足要求，或用户选择继续运行，则读取 `chapter_gates.json` 执行章节级门禁。
7. 运行 `report_generator.py`，由 `PROJECT_CONTEXT_SOURCES.json` 自动生成 `temp_report.json`。
8. 等待用户确认 `Y` 后，运行 `docx_builder.py`，根据 Word 模板样式生成 `output_report.docx`。

## 4 关键能力

- 自动抽取项目关键字段：项目名称、项目代码、建设单位、地点、占地、土石方、侵蚀模数、预测流失量、投资等。
- 自动判断资料完备性：识别核心资料缺失、次要资料缺失和关键字段缺失。
- 自动识别需要 OCR 的扫描版或不可抽字 PDF，并写入资料缺口报告。
- 自动生成补料建议：区分优先补充资料和次要补充资料。
- 严格缺失拦截：缺少硬核数据时不编造，转为显式缺失标注。
- 局部缺失标注：章节内能写的部分先写，缺少的字段、表格或小节在对应位置标注，不整章跳过。
- 样式驱动排版：`temp_report.json` 中的中文样式名映射 Word 模板样式。
- 标题不手工编号：标题一至标题四由 Word 模板多级列表自动编号。

## 5 常用命令

```bash
python .agents/skills/engineering_report/project_manager.py 项目简称
python .agents/skills/engineering_report/template_profile_builder.py
python .agents/skills/engineering_report/context_builder.py
python .agents/skills/engineering_report/report_generator.py
python .agents/skills/engineering_report/docx_builder.py
```

## 6 重要规则

- 不要把 `PROJECT_CONTEXT.md` 当作人工主写文件，它会被自动覆盖。
- 扫描版规范、模板 PDF 必须先 OCR，不能把无法抽字的 PDF 当作可引用依据。
- 人工补充内容写入 `PROJECT_CONTEXT_OVERRIDE.md`。
- 人工补充内容优先级高于自动抽取内容。
- 报告中的数字必须有资料来源。
- 资料不足时必须暂停并让用户选择，不得直接冒充完整报批稿。
- 成品 Word 生成前必须等待用户明确回复 `Y`。

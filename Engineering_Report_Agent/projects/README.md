# 项目隔离目录

每个水土保持方案项目建议单独建立一个子目录，避免不同项目资料互相污染。

推荐结构：

```text
projects/
  项目简称/
    raw/        原始资料：批复、主体设计、合同、图纸说明、PDF、DOCX 等
    override/   人工修正资料，可放 PROJECT_CONTEXT_OVERRIDE.md
    work/       自动生成的 PROJECT_CONTEXT.md、SOURCES.json、缺口报告等
    output/     temp_report.json、output_report.docx 等成果
```

使用规则：

- 新项目资料优先放入 `projects/<项目简称>/raw/`。
- 长期复用规范、标准和模板放入根目录 `standards_templates/`。
- 若未指定项目目录，脚本仍兼容扫描项目根目录。
- 自动生成文件不应放入 `raw/`，避免被下次识别为原始资料。


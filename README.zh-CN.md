# Python + Playwright Locator 自愈辅助工具

本项目实现自动化测试失败现场采集、定位器修复建议、Claude Code Hook/Skill 编排，以及人工确认后的最小修改。**当前不是完全自主修复系统**：工具默认只提出建议，不会自动覆盖业务脚本。

## 环境安装

建议 Python 3.10 以上：

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium
```

## 运行示例

```bash
python tools/heal_runner.py examples/passing.py
python tools/heal_runner.py examples/failing_locator.py
python tools/heal_runner.py examples/failing_assertion.py
python tools/repair_locator.py examples/_healing/failing_locator/bundle.json
pytest -q
```

- `passing.py`：应正常通过。
- `failing_locator.py`：故意使用错误的日语按钮名称，失败后保存 `bundle.json`、`aria_snapshot.yaml`、`screenshot.png`、`traceback.txt`。
- `failing_assertion.py`：故意触发业务断言失败；不应使用 Locator 自愈方式掩盖。
- `repair_locator.py`：根据快照与源码生成 Locator 修改建议。**必须人工确认实际页面匹配、语义正确后才可应用。**

如果确实要应用建议，把命令输出保存成 `proposal.json`，再运行：

```bash
python tools/apply_repair.py examples/failing_locator.py proposal.json --approve
```

注意：这会让故意失败的样例不再保持失败，通常应在单独副本或分支中演示。

## 工作流程

Claude Code 的 `.claude/settings.json` 为 Bash 命令注册 PostToolUse Hook，检查失败输出并提示读取 `.claude/skills/heal-locators/SKILL.md`。Skill 规范分为 Phase 0–8：执行、诊断、实时验证（可选）、修复、横向检查、复测、日志与报告、Git 操作、规则改进。

## 限制与安全

- 浏览器关闭后可能无法采集快照；失败样例通过 `capture_in_context` 在关闭前保存现场。
- 不默认开放 CDP 9222 端口，不随意 Monkey Patch Playwright 私有实现。
- 修复建议仅支持简单单行 `get_by_role('button', name='...')`，复杂 Locator 需人工分析。
- 绝不自动修改断言、业务数据、等待时间或 URL；不自动推送到 main。
- `_healing/` 已被 `.gitignore` 排除；不要上传账号、Cookie、截图中的敏感数据。

## 一键诊断与可选自愈（默认不修改代码）

```bash
python tools/heal_pipeline.py examples/failing_locator.py
# 先查看建议并验证它确实是目标按钮，再明确批准修改：
python tools/heal_pipeline.py examples/failing_locator.py --apply
python -m pytest -q
```

默认执行为 **Dry Run**，只采集失败现场、分析并打印修复建议。`--apply` 是明确授权：仅对快照中只有一个按钮、且可识别的单行 `get_by_role('button', name=...)` 做最小替换；执行后自动复测，失败会恢复原文件。**演示前建议复制 `failing_locator.py`，避免破坏故意失败的示例。** 真实应用中的语义、业务含义及目标唯一性仍需要审核。

可查阅 [设计改进与原因](docs/IMPROVEMENTS.md)。自动化范围刻意受限，尚不能保证任意网页的 Locator 自愈。

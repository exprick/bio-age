---
name: bio-age
description: "用 LLM 推断生理年龄并生成可分享的 PDF + JPG 报告。**默认 blind 模式**：抹掉用户的真实年龄，让模型纯靠生物标志物推断 7 器官年龄 + 反猜实际年龄（用户对比反猜结果即可判断准确度）。复现 Nature Medicine 2025 论文方法：纯 zero-shot prompt + 自然语言体检 → overall + 心血管/肝/肺/肾/代谢/肌骨。Cross-vendor — Claude Code / Codex / OpenClaw 都可用，谁调用谁推理。Use when user provides 体检报告 / 化验单 / blood panel / 健康档案 + asks 生理年龄 / biological age / 器官年龄 / 推断年龄 / 抗衰评估 / aging analysis. Outputs HTML + PDF + JPG cards (适合发朋友圈 / X / 小红书). Trigger words: 生理年龄, biological age, 器官年龄, 抗衰, organ age, aging biomarkers, LLM-Aging, 体检解读, 体检报告分析, blind age, 盲测年龄, age estimation, PDF 报告, JPG 卡片."
version: "1.2.0"
user_invocable: true
---

# bio-age

LLM-based 生理年龄推断 — cross-vendor skill。给一份体检报告，**默认隐藏真实年龄**让模型盲推 → 输出 7 器官年龄 + 反猜的实际年龄 + 推理。生成 HTML + PDF + 一组 JPG 卡片，可直接发社交媒体。

## 三个出处（全部进 footer，缺一不可）

1. **方法**：Sun et al. (2025) *A large language model approach for biological age estimation and aging intervention.* Nature Medicine. https://www.nature.com/articles/s41591-025-03856-8
2. **Skill**：https://github.com/exprick/bio-age (MIT)

## 何时调用

- 用户给体检 / 化验单 / 健康档案 → 问"生理年龄 / 器官年龄"
- 用户问"模型猜得准不准 / 不告诉年龄会怎样" → blind 模式天然解决
- 用户要 PDF / JPG / 图片 / 朋友圈分享物料

## 默认行为：blind

`bio-age <input.txt>` 不带 mode 时**默认 blind**：
- 抹掉年龄 / 生日 / 时间锚点
- 让当前 agent（Claude / Codex / OpenClaw 都行）作为 LLM 自行推理
- 输出包含**反猜的实际年龄**——这是准确度凭证（用户拿真实年龄一比就知道）

仍可显式：
- `--mode standard` 公开年龄运行（论文复现 / 对比 anchoring effect）
- `--mode trend` 多时点对比（少见用途）

## 调用流程

### A. 当前 session 自己推理（推荐 — 谁调用谁出）

```bash
# 1. 构造 prompt（已抹年龄）
~/dev/bio-age/bin/bio-age blind /path/to/exam.txt --output ./out --runner claude

# 2. 当前 session（Claude / Codex / OpenClaw）读 ./out/prompt.txt
#    → 自己产出 7 器官 JSON + 反猜年龄 → 写到 ./out/raw.txt

# 3. 解析 + 渲染 PDF + JPG 卡片
~/dev/bio-age/bin/bio-age blind /path/to/exam.txt --output ./out --runner skip-llm
```

### B. 调外部模型（reproducibility）

```bash
~/dev/bio-age/bin/bio-age blind exam.txt --runner codex                       # GPT-5.5pro
~/dev/bio-age/bin/bio-age blind exam.txt --runner ollama:gemma4:31b-it-q4_K_M # Local
```

## 输出结构

```
out/
├── prompt.txt        # 实际喂给模型的 prompt（已 scrub，audit 用）
├── raw.txt           # 模型 raw stdout
├── result.json       # 标准化 JSON: 7 器官 + 推理 + 反猜年龄
├── report.html       # 网页报告
├── report.pdf        # A4 PDF (headless Chrome 渲染, parchment 底色保留)
├── page-1.jpg ...    # 每页 PDF → 200dpi JPG (社交分享 friendly)
```

JPG 是 PDF 各页 200dpi 转换，竖屏 portrait，适合微信朋友圈 / X / 小红书。

## 隐藏年龄（blind）实现

`scripts/scrub_age.py`（17 case 全 pass + bug-class-fixed for inline parens / single-line JSON）：

抹掉：
- `Age: X years old` / `Date of birth` 整行
- `(38y 10m at YYYY-MM-DD blood draw)` 类内嵌
- `started age 18` / `smoker since age 18` → `long-term smoker`
- `diseases suffered for X-Y years ago` → `longstanding history`
- `low for age` / `[N]yo male` / `[N]-year-old` → 抹年龄部分
- `chronological age = X` → `chronological age (withheld)`

不动：化验数值、病史描述、收集日期（仅时点先后）、BMD `% YAM`（固定锚不是患者年龄）。

跑 self-test：
```bash
python3 ~/dev/bio-age/scripts/scrub_age.py --self-test  # 17/17 pass
```

## 数据完整度

**最低可用**（≥ 8 项 + 性别 + 生活方式 → ±5 岁）：
```
Gender + Lifestyle (吸烟 + 酒精 + 运动)
Lipid: LDL + HDL + TG
Liver: ALT/AST
Kidney: Cr + eGFR
Glucose: fasting + HbA1c
```

**推荐完整**（≥ 25 项 → ±2 岁）：加 ApoB / Lp(a) / CRP / insulin / ferritin / vitamin D / testosterone / BP / HRV / VO2max / BMI / 家族史。

**专科加分**：心电图 / FibroScan / 肺功能 / Cystatin C / DEXA BMD / OGTT。

LLM 容忍度高 — 论文用 NHANES 每例 ~30 项依然 r=0.84。覆盖 6 个器官即可。

## 设计说明

默认设计是为 bio-age 原创的现代编辑级排版，单一固定主题。

要换主题（cyberpunk / 生物发光 / 任务控制台 / 全息 HUD），见 `designs/` 目录的 4 份替代 brief，每份返回一个新的 `templates/styles/default.css` 即可，不需要改其他文件。

## 注意

1. **Blind 是默认 = anchoring effect 已规避**。模型如果反猜年龄偏离用户真实年龄 ±5 岁，就要警惕器官年龄的可信度
2. **跨模型差 ±5 岁正常** — 同输入跑 3 个 LLM 取中位数更稳
3. **不能替代医疗建议** — footer 永远带 disclaimer

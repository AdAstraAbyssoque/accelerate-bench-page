# 中文页界面文案审阅

构建读取下表的键和值。花括号字段在渲染时从冻结数据填入。八个领域采用统一文案「包含哪些科学计算应用？」中的名称，英文键对应 `results.json` 的 `tasks[].area`。正文、标题和问答使用 `messaging.md`。

| 键 | 显示文案 | 出处 |
|---|---|---|
| leaderboard | 排行榜 | messaging.md 中文 FAQ「评测了哪些智能体？谁得分最高？」 |
| tasks | 任务列表 | results.json 的 tasks；T12 任务卡第 1 项 |
| paper | 论文 | messaging.md 中文 FAQ；官网 paper.html |
| headers | #、模型、运行框架、Score@1、GM、A₁.₂₅、A₂ | T12 任务卡指定表头；论文 §4 表 1，第 6 页；results.json 的 models[].name、harness、score、gm、a125、a2 |
| caption | 论文表 {table} · 基准 v{version} · {agents} 个智能体 × {tasks} 个任务，共 {outcomes} 个结果。每个智能体在每个任务上取首次运行，所有结果均在同一台机器上计分。Score@1 和 Aτ 用百分比表示，GM 用倍数表示。每个智能体由模型和运行框架组成，均请求高推理强度。结果错误或未提速，节省运行时间的奖励均为零。{omitted} 的 v{version} 运行尚未完成，未列入表中。 | 首页 #leaderboard 的 caption；论文 §3–4，第 5–6 页；results.json 的 sources.leaderboard、selection.benchmark_version、models、tasks、metric_note、selection.not_listed |
| stopped | 模型提供方的安全系统中止了 {model} 在 {stopped} 上的运行，这些运行均按失败计，奖励为零。该智能体在其余 {remaining} 个任务上的得分为 {score}%。 | 首页 #leaderboard 的 † 脚注；论文 §4 表 1，第 6 页；results.json 的 models[].stopped_tasks、tasks、selection.score_on_other_tasks |
| Molecular simulation & electronic structure | 分子模拟与电子结构 | messaging.md 中文 FAQ；results.json 的 areas |
| Fluids, atmosphere & ocean | 流体、大气与海洋 | messaging.md 中文 FAQ；results.json 的 areas |
| Transport, plasma & astronomy | 输运、等离子体与天文 | messaging.md 中文 FAQ；results.json 的 areas |
| Bioinformatics & phylogenetics | 生物信息与系统发育 | messaging.md 中文 FAQ；results.json 的 areas |
| Numerics, tensors & graphs | 数值计算、张量与图 | messaging.md 中文 FAQ；results.json 的 areas |
| Quantum circuits | 量子线路 | messaging.md 中文 FAQ；results.json 的 areas |
| Machine learning | 机器学习 | messaging.md 中文 FAQ；results.json 的 areas |
| Scientific I/O | 科学 I/O | messaging.md 中文 FAQ；results.json 的 areas |

页眉切换使用任务卡指定的「中文」和「English」。资源名 Harbor Hub、Hugging Face、GitHub 来自统一文案。llms.txt 的导航标题采用任务卡第 3 项指定的栏目名，中文入口沿用统一文案的「中文」，任务链接名来自 results.json 的 tasks[].name。

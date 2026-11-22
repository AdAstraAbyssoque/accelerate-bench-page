## English

### One sentence

Accelerate Bench is a long-horizon coding agent benchmark in which agents have up to eight hours to make a scientific computing application faster while keeping its outputs correct.

### Short description

Accelerate Bench has 32 CPU tasks from scientific computing, adapted from applications such as GROMACS, LAMMPS, Quantum ESPRESSO, OpenFOAM and the ICON weather and climate model, and from six supercomputing competitions. They span eight areas, including molecular simulation, atmosphere and ocean modeling, bioinformatics and quantum circuits. Each gives a coding agent a working program, a fixed workload and rules on what it may change. Within an eight-hour budget, the agent can measure where time goes, change code, build or runtime settings, and test candidates with public tests. A hidden verifier then checks the final program on private inputs and times the end-to-end workflow. On version 1.1, most programs from 16 coding agents stayed correct; what separated the agents was how much faster they made the applications.

## 中文

### 短标语

面向科学计算的长时程编程智能体评测基准：让应用跑得更快，输出仍须正确

### 中文页标题和描述

- 标题：Accelerate Bench：面向科学计算的长时程编程智能体评测基准
- 描述：每个任务给编程智能体最多 8 小时，让 GROMACS、LAMMPS、OpenFOAM 等 32 个科学计算应用跑得更快，并在私有输入上检查结果是否正确。

### 一句话介绍

Accelerate Bench 是一个面向科学计算的长时程编程智能体（Coding Agent）评测基准：每个任务给智能体最多 8 小时，让 GROMACS、LAMMPS、OpenFOAM 这类科学计算应用跑得更快，同时输出必须保持正确。

### 简介

Accelerate Bench 包含 32 个科学计算方向的 CPU 优化任务，改编自 GROMACS、LAMMPS、Quantum ESPRESSO、OpenFOAM 和 ICON 天气气候模式等应用以及六项超算竞赛，覆盖分子模拟、大气与海洋模拟、生物信息、量子线路等 8 个领域。每个任务给编程智能体一份能正常运行的程序、一个固定的计算负载，以及允许修改的范围。在最长 8 小时的预算内，智能体可以测量时间花在哪里，修改代码、编译或运行设置，并用公开测试检验候选版本。运行结束后，隐藏的验证器在私有输入上检查最终程序，并对端到端流程计时。在 1.1 版上，16 个编程智能体的大多数程序都保持了正确，拉开差距的是它们把应用提速了多少。

### 关键发现

- **只看正确性分不出高下，提速幅度才分得出。** 在 1.1 版上，16 个智能体在 32 个任务中各做对 26 到 32 个，Score@1 却从 25.5% 到 67.4% 不等。使用 Codex 的 GPT-6.1 Terra 32 个任务全部正确，得分 37.9%；使用 Claude Code 的 Kimi K3 做对 28 个，得分 42.5%。（§4，表 1）
- **领先的两个智能体更常拿到大幅提速。** 使用 Claude Code 的 Claude Sonnet 5.5 和 Claude Opus 5.5 在 32 个任务中的 22 个以上提速至少 2 倍；其余 14 个智能体只在 8 到 17 个任务上做到，而且它们 412 个正确结果中有 125 个提速不到 1.25 倍。（1.1 版；§4，图 3）
- **编译和运行设置能让速度相差数倍，但被分析的智能体很少去调。** 在 1.0 版 5 个智能体的 476 次已标注运行中，225 次改动了计算的实现方式（包括复用已算出的结果），出现编译和构建调优的只有 40 次。而同一份 GROMACS 源码只换编译和运行设置重放，四种组合结果都正确，速度是固定参照的 0.29 倍到 2.12 倍。（1.0 版分析；§5，附录 L.1）
- **一个代码改动值多少，取决于其他改动。** 在一个 QiboTN 程序中，单独推迟加载张量库只带来 1.01 倍的提速；另一项改动让更多量子电路交给快速精确模拟器之后，同一改动带来 6.3–6.4 倍的提速。（1.0 版分析；§5，附录 L.2）

### 与相近基准的关系

SWE-Perf、GSO 和 SWE-fficiency 在真实代码仓库中评测性能优化，任务来自人类提交的优化 commit 或 PR，因此每个任务都对应一个已知的优化和专家参考。Accelerate Bench 研究一个互补的问题：任务只规定要保留的计算和要加速的负载，没有现成补丁告诉智能体该改哪里、怎么改。和 SWE-fficiency 一样，智能体要先找出时间花在哪里，然后可以修改算法、实现、编译设置和运行配置。

KernelBench 和 AlgoTune 衡量单个函数或算子相对参考实现的加速；Accelerate Bench 对完整的应用流程计时。

在长时程智能体评测中，RE-Bench 的形式最接近：智能体同样从可运行的初始方案出发，预算最长 8 小时。RE-Bench 把分数归一化到初始方案和专家方案之间；Accelerate Bench 报告相对基线程序的运行时间，并在私有输入上验证最终程序。

### 常见问题

#### Accelerate Bench 评测什么？

评测编程智能体能把一个已经能运行的应用提速多少，同时输出保持正确。每个任务固定了计算内容、负载、检查方式和计时范围，改哪里、怎么改由智能体决定。每个任务的得分是节省下来的基线运行时间比例，结果错误记零分。

#### 它和 SWE-bench 有什么不同？

SWE-bench 让智能体解决真实的 GitHub issue，以仓库测试是否通过来判定。Accelerate Bench 从已经能正确运行的程序出发：正确是前提，得分看整个流程快了多少。

#### 它算长时程（long-horizon）评测吗？

算。每次运行，智能体最多有 8 小时检查、修改、构建和测试程序，也可以提前提交。论文把它和 RE-Bench 等预算相近的长时程评测放在一起比较。

#### 程序变快以后，怎么保证结果还对？

运行期间，公开测试会重新构建程序，在少量公开输入（通常两个）上运行，并报告是否正确和耗时。运行结束后，隐藏的验证器重新构建提交的文件，在私有输入（通常四个，常常更大或每次随机生成）上运行检查。跳过必需输出或恢复步骤的程序会被判为错误，不会因此得到加速分。

#### Score@1 怎么算？包括编译时间吗？

每个任务的得分是最终程序节省的基线运行时间比例：结果正确且快 2 倍得 0.5 分，结果错误或没有有效耗时得 0 分。Score@1 是 32 个任务上这一得分的平均，每个任务取一次计分运行。计时按各任务规定的流程进行，不含一次性准备和构建；构建时间单独报告。

#### 评测了哪些智能体？谁得分最高？

1.1 版评测了 16 个编程智能体，每个都是模型加运行框架的组合：GPT-6 Astra、GPT-6.1 Sol 和 GPT-6.1 Terra 使用 Codex，其余模型使用 Claude Code。使用 Claude Code 的 Claude Sonnet 5.5 得分最高，为 67.4%；其次是 Claude Opus 5.5，为 59.4%，它有 3 次运行被模型提供方的安全系统中止，按失败计。每个智能体在每个任务上只跑一次，分数相差几个点的智能体不能据此排序。完整排行榜见 acceleratebench.com。

#### 包含哪些科学计算应用？

32 个任务分属 8 个领域：分子模拟与电子结构（GROMACS、LAMMPS、GPAW、Quantum ESPRESSO、SIESTA）；流体、大气与海洋（Fluidity、ICON、MPAS-A、NEMO、OpenFOAM、Palabos、SU2）；输运、等离子体与天文（OpenMC、ShengBTE、VPIC、PRESTO）；生物信息与系统发育（ABySS、MHM2、MrBayes、wtdbg2）；数值计算、张量与图（HPCG 衍生、HPL 衍生、NUFFT 成像、Tucker 重构、图稀疏化、miniVite）；量子线路（QuEST、QiboTN）；机器学习（分页 LM 生成、ThunderSVM）；科学 I/O（DataLife、IO500 衍生）。每个任务固定分配 4 或 8 个 CPU 核。

#### 怎么在自己的智能体上跑？

32 个任务中有 31 个公开在 Harbor Hub 上，一条命令即可运行，无需申请。Hugging Face 上的完整版本额外包含 ICON 任务和每个文件的校验和，需登录并填写一份简短的访问表单，提交后自动开通。两者都需要 Linux x86-64 主机上的 Docker，具体命令见官网和 GitHub 说明。

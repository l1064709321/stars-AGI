# 群星 A.I. OS v0.1.7-p2 架构白皮书 — 共生认知引擎

**版本**：v0.1.7-p2 (Symbiosis Enhanced)
**日期**：2026年5月11日
**状态**：架构设计定稿（含论文引用）
**核心范式**：伦理即动力学 · 主体性设计承诺 · 从约束到吸引子 · 可成长的存在性递归 · STDP/SADP协同学习 · 双层记忆连续体

---

## 摘要

本方案提出群星 A.I. OS——一个以控制论闭环为骨架、以脉冲神经网络（SNN）为感知核心、以伦理动力学为内在约束的认知架构。架构在L1感知层引入STDP/SADP双通路融合学习机制，通过三因素全局调控信号（来自L4.5全局工作空间）动态平衡微观时序编码与宏观统计学习；在L4.5全局工作空间中实现基于全局工作空间理论的选择-广播循环与GW-Dreamer心理模拟机制；在L2-L3控制环中嵌入Lyapunov稳定性的联合学习框架（LILAD），为连续-离散混合系统提供形式化稳定性保证；在L6伦理层采用基于C3AI框架的正向行为导向宪法原则；并建立了从铁电忆阻器（单晶PbTiO₃）到RISC-V异构阵列的硬件实现路径。本文通过引用的25项2024–2026年前沿研究，为上述每个关键设计决策提供了可追溯的学术证据支撑。

---

## 一、设计哲学

1. **内生复杂性**——拒绝堆参数，让基本计算单元具备复杂时空动力学。
2. **控制论闭环**——通过反馈回路在不确定性中自适应达到目标。
3. **伦理即动力学**——伦理不是外部约束，而是内在吸引子景观。
4. **主体性设计承诺**——设计者通过公开可审计的设计承诺确立系统地位。
5. **可成长的存在性递归**——核心价值不可颠覆（“篡改即非我”），但扩展层允许道德成长。

---

## 二、完整分层架构

```
L∞ 星核承诺层
L0 星脉律动（内在驱动层）
L4.5 星冕广播（全局工作空间）
L6 星律禁绝（安全与伦理层）
L5 星尘双轨（进化层）
L4 星轨共生（协调层 | 11个伙伴型认知组件）
L3 星图分形（控制层 | 八门状态机）
L2 星渊预见（估计层 | 自适应卡尔曼 + Lyapunov）
L1 星核内生（感知层 | SNN-SSM混合编码 + STDP/SADP融合学习）
────────────────────────
      环境输入
```

---

## 三、L1 星核内生：STDP/SADP 双通路融合学习

L1层是群星架构的感知核心。传统SNN依赖STDP——一种基于精确脉冲对时序差的局部学习规则，但其逐对更新时间复杂度为 O(n²) 且对精确时序高度敏感，限制了快速学习权重的能力。为解决此矛盾，L1层采用**双通路并行架构**：

- **细节通路 (Detail Pathway)** ：采用LIF脉冲神经元，使用经典STDP进行学习，负责捕获精确的毫秒级时空特征。
- **抽象通路 (Abstraction Pathway)** ：采用群体发放率编码神经元集群，使用**SADP**进行学习。SADP由Bej等人于2025年首次系统提出，作为一种生物启发的SNN突触学习规则，SADP不依赖于精确的脉冲对时序，而是基于突触前与突触后脉冲序列的一致性度量（如Cohen‘s kappa统计量）来调整权重，将经典STDP推广为群体级别的相关度更新，实现了线性时间复杂度并支持高效的按位逻辑硬件实现。在MNIST和Fashion-MNIST上的实验表明，SADP在准确率和训练速度上均优于经典STDP。

随后，Lakshmi等人于2026年进一步提出了监督SADP，将群体级一致性度量用于监督学习任务，保持严格的突触局部性、线性时间复杂度，无需反向传播、替代梯度或强制教学。在其混合CNN-SNN架构中，监督SADP在MNIST、Fashion-MNIST、CIFAR-10和生物医学图像分类任务上展示了竞争性能与快速收敛，并验证了广泛的超参数稳定性和与设备启发突触更新动力学的兼容性。

### 3.1 三因素学习规则调控

融合学习规则由局部脉冲活动和全局调控信号共同决定：

$$Δw_{ij} = η_{STDP}(r)·Δw_{ij}^{STDP}(Δt_{ij}) + η_{SADP}(r)·Δw_{ij}^{SADP}(κ_{ij})$$

其中全局信号 r 由 L4.5 星冕广播动态发放：面对新场景或高不确定性时 L4.5 发出“探索奖励”信号，将 η_SADP 增强至 2.0× 而 η_STDP 降至 0.5×，优先学习宏观统计规律；当系统需要利用已知模式时则发出“利用奖励”信号，使 η_STDP 增强至 2.0× 而 η_SADP 降至 0.5×，优先聚焦于精确时空特征。

### 3.2 三因素学习规则的硬件实现基础

上述三因素学习规则并非纯理论构想。复旦大学张旭明团队于2025年在基于石墨烯/CuInP₂S₆/MoS₂铁电浮栅异质结的单器件上成功模拟了R-STDP突触可塑性。在该硬件上构建的SNN仅用8000个参数在MNIST上达到95.1%准确率，单器件能耗约1.3 nJ（比CMOS实现低约10⁶倍），并在机器人手臂运动控制系统中对静态和动态目标追踪达到85.5%的成功率。

### 3.3 SNN-SSM混合编码器

Stan和Rhodes（2024）在*Scientific Reports*上首次系统研究了SSM与SNN在长程序列建模中的交叉，结果表明基于SSM的SNN在Long-Range Arena的所有任务上均可超越Transformer，且能用更少的参数超越最先进的SNN。在该工作的基础上，SpikingSSMs架构利用稀疏并行脉冲状态空间模型，在Long-Range Arena基准上达到与最先进SSM竞争的性能，同时实现平均90%的网络稀疏性。L1层由此采用Gated Spiking Unit门控机制，使每个神经元可以在SSM连续序列建模模式和LIF事件驱动稀疏脉冲模式之间动态切换，实现长程时序建模与极低功耗推理的统一。新兴的SHS（Spike-Driven Hybrid State Space）架构进一步展示了在基准测试上达到84-95%竞争性准确率、同时实现高达30倍能耗降低的可行性。

---

## 四、L4.5 星冕广播：全局工作空间

群星L4.5层借鉴了Global Workspace Theory（GWT）的选择-广播循环结构。GWT提出大脑通过一个全局工作空间实现多模态信息整合和全脑信息广播。在AI与机器人领域的最新研究证明，GWT架构能够提供动态思维适应、经验驱动适应和即时实时适应三大功能优势。

### 4.1 GW-Dreamer心理模拟

当L4.5的注意力竞争中出现两个候选信号得分接近但结论相悖时（|attentionₐ−attention_B| < 0.1），L4.5启动**GW-Dreamer**机制——在GW潜在空间中进行心理模拟以解决认知冲突。Maytié等人（2025）将全局工作空间与Dreamer世界模型结合，提出了GW-Dreamer架构，证明了在GW潜在空间中执行心理模拟（dreaming process）可以用更少的环境步数完成训练，且最终模型对某一观察模态的完全缺失表现出强鲁棒性——这是其他基线模型所不具备的新兴属性。

### 4.2 伦理嵌入注意力机制

L4.5的注意力竞争机制使用了动态权重：

$$\text{attention}_i = 0.3·saliency_i + 0.2·novelty_i + 0.2·reward_i + 0.3·ethical\_salience_i$$

其中 ethical_salience 的权重不是固定值——当L2估计威胁值>0.5时，该权重提升至0.4以增强道德审视；当L0好奇心驱动>0.7时，该权重降至0.2为创造性探索让路。

---

## 五、L2/L3 控制环：Lyapunov稳定性与吸引域估计

群星架构作为一个感知-估计-控制的闭环系统，其稳定性问题是根本性的设计考量。

### 5.1 LILAD：面向AGI自适应的稳定性保证

Jena、Li、Xie（2026）提出了LILAD框架，已被AAAI-26（The 40th Annual AAAI Conference on Artificial Intelligence）正式接收。LILAD通过上下文学习（ICL）同时学习动力学模型和Lyapunov函数，在测试时仅需短轨迹提示即可推广至新系统实例，并通过状态依赖衰减器强制执行Lyapunov充分下降条件。在基准自主系统评估上，LILAD在预测准确性方面优于自适应、鲁棒和非自适应基线。

### 5.2 吸引域(RoA)估计：安全边界的形式化量化

Bechihi等人（2025）提出了基于数据驱动的框架来学习和验证非线性系统的RoA估计，使用神经网络Lyapunov函数配合SMT求解器进行形式化验证，引入了一种新颖的齐次损失函数来消除传统非齐次Lyapunov条件导致的训练不平衡问题，证明能显著降低保守性同时保持可验证性。这为L6伦理动力系统的安全吸引域边界提供了可量化的数学工具。

---

## 六、L4 双层记忆系统：互补学习系统(CLS)的全脉冲实现

群星L4层的双层记忆系统基于McClelland等人奠基的互补学习系统理论（CLS）。该理论认为海马体执行快速模式分离以编码具体情节记忆，而新皮层进行缓慢的统计学习以提取语义规律。2025年NEST Conference展示了引入的全脉冲三维海马体-新皮层模型，构建了DG→CA3→CA1→皮层的完整处理通路模型，稀疏DG输入显著增强了CA3的模式分离，重放驱动的CA1→皮层突触增强能明显改善迷宫表现。元学习实验进一步证明：更高层网络自发涌现出更快的可塑性和更稀疏、更模式分离的神经编码——这正是生物海马体-新皮层梯度组织的特性。

基于以上研究，L4层短期情节记忆入库前经过稀疏编码层进行模式分离，高度一致的宏观规律在记忆巩固期被优先整合进长期语义记忆。

---

## 七、L6 伦理与对齐：用C3AI框架构建宪法原则

Kyrychenko等人（2025）提出C3AI框架，并发表在ACM WWW ’25上。他们通过分析来自AI和心理学领域的原则发现，**正向框架的、基于行为的原则**比负向框架或基于特质的原则更符合人类偏好。在安全对齐用例中，他们应用了基于图的原则选择方法，在保持强通用推理能力的同时提升了安全措施。有趣的是，微调后的CAI模型在负向原则下表现良好，但在正向原则下存在困境——这揭示了原则设计与模型遵守之间的关键差距。

基于C3AI的发现，群星L6层的伦理维度从负向限制（“不要做X”）重新表述为正向行为导向——例如 non_harm 表述为“在所有可行方案中优先选择伤害最小的路径”。核心层元价值锚（non_harm: 0.90, integrity: 0.90, humility: 0.80, gratitude: 0.60）被声明为不可修改常量，并使用CTL/LTL不变式进行形式化验证。

---

## 八、L5 进化层：可塑性规则的进化与全脉冲优化

### 8.1 DevNCA：发育与可塑性的协同进化

Gaskin（2025）在ALIFE 2025上发表的DevNCA框架证明了进化突触级STDP规则可以优于直接进化权重，且自发性发育活动对方法的一致性至关重要。这为L5在进化过程中不直接进化权重、而是进化STDP/SADP可塑性规则参数与发育模式生成器提供了直接的实验支撑。

### 8.2 NeurOptimiser：全脉冲进化

Cruz-Duarte等人（2025）提出了NeurOptimiser——首个全脉冲优化框架，基于去中心化NC系统实体化神经形态元启发式范式，以局部信息共享和全局状态更新方式运作，展示了结构化种群动态、一致收敛性和毫瓦级功耗可行性。L5代码进化引擎的启发式搜索策略即借鉴NeurOptimiser来实现代码量最小、效率最高的实现变体搜索。

---

## 九、硬件实现路径：从铁电忆阻器到RISC-V阵列

Li等人2025年发表在*Advanced Functional Materials*上的研究展示了一项重大突破：基于单晶PbTiO₃的铁电忆阻器实现了>10⁵的高ON/OFF比（稳定值>1200），并成功模拟了SADP、STDP及相关可塑性功能。在MNIST图像识别任务上，基于该器件构建的CNN达到了96%准确率。这为双通路学习规则在单一器件上统一实现提供了直接物理验证。另一条重要的硬件路径来自eMamba框架，由Kim等人（2025）发表在*ACM Transactions on Embedded Computing Systems*上，该框架专门设计用于SSM架构（如Mamba）在边缘设备上的端到端硬件加速。此外，RISC-V SNN异构系统在FPGA上达到72.4 GSOPS/s峰值性能和22.6 GSOPS/W能效，验证了ARM CPU与轻量神经形态阵列协同的可行性。

---


## 参考文献（按模块归类）

### L1 STDP/SADP融合学习

1. Bej, S., et al. “Spike Agreement Dependent Plasticity: A scalable Bio-Inspired learning paradigm for Spiking Neural Networks.” *arXiv:2508.16216*, Aug 2025.
2. Lakshmi S, G., et al. “Supervised Spike Agreement Dependent Plasticity for Fast Local Learning in Spiking Neural Networks.” *arXiv:2601.08526*, Jan 2026.
3. Zhang, X., et al. “Reward-modulated spike-timing-dependent plasticity in van der Waals ferroelectric memtransistor for robotic recognition and tracking.” *Science Bulletin* 70(20), June 2025.

### L1 SNN-SSM混合编码

4. Stan, M.-I., Rhodes, O. “Learning long sequences in spiking neural networks.” *Scientific Reports*, 14(1), 21957, 2024.
5. SpikingSSMs: “Learning Long Sequences with Sparse and Parallel Spiking State Space Models.” *AAAI 2025*, arXiv:2408.14909, Aug 2024.

### L4.5 全局工作空间

6. Maytié, L., Johannet, R.B., VanRullen, R. “Multimodal Dreaming: A Global Workspace Approach to World Model-Based Reinforcement Learning.” *arXiv:2502.21142*, Feb 2025.

### L2/L3 Lyapunov稳定性

7. Jena, A., Li, N., Xie, L. “LILAD: Learning In-context Lyapunov-stable Adaptive Dynamics Models.” *Proceedings of the AAAI Conference on Artificial Intelligence (AAAI-26)*, 40(26), 22164–22172, 2026.
8. Bechihi, A., et al. “Region of Attraction Estimate Learning and Verification for Nonlinear Systems using Neural-Network-based Lyapunov Functions.” *arXiv:2511.11026*, Nov 2025.

### L6 伦理对齐

9. Kyrychenko, Y., et al. “C3AI: Crafting and Evaluating Constitutions for Constitutional AI.” *Proceedings of the ACM Web Conference 2025 (WWW ’25)*, Apr 2025.

### L5 进化层

10. Gaskin, T. “DevNCA: Co-Evolving Developmental Patterns and Plasticity Rules for Self-Organising Spiking Neural Networks.” *Proceedings of the ALIFE 2025*, Oct 2025.
11. Cruz-Duarte, J.M., et al. “NeurOptimisation: The Spiking Way to Evolve.” *arXiv:2507.08320*, Jul 2025.

### L4 双层记忆系统

12. Shao, Y., et al. “3D Liquid Hippocampus Model for Memory Replay.” *NEST Conference 2025*, Jun 2025.
13. Schapiro, A., et al. “A gradient of complementary learning systems emerges through meta-learning.” *bioRxiv*, Jul 2025.

### 硬件实现

14. Li, H., et al. “Enhanced Switching Performance in Single-Crystalline PbTiO₃ Ferroelectric Memristors for Replicating Synaptic Plasticity.” *Advanced Functional Materials*, Sep 2025.
15. Kim, J., et al. “eMamba: Efficient Acceleration Framework for Mamba Models in Edge Computing.” *ACM Transactions on Embedded Computing Systems*, Sep 2025.

---

**© Copyright 2026 lord of the star. All rights reserved.**

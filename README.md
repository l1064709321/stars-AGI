```markdown
# STARS-Gateway: Stateless Traffic Absorption & Resource-Sink

[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange)](https://www.rust-lang.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)
[![Stage](https://img.shields.io/badge/Stage-Proof%20of%20Concept-yellow)]()

Current Status: Proof-of-Concept
This repository currently implements a single-node Slowloris-style tarpit engine (STARS-Sink). The decentralized constellation mesh (STARS-Pulse) and eBPF XDP filter (STARS-Filter) are under active design. See RFC.md for the architectural vision.

## What is STARS-Gateway?

STARS-Gateway is an experimental edge traffic governance framework that replaces traditional WAF "block-on-sight" behavior with asymmetric resource consumption traps. Instead of returning 403 or resetting connections, it accepts suspicious traffic and forces the client to waste resources waiting for a response that never completes.

### Core Modules (Current & Planned)

| Module | Status | Description |
| :--- | :--- | :--- |
| STARS-Sink | Implemented | Async tarpit engine. Responds to clients with exponentially delayed 1-byte payloads. Consumes attacker's file descriptors and event loop capacity while using less than 5 percent local CPU. |
| STARS-Filter | Design | eBPF/XDP in-kernel classifier. Routes suspicious flows to the sink without touching user-space network stack. |
| STARS-Pulse | Design | SWIM-based gossip protocol for decentralized signature propagation across edge nodes. |

## Quick Start (Single Node Tarpit)

### Prerequisites
- Linux kernel 5.4 or newer
- Rust 1.75 or newer (install via rustup)

### Build and Run
”“bash
git clone https://github.com/L1064709321/stars-gateway.git
cd stars-gateway

货物建造—放行

sudo。/target/release/stars-gateway——mode sink——bind 0.0.0.0:9999
```

###使用slowhttptest测试
”“bash
slowttptest -c 500 -H -g -o报告-i 10 -r 200 -t GET -u http://127.0.0.1:9999
```

观察到:
—攻击客户端挂起，最终超时。
- stars-gateway进程的本地CPU使用率仍然很低（低于5%）。
—接收端口（ss -ntp | grep 9999）的连接保持ESTABLISHED状态。

项目结构

```
stars-gateway/
├──ebpf/ # XDP滤镜（设计阶段）
│   ├── include/
我愿……
││├──filter_xdp.c
│Makefile
├── src/
│├──sink/ # Tarpit引擎实现
我的意思是：
│   │   └── tarpit.rs
│├──├─rammstein（设计阶段）
mod.rs
│   └── main.rs
├──docs/ # RFC和架构注释
├── Cargo.toml
└── README.md
```

# #命名

STARS代表无状态流量吸收和资源吸收。该名称还反映了预期的星座拓扑，其中每个边缘节点充当一个独立的“星”。是的，我是星爵。

# #路线图

- [x]单节点tarpit引擎（STARS-Sink）
- [] eBPF XDP流量分类器（STARS-Filter）
- [] SWIM八卦会员（STARS-Pulse）
-[]基于crdt的签名传播
- [] Kubernetes DaemonSet部署清单

# #贡献

该项目处于早期概念验证阶段。Bug报告，想法和讨论欢迎通过问题。请注意，大型特性发布可能会推迟到核心架构稳定之后。

# #许可证

Apache 2.0。看到许可证。
```

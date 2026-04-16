# STARS-Gateway v0.1.0

[![Rust](https://img.shields.io/badge/Rust-1.75%2B-orange)](https://www.rust-lang.org)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)
[![Stage](https://img.shields.io/badge/Stage-Proof%20of%20Concept-yellow)]()

**Current Status: Proof-of-Concept**  
This repository implements a single-node Slowloris-style tarpit engine (STARS-Sink). The decentralized constellation mesh (STARS-Pulse) and eBPF XDP filter (STARS-Filter) are under active design. See [RFC.md](docs/RFC.md) for the architectural vision.

## What is STARS-Gateway?

STARS-Gateway is an experimental edge traffic governance framework that replaces traditional WAF "block-on-sight" behavior with **asymmetric resource consumption traps**. Instead of returning 403 or resetting connections, it accepts suspicious traffic and forces the client to waste resources waiting for a response that never completes.

### Core Modules (Current & Planned)

| Module | Status | Description |
| :--- | :--- | :--- |
| **STARS-Sink** | Implemented | Async tarpit engine. Responds to clients with exponentially delayed 1-byte payloads. Consumes attacker's file descriptors and event loop capacity while using less than 5% local CPU. |
| **STARS-Filter** | Design | eBPF/XDP in-kernel classifier. Routes suspicious flows to the sink without touching user-space network stack. |
| **STARS-Pulse** | Design | SWIM-based gossip protocol for decentralized signature propagation across edge nodes. |

## 环境要求与安装

### 前提条件
- Linux 内核 5.4 或更高版本 (Android AidLux / Termux 均可)
- Rust 1.75 或更高版本 (通过 rustup 安装)

### 安装 Rust 环境

如果尚未安装 Rust，请在终端执行以下命令：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

安装过程中按回车键选择默认选项。完成后立即执行以下命令使环境变量生效：

```bash
source "$HOME/.cargo/env"
```

# 验证安装：

```bash
rustc --version
cargo --version
```

# 快速开始

1. 克隆仓库并进入目录

```bash
git clone https://github.com/L1064709321/stars-gateway.git
cd stars-gateway
git checkout v0.1.0  # 确保使用 v0.1.0 版本标签
```

2. 编译

```bash
cargo build --release
```

3. 运行

```bash
sudo ./target/release/stars-gateway
```

# 启动成功后会显示：

```
[星主] 陷阱引擎已启动，监听端口 9999
```

4. 测试（使用 slowhttptest 模拟攻击）

在另一终端安装 slowhttptest：

```bash
sudo apt-get update
sudo apt-get install -y slowhttptest
```

# 发起攻击：

```bash
slowhttptest -c 500 -H -g -o report -i 10 -r 200 -t GET -u http://127.0.0.1:9999/
```

# 观察要点：

*   攻击方客户端挂起，最终超时。
*   防御方 stars-gateway 进程 CPU 占用持续低于 5%。
*   陷阱端口上连接保持 ESTABLISHED 状态 (ss -ntp | grep 9999)。

# 项目结构
```

 stars-gateway/
 ── Cargo.toml
├── src/
│   └── main.rs
├── docs/                   # RFC and architectural notes
└── README.md
```

# 版本说明

*   **v0.1.0**：极简原型，仅支持 HTTP 慢速陷阱，已验证不对称消耗可行性。
后续版本规划请见ROADMAP.md
# Naming

STARS stands for Stateless Traffic Absorption & Resource-Sink. The name also reflects the intended constellation topology where each edge node acts as an independent "star". Yes, I'm the Lord of the Star.

# Roadmap

*   Single-node tarpit engine (STARS-Sink)
*   eBPF XDP traffic classifier (STARS-Filter)
*   SWIM gossip membership (STARS-Pulse)
*   CRDT-based signature propagation
*   Kubernetes DaemonSet deployment manifests

# Contributing

This project is in early proof-of-concept stage. Bug reports, ideas, and discussions are welcome via Issues. Please note that large feature PRs may be deferred until the core architecture stabilizes.

License

# Apache 2.0. See LICENSE.

```

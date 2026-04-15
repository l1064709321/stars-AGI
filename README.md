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
```bash
git clone https://github.com/L1064709321/stars-gateway.git
cd stars-gateway

cargo build --release

sudo ./target/release/stars-gateway --mode sink --bind 0.0.0.0:9999
```
# Test with slowhttptest

```bash
slowhttptest -c 500 -H -g -o report -i 10 -r 200 -t GET -u http://127.0.0.1:9999
```
# Observe that:

· The attacking client hangs, eventually timing out.
· Local CPU usage of the stars-gateway process remains low (under 5 percent).
· Connections stay ESTABLISHED on the sink port (ss -ntp | grep 9999).

# Project Structure

```
stars-gateway/
├── ebpf/                   # XDP filter (design phase)
│   ├── include/
│   ├── progs/
│   │   └── filter_xdp.c
│   └── Makefile
├── src/
│   ├── sink/               # Tarpit engine implementation
│   │   ├── mod.rs
│   │   └── tarpit.rs
│   ├── pulse/              # Gossip sync (design phase)
│   │   └── mod.rs
│   └── main.rs
├── docs/                   # RFC and architectural notes
├── Cargo.toml
└── README.md
```

# Naming

STARS stands for Stateless Traffic Absorption & Resource-Sink. The name also reflects the intended constellation topology where each edge node acts as an independent "star". Yes, I'm the Lord of the Star.

# Roadmap

· Single-node tarpit engine (STARS-Sink)
· eBPF XDP traffic classifier (STARS-Filter)
· SWIM gossip membership (STARS-Pulse)
· CRDT-based signature propagation
· Kubernetes DaemonSet deployment manifests

# Contributing

This project is in early proof-of-concept stage. Bug reports, ideas, and discussions are welcome via Issues. Please note that large feature PRs may be deferred until the core architecture stabilizes.

# License

Apache 2.0. See LICENSE.

```

# NetTrace  
### Real‑Time Network Diagnostics & IP Tracing

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)

NetTrace is a fast, lightweight deep network tool designed for developers, analysts, and security‑minded users who need clear, real‑time visibility into how their connections behave. Built entirely on Python’s standard library, it performs IP tracing, latency checks, DNS lookups, and route inspection without any external dependencies. With a clean terminal‑inspired interface and a modular architecture, NetTrace delivers accurate, privacy‑respecting network insights on Windows, macOS, and Linux — all in a portable, deploy‑ready package.

-------------------------------------------------------------------
🚀 NetTrace — Real‑Time Network Diagnostics & IP Tracing
NetTrace is a lightweight, zero‑dependency network diagnostics tool built in Python. It provides real‑time IP tracing, hop inspection, DNS tools, latency testing, and a customizable terminal‑style UI — all running on the Python standard library.

🔌 Data Flow Summary
User Input  
The CLI/UI receives an IP, domain, or command flag.

Command Routing  
The UI dispatches the request to the appropriate network engine module.

Network Execution  
The engine performs:

traceroute

ping

DNS lookup

reverse lookup

Parsing & Normalization  
OS‑native output is parsed into structured Python objects.

UI Rendering  
Results are displayed using the active theme (colors, borders, status text).

🧱 Design Principles
Zero external dependencies — Python standard library only

Cross‑platform compatibility — Windows, macOS, Linux

Modular architecture — UI, engine, and utilities are cleanly separated

Theme‑driven UI — JSON‑based color and layout system

Deploy‑ready — No frameworks, no build steps, no bloat
--------------------------------------------------------------------
🚀 Features
Real‑time IP tracing

Route & hop inspection

DNS lookup & reverse lookup

Latency measurement

Terminal‑style theme system

Zero external dependencies

Works on Windows, macOS, and Linux
└──────────────────────────────────────────────────────────────┘

# IP Trace
python NetTraceBeta.py --trace 8.8.8.8

# DNS Lookup
python NetTraceBeta.py --dns example.com

# Reverse Lookup
python NetTraceBeta.py --reverse 1.1.1.1

# Latency Test
python NetTraceBeta.py --ping 8.8.4.4

# Launch UI Mode
python NetTraceBeta.py --ui

🧩 Installation
1. Clone the repository
git clone https://github.com/20cdelmonaco/NetTraceBeta.git
cd NetTraceBeta

2. Run NetTrace
python NetTraceBeta.py

┌───────────────────────────────────────────────────-───────────┐
│                          NetTrace                             │
│                 Real‑Time Network Diagnostics                 │
└──────────────────────────────────────────────────-────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────-──────────────┐
│                        UI Layer (CLI/UI)                      │
│  • Terminal‑style interface                                   │
│  • Theme engine (JSON‑based)                                  │
│  • Input handling (IP, domain, commands)                      │
│  • Output formatting (colors, status, logs)                   │
└─────────────────────────────────────────────────-─────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│                    Core Network Engine                       │
│  • IP tracing (hop‑by‑hop)                                   │
│  • Latency measurement (ping)                                │
│  • DNS lookup / reverse lookup                               │
│  • Route inspection                                          │
│  • Error handling & validation                               │
└──────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│                        Utility Modules                       │
│  • OS‑safe subprocess wrappers                               │
│  • Cross‑platform compatibility                              │
│  • Timing utilities                                          │
│  • Output parsing helpers                                    │
└──────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│                      System Interfaces                       │
│  • ICMP / ping commands                                      │
│  • traceroute / tracert                                      │
│  • DNS resolver (socket + stdlib)                            │
│  • OS‑native network stack                                   │
└───────────────────────────────────────────────-──────────────┘






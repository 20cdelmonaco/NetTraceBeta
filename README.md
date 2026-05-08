# NetTrace  
### Real‑Time Network Diagnostics & IP Tracing

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen)

NetTrace is a fast, lightweight deep network tool designed for developers, analysts, and security‑minded users who need clear, real‑time visibility into how their connections behave. Built entirely on Python’s standard library, it performs IP tracing, latency checks, DNS lookups, and route inspection without any external dependencies. With a clean terminal‑inspired interface and a modular architecture, NetTrace delivers accurate, privacy‑respecting network insights on Windows, macOS, and Linux — all in a portable, deploy‑ready package.

---
## 🔌 Data Flow Summary

1. **User Input**  
   The UI receives an IP, domain, or command flag.

2. **Command Routing**  
   The UI dispatches the request to the appropriate network engine function.

3. **Network Execution**  
   The engine performs:
   - traceroute  
   - ping  
   - DNS lookup  
   - reverse lookup  

4. **Parsing & Normalization**  
   Raw OS output is parsed into structured Python data.

5. **UI Rendering**  
   Results are displayed using the active theme (colors, borders, status text).

---

## 🧱 Design Principles

- **Zero external dependencies**  
  Everything runs on Python’s standard library.

- **Cross‑platform compatibility**  
  Uses OS‑safe wrappers for ping/traceroute.

- **Modular architecture**  
  Each feature is isolated and easy to extend.

- **Theme‑driven UI**  
  Colors and layout are fully customizable.

- **Deploy‑ready**  
  No frameworks, no heavy packages, no build steps.

---



---

## 🚀 Features
- Real‑time IP tracing  
- Route & hop inspection  
- DNS lookup & reverse lookup  
- Latency measurement  
- Terminal‑style theme system  
- Zero external dependencies  
- Works on Windows, macOS, and Linux  

---

**Usage Examples (terminal)**

IP Trace - python NetTraceBeta.py --trace 8.8.8.8
DNS Lookup - python NetTraceBeta.py --dns example.com
Reverse lookup - python NetTraceBeta.py --reverse 1.1.1.1
Latency Test  - python NetTraceBeta.py --ping 8.8.4.4
Launch UI mode - python NetTraceBeta.py --ui

---

## 🧩 Installation

### **1. Clone the repository**\
```bash
git clone https://github.com/20cdelmonaco/NetTraceBeta.git
cd NetTraceBeta

# Run NetTrace
  python NetTraceBeta.py

┌──────────────────────────────────────────────────────────────┐
│                          NetTrace                             │
│                 Real‑Time Network Diagnostics                 │
└──────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│                        UI Layer (CLI/UI)                      │
│  • Terminal‑style interface                                   │
│  • Theme engine (JSON‑based)                                  │
│  • Input handling (IP, domain, commands)                      │
│  • Output formatting (colors, status, logs)                   │
└──────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│                    Core Network Engine                        │
│  • IP tracing (hop‑by‑hop)                                    │
│  • Latency measurement (ping)                                 │
│  • DNS lookup / reverse lookup                                │
│  • Route inspection                                            │
│  • Error handling & validation                                │
└──────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│                        Utility Modules                        │
│  • OS‑safe subprocess wrappers                                │
│  • Cross‑platform compatibility (Windows/macOS/Linux)         │
│  • Timing utilities                                           │
│  • Output parsing helpers                                     │
└──────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│                      System Interfaces                        │
│  • ICMP / ping commands                                       │
│  • traceroute / tracert                                       │
│  • DNS resolver (socket + Python stdlib)                      │
│  • Network stack (OS‑native)                                  │
└──────────────────────────────────────────────────────────────┘





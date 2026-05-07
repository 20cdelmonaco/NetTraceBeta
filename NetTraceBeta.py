import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import platform
import socket
import threading
import ssl
import http.client
import json
import sys
import datetime
import re

# =============================
# Utility: Threading
# =============================

def run_in_thread(func, *args, **kwargs):
    threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True).start()

# =============================
# Import / Tool Availability
# =============================

REQUIRED_TOOLS = {
    "requests": {
        "module": "requests",
        "pip": "requests",
        "installed": False,
    },
    "whois": {
        "module": "whois",
        "pip": "python-whois",
        "installed": False,
    },
    "speedtest": {
        "module": "speedtest",
        "pip": "speedtest-cli",
        "installed": False,
    },
}

def check_module_available(mod_name):
    try:
        __import__(mod_name)
        return True
    except ImportError:
        return False

def check_command_available(cmd):
    try:
        subprocess.check_output([cmd, "--version"], stderr=subprocess.STDOUT)
        return True
    except Exception:
        return False

def init_tool_availability():
    for key, info in REQUIRED_TOOLS.items():
        info["installed"] = check_module_available(info["module"])

init_tool_availability()

# =============================
# Helper: ttk detection
# =============================

def is_ttk_widget(widget):
    try:
        cls = widget.winfo_class()
        return cls.startswith("T")
    except Exception:
        return False

# =============================
# Theme Manager
# =============================

class ThemeManager:
    def __init__(self, root, widgets_registry):
        self.root = root
        self.widgets_registry = widgets_registry
        self.current_theme = "Terminal Classic"
        self.themes = {
            "Terminal Classic": {
                "bg": "#000000",
                "fg": "#ffffff",
                "accent": "#423F3F",
                "button_bg": "#312F2F",
                "button_fg": "#ffb000",
                "entry_bg": "#111111",
                "entry_fg": "#FFFFFF",
                "output_bg": "#000000",
                "output_fg": "#17cc45",
                "status_fg": "#01e901",
                "border": "#5e509b",
            },
            "Matrix Green": {
                "bg": "#000000",
                "fg": "#00ff41",
                "accent": "#00ff41",
                "button_bg": "#001100",
                "button_fg": "#00ff41",
                "entry_bg": "#001100",
                "entry_fg": "#00ff41",
                "output_bg": "#000000",
                "output_fg": "#00ff41",
                "status_fg": "#00ff41",
                "border": "#00ff41",
            },
            "Midnight Blue": {
                "bg": "#020617",
                "fg": "#e0f2fe",
                "accent": "#38bdf8",
                "button_bg": "#0f172a",
                "button_fg": "#e0f2fe",
                "entry_bg": "#020617",
                "entry_fg": "#e0f2fe",
                "output_bg": "#020617",
                "output_fg": "#e0f2fe",
                "status_fg": "#38bdf8",
                "border": "#38bdf8",
            },
            "Light Mode": {
                "bg": "#f9fafb",
                "fg": "#111827",
                "accent": "#2563eb",
                "button_bg": "#e5e7eb",
                "button_fg": "#111827",
                "entry_bg": "#ffffff",
                "entry_fg": "#111827",
                "output_bg": "#ffffff",
                "output_fg": "#111827",
                "status_fg": "#2563eb",
                "border": "#2563eb",
            },
            "Cyberpunk": {
                "bg": "#050014",
                "fg": "#f9a8d4",
                "accent": "#22d3ee",
                "button_bg": "#111827",
                "button_fg": "#f9a8d4",
                "entry_bg": "#020617",
                "entry_fg": "#e0f2fe",
                "output_bg": "#020617",
                "output_fg": "#e0f2fe",
                "status_fg": "#22d3ee",
                "border": "#f97316",
            },
        }

    def apply_theme(self, name=None):
        if name:
            self.current_theme = name
        theme = self.themes[self.current_theme]

        self.root.configure(bg=theme["bg"])

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "TNotebook",
            background=theme["bg"],
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            background=theme["button_bg"],
            foreground=theme["fg"],
            padding=(8, 4),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", theme["accent"])],
            foreground=[("selected", theme["bg"])],
        )

        style.configure(
            "TCombobox",
            fieldbackground=theme["entry_bg"],
            background=theme["entry_bg"],
            foreground=theme["entry_fg"],
            arrowcolor=theme["entry_fg"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", theme["entry_bg"])],
            foreground=[("readonly", theme["entry_fg"])],
        )

        for wtype, widgets in self.widgets_registry.items():
            for w in widgets:
                if wtype == "notebook":
                    continue
                if is_ttk_widget(w):
                    continue

                if wtype == "frame":
                    w.configure(bg=theme["bg"])
                elif wtype == "label":
                    w.configure(bg=theme["bg"], fg=theme["fg"])
                elif wtype == "status":
                    w.configure(bg=theme["bg"], fg=theme["status_fg"])
                elif wtype == "button":
                    w.configure(
                        bg=theme["button_bg"],
                        fg=theme["button_fg"],
                        activebackground=theme["accent"],
                        activeforeground=theme["fg"],
                        relief=tk.FLAT,
                        bd=1,
                    )
                elif wtype == "entry":
                    w.configure(
                        bg=theme["entry_bg"],
                        fg=theme["entry_fg"],
                        insertbackground=theme["entry_fg"],
                        relief=tk.FLAT,
                    )
                elif wtype == "output":
                    w.configure(
                        bg=theme["output_bg"],
                        fg=theme["output_fg"],
                        insertbackground=theme["output_fg"],
                        relief=tk.FLAT,
                    )

# =============================
# Animation Manager
# =============================

class AnimationManager:
    def __init__(self, root, status_label, theme_manager):
        self.root = root
        self.status_label = status_label
        self.theme_manager = theme_manager
        self.status_pulse = False

    def start_status_pulse(self):
        self.status_pulse = True
        self._pulse_status()

    def stop_status_pulse(self):
        self.status_pulse = False

    def _pulse_status(self):
        if not self.status_pulse:
            return
        theme = self.theme_manager.themes[self.theme_manager.current_theme]
        base_color = theme["status_fg"]

        def brighten(color):
            try:
                c = color.lstrip("#")
                r = int(c[0:2], 16)
                g = int(c[2:4], 16)
                b = int(c[4:6], 16)
                r = min(255, int(r + (255 - r) * 0.4))
                g = min(255, int(g + (255 - g) * 0.4))
                b = min(255, int(b + (255 - b) * 0.4))
                return f"#{r:02x}{g:02x}{b:02x}"
            except Exception:
                return color

        bright = brighten(base_color)
        current = self.status_label.cget("fg")
        self.status_label.configure(fg=bright if current == base_color else base_color)
        self.root.after(400, self._pulse_status)

    def fade_in_output(self, text_widget, content, delay=1):
        text_widget.configure(state=tk.NORMAL)
        text_widget.delete("1.0", tk.END)

        def writer(i=0):
            if i >= len(content):
                return
            text_widget.insert(tk.END, content[i])
            text_widget.see(tk.END)
            text_widget.update_idletasks()
            text_widget.after(delay, writer, i + 1)

        writer()

# =============================
# Scanline Overlay
# =============================

class ScanlineOverlay:
    def __init__(self, parent, theme_manager):
        self.parent = parent
        self.theme_manager = theme_manager
        self.canvas = tk.Canvas(parent, highlightthickness=0, bd=0)
        self.mode = "Off"
        self.running = False
        self.offset = 0

    def resize(self, event=None):
        if self.mode == "Off":
            return
        self.draw_scanlines()

    def set_mode(self, mode):
        self.mode = mode
        if mode == "Off":
            self.running = False
            self.canvas.place_forget()
            return
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.running = (mode == "Dynamic")
        self.draw_scanlines()
        if self.running:
            self.animate()

    def draw_scanlines(self):
        self.canvas.delete("all")
        if self.mode == "Off":
            return
        theme = self.theme_manager.themes[self.theme_manager.current_theme]
        bg = theme["bg"]
        self.canvas.configure(bg=bg)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 0 or h <= 0:
            return

        if self.mode == "Soft":
            spacing = 6
            color = "#111111"
        elif self.mode == "Medium":
            spacing = 4
            color = "#080808"
        elif self.mode == "Heavy":
            spacing = 3
            color = "#050505"
        elif self.mode == "Dynamic":
            spacing = 4
            color = "#080808"
        else:
            spacing = 6
            color = "#111111"

        y = self.offset
        while y < h:
            self.canvas.create_line(0, y, w, y, fill=color)
            y += spacing

        try:
            self.canvas.lower(self.parent)
        except Exception:
            pass

    def animate(self):
        if not self.running:
            return
        self.offset = (self.offset + 1) % 8
        self.draw_scanlines()
        self.parent.after(80, self.animate)

# =============================
# Network Operations & Analytics
# =============================

def run_subprocess(command):
    try:
        result = subprocess.check_output(
            command, stderr=subprocess.STDOUT, universal_newlines=True
        )
        return result
    except FileNotFoundError:
        return f"Command not found: {command[0]}\n"
    except subprocess.CalledProcessError as e:
        return f"Error:\n{e.output}\n"

# ---- Ping with analytics ----

def parse_ping_output(raw):
    lines = raw.splitlines()
    times = []
    ttl = None
    sent = received = 0

    for line in lines:
        lower = line.lower()
        if "time=" in lower or "time<" in lower:
            sent += 1
            m = re.search(r"time[=<]\s*([\d\.]+)\s*ms", lower)
            if m:
                try:
                    times.append(float(m.group(1)))
                    received += 1
                except ValueError:
                    pass
        if "ttl=" in lower:
            m2 = re.search(r"ttl[=\s]*([0-9]+)", lower)
            if m2:
                try:
                    ttl = int(m2.group(1))
                except ValueError:
                    pass

    stats = {}
    if times:
        stats["min"] = min(times)
        stats["max"] = max(times)
        stats["avg"] = sum(times) / len(times)
        if len(times) > 1:
            diffs = [abs(times[i] - times[i - 1]) for i in range(1, len(times))]
            stats["jitter"] = sum(diffs) / len(diffs)
        else:
            stats["jitter"] = 0.0
    else:
        stats["min"] = stats["max"] = stats["avg"] = stats["jitter"] = None

    stats["sent"] = sent
    stats["received"] = received
    stats["loss"] = (sent - received) / sent * 100 if sent > 0 else None
    stats["ttl"] = ttl

    if ttl is not None:
        if ttl <= 64:
            stats["os_guess"] = "Linux/Unix-like (TTL≈64)"
        elif ttl <= 128:
            stats["os_guess"] = "Windows (TTL≈128)"
        else:
            stats["os_guess"] = "Network device / custom"
    else:
        stats["os_guess"] = "Unknown"

    return stats

def format_ping_stats(stats):
    lines = []
    lines.append("")
    lines.append("=== Ping Analysis ===")
    if stats["sent"] is not None:
        lines.append(f"Packets: Sent={stats['sent']}, Received={stats['received']}, Lost={stats['sent'] - stats['received']} ({stats['loss']:.1f}% loss)" if stats["loss"] is not None else "Packets: <unavailable>")
    if stats["avg"] is not None:
        lines.append(f"Latency: min={stats['min']:.2f} ms, avg={stats['avg']:.2f} ms, max={stats['max']:.2f} ms")
        lines.append(f"Jitter: {stats['jitter']:.2f} ms")
    else:
        lines.append("Latency: <no replies>")
    if stats["ttl"] is not None:
        lines.append(f"Observed TTL: {stats['ttl']}  →  {stats['os_guess']}")
    else:
        lines.append("Observed TTL: <unknown>")
    return "\n".join(lines) + "\n"

def ping_host(target):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "4", target]
    raw = run_subprocess(command)
    stats = parse_ping_output(raw)
    return raw + format_ping_stats(stats)

# ---- Traceroute with enrichment ----

def traceroute_host(target):
    command = ["tracert", target] if platform.system().lower() == "windows" else ["traceroute", target]
    raw = run_subprocess(command)
    enriched = enrich_traceroute(raw)
    return enriched

def enrich_traceroute(raw):
    lines = raw.splitlines()
    out_lines = []
    hop_re = re.compile(r"^\s*(\d+)\s+(.+)$")
    for line in lines:
        stripped = line.strip()
        m = hop_re.match(stripped)
        if not m:
            out_lines.append(line)
            continue
        hop_num = m.group(1)
        rest = m.group(2)

        ip_match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})", rest)
        ip = ip_match.group(1) if ip_match else None

        extra = []
        if ip:
            try:
                host, aliases, addrs = socket.gethostbyaddr(ip)
                extra.append(f"rDNS={host}")
            except Exception:
                pass

            if REQUIRED_TOOLS["requests"]["installed"]:
                try:
                    import requests
                    r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=2)
                    if r.status_code == 200:
                        data = r.json()
                        city = data.get("city")
                        country = data.get("country")
                        org = data.get("org")
                        parts = []
                        if city or country:
                            parts.append("Loc=" + ", ".join([p for p in [city, country] if p]))
                        if org:
                            parts.append(f"Org={org}")
                        if parts:
                            extra.append(" | ".join(parts))
                except Exception:
                    pass

        if extra:
            out_lines.append(f"{line}    [{'; '.join(extra)}]")
        else:
            out_lines.append(line)

    out_lines.append("")
    out_lines.append("=== Traceroute Notes ===")
    out_lines.append("Per-hop rDNS and GeoIP (where available) are appended in brackets.")
    return "\n".join(out_lines) + "\n"

# ---- NSLookup / DNS ----

def nslookup_host(target):
    command = ["nslookup", target]
    raw = run_subprocess(command)
    extra = dns_records_basic(target)
    return raw + "\n=== DNS Summary ===\n" + extra

def dns_records_basic(target):
    try:
        host, aliases, addrs = socket.gethostbyname_ex(target)
        lines = []
        lines.append(f"Host: {host}")
        if aliases:
            lines.append("Aliases:")
            for a in aliases:
                lines.append(f"  {a}")
        if addrs:
            lines.append("Addresses:")
            for ip in addrs:
                lines.append(f"  {ip}")
        return "\n".join(lines) + "\n"
    except Exception as e:
        return f"DNS lookup error: {e}\n"

def reverse_dns(ip):
    try:
        host, aliases, addrs = socket.gethostbyaddr(ip)
        lines = [f"Host: {host}"]
        if aliases:
            lines.append("Aliases:")
            for a in aliases:
                lines.append(f"  {a}")
        if addrs:
            lines.append("Addresses:")
            for a in addrs:
                lines.append(f"  {a}")
        return "\n".join(lines) + "\n"
    except Exception as e:
        return f"Reverse DNS error: {e}\n"

# ---- Nmap ----

def nmap_scan(target, ports=None, args=None):
    if args is None:
        args = "-sV"
    cmd = ["nmap"]
    if args:
        cmd.extend(args.split())
    if ports:
        cmd.extend(["-p", ports])
    cmd.append(target)
    raw = run_subprocess(cmd)
    summary = summarize_nmap(raw)
    return raw + summary

def summarize_nmap(raw):
    open_ports = []
    for line in raw.splitlines():
        if re.search(r"open", line) and re.search(r"/tcp|/udp", line):
            open_ports.append(line.strip())
    lines = []
    lines.append("")
    lines.append("=== Nmap Summary ===")
    if open_ports:
        lines.append(f"Open services detected: {len(open_ports)}")
        for l in open_ports:
            lines.append(f"  {l}")
    else:
        lines.append("No open services detected (or scan incomplete).")
    return "\n".join(lines) + "\n"

# ---- Port Scan + Banner ----

def port_scan(target, start_port, end_port, timeout=0.5):
    results = []
    for port in range(start_port, end_port + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            if s.connect_ex((target, port)) == 0:
                banner = grab_banner(target, port, timeout=timeout)
                results.append((port, banner))
        except Exception:
            pass
        finally:
            s.close()
    return results

def grab_banner(target, port, timeout=0.5):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((target, port))
        if port in (80, 8080, 8000, 443):
            try:
                s.sendall(b"HEAD / HTTP/1.0\r\nHost: %b\r\n\r\n" % target.encode())
            except Exception:
                pass
        try:
            data = s.recv(4096)
        except Exception:
            data = b""
        s.close()
        if not data:
            return "<no banner>"
        text = data.decode(errors="ignore").strip()
        first_line = text.splitlines()[0] if text.splitlines() else text
        return first_line[:200]
    except Exception:
        return "<no banner>"

# ---- WHOIS ----

def whois_lookup(target):
    if not REQUIRED_TOOLS["whois"]["installed"]:
        return "python-whois module not installed.\nInstall it from Settings.\n"
    import whois
    try:
        w = whois.whois(target)
        lines = []
        lines.append("=== Raw WHOIS ===")
        lines.append(json.dumps(w, indent=2, default=str))
        lines.append("")
        lines.append("=== WHOIS Summary ===")
        registrar = w.get("registrar")
        created = w.get("creation_date")
        expires = w.get("expiration_date")
        if isinstance(created, list):
            created = created[0]
        if isinstance(expires, list):
            expires = expires[0]
        lines.append(f"Registrar: {registrar}")
        lines.append(f"Created: {created}")
        lines.append(f"Expires: {expires}")
        if created:
            try:
                if isinstance(created, str):
                    created_dt = datetime.datetime.fromisoformat(str(created).replace("Z", "+00:00"))
                else:
                    created_dt = created
                age_days = (datetime.datetime.utcnow() - created_dt.replace(tzinfo=None)).days
                lines.append(f"Domain Age: {age_days} days (~{age_days/365:.1f} years)")
            except Exception:
                pass
        if expires:
            try:
                if isinstance(expires, str):
                    exp_dt = datetime.datetime.fromisoformat(str(expires).replace("Z", "+00:00"))
                else:
                    exp_dt = expires
                days_left = (exp_dt.replace(tzinfo=None) - datetime.datetime.utcnow()).days
                lines.append(f"Days until expiration: {days_left} days")
            except Exception:
                pass
        return "\n".join(lines) + "\n"
    except Exception as e:
        return f"WHOIS error: {e}\n"

# ---- HTTP Headers & Security ----

def http_headers(target, use_https=True):
    try:
        port = 443 if use_https else 80
        conn_class = http.client.HTTPSConnection if use_https else http.client.HTTPConnection
        conn = conn_class(target, port=port, timeout=5)
        conn.request("GET", "/")
        resp = conn.getresponse()
        headers = resp.getheaders()
        lines = [f"Status: {resp.status} {resp.reason}", ""]
        for k, v in headers:
            lines.append(f"{k}: {v}")
        conn.close()
        lines.append("")
        lines.append("=== HTTP Security Analysis ===")
        header_dict = {k.lower(): v for k, v in headers}
        if "strict-transport-security" in header_dict:
            lines.append("HSTS: ENABLED")
        else:
            lines.append("HSTS: NOT PRESENT")
        if "content-security-policy" in header_dict:
            lines.append("CSP: PRESENT")
        else:
            lines.append("CSP: NOT PRESENT")
        if "x-frame-options" in header_dict:
            lines.append(f"X-Frame-Options: {header_dict['x-frame-options']}")
        else:
            lines.append("X-Frame-Options: NOT PRESENT")
        if "x-content-type-options" in header_dict:
            lines.append(f"X-Content-Type-Options: {header_dict['x-content-type-options']}")
        else:
            lines.append("X-Content-Type-Options: NOT PRESENT")
        if "x-xss-protection" in header_dict:
            lines.append(f"X-XSS-Protection: {header_dict['x-xss-protection']}")
        else:
            lines.append("X-XSS-Protection: NOT PRESENT")
        server = header_dict.get("server")
        if server:
            lines.append(f"Server: {server}")
        return "\n".join(lines) + "\n"
    except Exception as e:
        return f"HTTP header fetch error: {e}\n"

# ---- ARP ----

def arp_table():
    if platform.system().lower() == "windows":
        cmd = ["arp", "-a"]
    else:
        cmd = ["arp", "-n"]
    raw = run_subprocess(cmd)
    return raw

# ---- SSL Certificate ----

def ssl_certificate_info(target, port=443):
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((target, port), timeout=5) as sock:
            with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                proto = ssock.version()
        lines = []
        lines.append(f"SSL/TLS Protocol: {proto}")
        lines.append(f"Cipher: {cipher}")
        lines.append("")
        lines.append("=== Certificate Details ===")
        lines.append(json.dumps(cert, indent=2, default=str))
        not_before = cert.get("notBefore")
        not_after = cert.get("notAfter")
        if not_before and not_after:
            try:
                fmt = "%b %d %H:%M:%S %Y %Z"
                nb = datetime.datetime.strptime(not_before, fmt)
                na = datetime.datetime.strptime(not_after, fmt)
                now = datetime.datetime.utcnow()
                days_total = (na - nb).days
                days_left = (na - now).days
                lines.append("")
                lines.append("=== Certificate Lifetime ===")
                lines.append(f"Valid From: {not_before}")
                lines.append(f"Valid To:   {not_after}")
                lines.append(f"Total Lifetime: {days_total} days")
                lines.append(f"Days Until Expiration: {days_left} days")
            except Exception:
                pass
        issuer = cert.get("issuer")
        subject = cert.get("subject")
        if issuer:
            lines.append("")
            lines.append("Issuer:")
            lines.append(str(issuer))
        if subject:
            lines.append("")
            lines.append("Subject:")
            lines.append(str(subject))
        return "\n".join(lines) + "\n"
    except Exception as e:
        return f"SSL certificate error: {e}\n"

# ---- GeoIP ----

def geoip_lookup(target):
    if not REQUIRED_TOOLS["requests"]["installed"]:
        return "requests module not installed.\nInstall it from Settings.\n"
    import requests
    try:
        url = f"https://ipinfo.io/{target}/json"
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return f"GeoIP error: HTTP {r.status_code}\n"
        data = r.json()
        lines = []
        lines.append("=== Raw GeoIP ===")
        lines.append(json.dumps(data, indent=2))
        lines.append("")
        lines.append("=== GeoIP Summary ===")
        ip = data.get("ip")
        city = data.get("city")
        region = data.get("region")
        country = data.get("country")
        loc = data.get("loc")
        org = data.get("org")
        postal = data.get("postal")
        timezone = data.get("timezone")
        asn = data.get("asn") if isinstance(data.get("asn"), dict) else None

        lines.append(f"IP: {ip}")
        lines.append(f"Location: {', '.join([p for p in [city, region, country] if p])}")
        lines.append(f"Coordinates: {loc}")
        lines.append(f"Postal: {postal}")
        lines.append(f"Timezone: {timezone}")
        lines.append(f"Org/ISP: {org}")
        if asn:
            lines.append(f"ASN: {asn.get('asn')} ({asn.get('name')})")
        return "\n".join(lines) + "\n"
    except Exception as e:
        return f"GeoIP error: {e}\n"

# ---- Speedtest ----

def speedtest_run():
    if REQUIRED_TOOLS["speedtest"]["installed"]:
        try:
            import speedtest
            st = speedtest.Speedtest()
            st.get_best_server()
            dl = st.download() / 1_000_000
            ul = st.upload() / 1_000_000
            ping = st.results.ping
            s = st.get_best_server()
            lines = [
                "Speedtest (speedtest-cli module):",
                f"Server: {s.get('sponsor')} ({s.get('name')}, {s.get('country')})",
                f"Distance: {s.get('d')} km",
                f"Ping: {ping:.2f} ms",
                f"Download: {dl:.2f} Mbps",
                f"Upload: {ul:.2f} Mbps",
            ]
            return "\n".join(lines) + "\n"
        except Exception as e:
            return f"Speedtest error: {e}\n"
    else:
        if check_command_available("speedtest"):
            return run_subprocess(["speedtest", "--simple"])
        return "speedtest-cli not installed.\nInstall it from Settings.\n"

# ---- Local Interface Info ----

def local_interface_info():
    lines = []
    try:
        hostname = socket.gethostname()
        lines.append(f"Hostname: {hostname}")
        try:
            ip = socket.gethostbyname(hostname)
            lines.append(f"Primary IP: {ip}")
        except Exception:
            lines.append("Primary IP: <unavailable>")
    except Exception as e:
        lines.append(f"Hostname error: {e}")

    lines.append("")
    lines.append("Basic Interfaces (via getaddrinfo):")
    try:
        addrs = socket.getaddrinfo(hostname, None)
        seen = set()
        for a in addrs:
            ip = a[4][0]
            if ip not in seen:
                seen.add(ip)
                lines.append(f"  {ip}")
    except Exception as e:
        lines.append(f"Interface error: {e}")

    lines.append("")
    lines.append("Routing Table (best-effort):")
    if platform.system().lower() == "windows":
        lines.append(run_subprocess(["route", "print"]))
    else:
        lines.append(run_subprocess(["ip", "route"]))

    return "\n".join(lines) + "\n"

# ---- Reverse IP (simple) ----

def reverse_ip_lookup(target):
    if not REQUIRED_TOOLS["requests"]["installed"]:
        return "requests module not installed.\nInstall it from Settings.\n"
    import requests
    try:
        ip = target
        try:
            ip = socket.gethostbyname(target)
        except Exception:
            pass
        # Simple free-style: use ipinfo's "domains" if available
        r = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        if r.status_code != 200:
            return f"Reverse IP error: HTTP {r.status_code}\n"
        data = r.json()
        lines = []
        lines.append("=== Reverse IP (via ipinfo.io) ===")
        lines.append(f"IP: {ip}")
        org = data.get("org")
        if org:
            lines.append(f"Org/ISP: {org}")
        domains = data.get("domains")
        if domains:
            lines.append("")
            lines.append("Domains on this IP:")
            for d in domains:
                lines.append(f"  - {d}")
        else:
            lines.append("No domain list available from this source.")
        return "\n".join(lines) + "\n"
    except Exception as e:
        return f"Reverse IP error: {e}\n"

# ---- Simple Tech Fingerprint ----

def tech_fingerprint(target):
    try:
        port = 443
        conn = http.client.HTTPSConnection(target, port=port, timeout=5)
        conn.request("GET", "/")
        resp = conn.getresponse()
        headers = resp.getheaders()
        body = resp.read(8192).decode(errors="ignore")
        conn.close()
    except Exception:
        try:
            port = 80
            conn = http.client.HTTPConnection(target, port=port, timeout=5)
            conn.request("GET", "/")
            resp = conn.getresponse()
            headers = resp.getheaders()
            body = resp.read(8192).decode(errors="ignore")
            conn.close()
        except Exception as e:
            return f"Tech fingerprint error: {e}\n"

    header_dict = {k.lower(): v for k, v in headers}
    lines = []
    lines.append("=== HTTP Technology Fingerprint (heuristic) ===")
    server = header_dict.get("server")
    powered = header_dict.get("x-powered-by")
    if server:
        lines.append(f"Server: {server}")
    if powered:
        lines.append(f"X-Powered-By: {powered}")

    techs = []

    if "wordpress" in body.lower():
        techs.append("WordPress")
    if "wp-content" in body.lower():
        techs.append("WordPress (wp-content)")
    if "drupal" in body.lower():
        techs.append("Drupal")
    if "joomla" in body.lower():
        techs.append("Joomla")
    if "shopify" in body.lower():
        techs.append("Shopify")
    if "woocommerce" in body.lower():
        techs.append("WooCommerce")
    if "cloudflare" in (server or "").lower():
        techs.append("Cloudflare (CDN/WAF)")
    if "akamai" in (server or "").lower():
        techs.append("Akamai (CDN)")
    if "nginx" in (server or "").lower():
        techs.append("nginx")
    if "apache" in (server or "").lower():
        techs.append("Apache HTTPD")
    if "iis" in (server or "").lower():
        techs.append("Microsoft IIS")

    if techs:
        lines.append("Detected Technologies:")
        for t in sorted(set(techs)):
            lines.append(f"  - {t}")
    else:
        lines.append("No specific technologies confidently detected from this heuristic scan.")

    return "\n".join(lines) + "\n"

# ---- Network Health Summary ----

def network_health_summary(target):
    lines = []
    lines.append(f"=== Network Health Summary for {target} ===")
    lines.append("")

    # Ping
    try:
        ping_res = ping_host(target)
        lines.append("--- Ping ---")
        lines.append(ping_res.split("=== Ping Analysis ===")[-1].strip())
        lines.append("")
    except Exception as e:
        lines.append(f"Ping: error: {e}")
        lines.append("")

    # DNS
    try:
        dns_res = dns_records_basic(target)
        lines.append("--- DNS ---")
        lines.append(dns_res.strip())
        lines.append("")
    except Exception as e:
        lines.append(f"DNS: error: {e}")
        lines.append("")

    # SSL
    try:
        ssl_res = ssl_certificate_info(target)
        lines.append("--- SSL/TLS ---")
        lines.append(ssl_res.strip())
        lines.append("")
    except Exception as e:
        lines.append(f"SSL: error: {e}")
        lines.append("")

    # HTTP Security
    try:
        http_res = http_headers(target, use_https=True)
        lines.append("--- HTTPS Security ---")
        lines.append(http_res.strip())
        lines.append("")
    except Exception as e:
        lines.append(f"HTTPS: error: {e}")
        lines.append("")

    # GeoIP
    try:
        geo_res = geoip_lookup(target)
        lines.append("--- GeoIP ---")
        lines.append(geo_res.strip())
        lines.append("")
    except Exception as e:
        lines.append(f"GeoIP: error: {e}")
        lines.append("")

    # Tech Fingerprint
    try:
        tech_res = tech_fingerprint(target)
        lines.append("--- Web Technology ---")
        lines.append(tech_res.strip())
        lines.append("")
    except Exception as e:
        lines.append(f"Tech Fingerprint: error: {e}")
        lines.append("")

    lines.append("=== End of Summary ===")
    return "\n".join(lines) + "\n"

# =============================
# Main App
# =============================

class NetTraceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NetTrace Beta - Network Toolkit")
        self.root.geometry("1200x750")

        self.widgets_registry = {
            "frame": [],
            "label": [],
            "status": [],
            "button": [],
            "entry": [],
            "output": [],
            "notebook": [],
        }

        self.status_text = tk.StringVar(value="Ready")
        self.shared_target = tk.StringVar()

        self.theme_manager = ThemeManager(self.root, self.widgets_registry)
        self.animation_manager = None
        self.scanline_overlay = None
        self.scanline_mode = tk.StringVar(value="Off")

        self.build_ui()
        self.theme_manager.apply_theme("Terminal Classic")

    def register(self, wtype, widget):
        if wtype in self.widgets_registry:
            self.widgets_registry[wtype].append(widget)

    def set_status(self, text, animate=True):
        self.status_text.set(text)
        if animate and self.animation_manager:
            self.animation_manager.start_status_pulse()
        elif self.animation_manager:
            self.animation_manager.stop_status_pulse()

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, pady=5)
        self.register("frame", top_frame)

        title_label = tk.Label(
            top_frame,
            text="NetTrace Beta",
            font=("Cascadia Mono", 20, "bold"),
        )
        title_label.pack(side=tk.LEFT, padx=10)
        self.register("label", title_label)

        subtitle_label = tk.Label(
            top_frame,
            text="Deep Network Intelligence Toolkit - Built by Eskee",
            font=("Consolas", 12),
        )
        subtitle_label.pack(side=tk.LEFT, padx=10)
        self.register("label", subtitle_label)

        target_outer = tk.Frame(self.root)
        target_outer.pack(fill=tk.X, padx=10, pady=5)
        self.register("frame", target_outer)

        border_top = tk.Label(target_outer, text="┌" + "─" * 100 + "┐", font=("Consolas", 10))
        border_top.pack(anchor="w")
        self.register("label", border_top)

        middle_frame = tk.Frame(target_outer)
        middle_frame.pack(fill=tk.X)
        self.register("frame", middle_frame)

        left_label = tk.Label(middle_frame, text="│  Target:  ", font=("Consolas", 10))
        left_label.pack(side=tk.LEFT)
        self.register("label", left_label)

        target_entry = tk.Entry(middle_frame, textvariable=self.shared_target, font=("Consolas", 10))
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.register("entry", target_entry)

        right_label = tk.Label(middle_frame, text="  │", font=("Consolas", 10))
        right_label.pack(side=tk.LEFT)
        self.register("label", right_label)

        border_bottom = tk.Label(target_outer, text="└" + "─" * 100 + "┘", font=("Consolas", 10))
        border_bottom.pack(anchor="w")
        self.register("label", border_bottom)

        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.register("frame", content_frame)

        notebook = ttk.Notebook(content_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        self.register("notebook", notebook)

        self.build_tab_ping(notebook)
        self.build_tab_traceroute(notebook)
        self.build_tab_nslookup(notebook)
        self.build_tab_nmap(notebook)
        self.build_tab_portscan(notebook)
        self.build_tab_extras(notebook)
        self.build_tab_advanced(notebook)
        self.build_tab_summary(notebook)
        self.build_tab_settings(notebook)

        self.scanline_overlay = ScanlineOverlay(content_frame, self.theme_manager)
        content_frame.bind("<Configure>", self.scanline_overlay.resize)

        status_frame = tk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.register("frame", status_frame)

        status_label = tk.Label(
            status_frame,
            textvariable=self.status_text,
            anchor="w",
            font=("Consolas", 10),
        )
        status_label.pack(fill=tk.X, padx=5, pady=3)
        self.register("status", status_label)

        self.animation_manager = AnimationManager(self.root, status_label, self.theme_manager)

    def get_target(self):
        target = self.shared_target.get().strip()
        if not target:
            messagebox.showwarning("No target", "Please enter a host, IP, or domain in the Target bar.")
            return None
        return target

    def create_output_box(self, parent):
        output = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            font=("Consolas", 10),
        )
        output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.register("output", output)
        return output

    def create_button_row(self, parent, buttons):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        self.register("frame", frame)

        for text, cmd in buttons:
            btn = tk.Button(frame, text=text, command=cmd, font=("Consolas", 10))
            btn.pack(side=tk.LEFT, padx=5)
            self.register("button", btn)

    # Tabs

    def build_tab_ping(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="Ping")
        self.register("frame", frame)

        output = self.create_output_box(frame)

        def do_ping():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Pinging {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = ping_host(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        self.create_button_row(frame, [("Ping", do_ping)])

    def build_tab_traceroute(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="Traceroute")
        self.register("frame", frame)

        output = self.create_output_box(frame)

        def do_traceroute():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Running traceroute to {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = traceroute_host(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        self.create_button_row(frame, [("Traceroute", do_traceroute)])

    def build_tab_nslookup(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="DNS / NSLookup")
        self.register("frame", frame)

        output = self.create_output_box(frame)

        def do_nslookup():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Running nslookup for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = nslookup_host(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_reverse_dns():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Reverse DNS for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                try:
                    ip = target
                    if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", target):
                        ip = socket.gethostbyname(target)
                    result = reverse_dns(ip)
                except Exception as e:
                    result = f"Reverse DNS error: {e}\n"
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        self.create_button_row(
            frame,
            [
                ("NSLookup + Summary", do_nslookup),
                ("Reverse DNS", do_reverse_dns),
            ],
        )

    def build_tab_nmap(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="Nmap")
        self.register("frame", frame)

        ports_frame = tk.Frame(frame)
        ports_frame.pack(fill=tk.X, pady=5)
        self.register("frame", ports_frame)

        ports_label = tk.Label(ports_frame, text="Ports (e.g. 80,443 or 1-1024):", font=("Consolas", 10))
        ports_label.pack(side=tk.LEFT, padx=5)
        self.register("label", ports_label)

        ports_entry = tk.Entry(ports_frame, font=("Consolas", 10))
        ports_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.register("entry", ports_entry)

        args_frame = tk.Frame(frame)
        args_frame.pack(fill=tk.X, pady=5)
        self.register("frame", args_frame)

        args_label = tk.Label(args_frame, text="Nmap Args (default: -sV):", font=("Consolas", 10))
        args_label.pack(side=tk.LEFT, padx=5)
        self.register("label", args_label)

        args_entry = tk.Entry(args_frame, font=("Consolas", 10))
        args_entry.insert(0, "-sV")
        args_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.register("entry", args_entry)

        output = self.create_output_box(frame)

        def do_nmap():
            target = self.get_target()
            if not target:
                return
            ports = ports_entry.get().strip() or None
            args = args_entry.get().strip() or "-sV"
            self.set_status(f"Running nmap on {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = nmap_scan(target, ports=ports, args=args)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        self.create_button_row(frame, [("Run Nmap", do_nmap)])

    def build_tab_portscan(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="Port Scan")
        self.register("frame", frame)

        range_frame = tk.Frame(frame)
        range_frame.pack(fill=tk.X, pady=5)
        self.register("frame", range_frame)

        start_label = tk.Label(range_frame, text="Start Port:", font=("Consolas", 10))
        start_label.pack(side=tk.LEFT, padx=5)
        self.register("label", start_label)

        start_entry = tk.Entry(range_frame, width=8, font=("Consolas", 10))
        start_entry.insert(0, "1")
        start_entry.pack(side=tk.LEFT, padx=5)
        self.register("entry", start_entry)

        end_label = tk.Label(range_frame, text="End Port:", font=("Consolas", 10))
        end_label.pack(side=tk.LEFT, padx=5)
        self.register("label", end_label)

        end_entry = tk.Entry(range_frame, width=8, font=("Consolas", 10))
        end_entry.insert(0, "1024")
        end_entry.pack(side=tk.LEFT, padx=5)
        self.register("entry", end_entry)

        output = self.create_output_box(frame)

        def do_portscan():
            target = self.get_target()
            if not target:
                return
            try:
                start_port = int(start_entry.get().strip())
                end_port = int(end_entry.get().strip())
            except ValueError:
                messagebox.showerror("Invalid ports", "Start and end ports must be integers.")
                return
            if start_port < 1 or end_port > 65535 or start_port > end_port:
                messagebox.showerror("Invalid range", "Port range must be between 1 and 65535 and start <= end.")
                return

            self.set_status(f"Scanning ports {start_port}-{end_port} on {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                results = port_scan(target, start_port, end_port)
                if results:
                    lines = [f"Open ports on {target}:"]
                    for p, banner in results:
                        lines.append(f"  - {p}: {banner}")
                    result = "\n".join(lines) + "\n"
                else:
                    result = f"No open ports found on {target} in range {start_port}-{end_port}.\n"
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        self.create_button_row(frame, [("Scan Ports + Banners", do_portscan)])

    def build_tab_extras(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="Extra Tools")
        self.register("frame", frame)

        output = self.create_output_box(frame)

        def do_whois():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Running WHOIS for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = whois_lookup(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_dns():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"DNS lookup for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = dns_records_basic(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_http_headers():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Fetching HTTPS headers from {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = http_headers(target, use_https=True)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_arp():
            self.set_status("Reading ARP table...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = arp_table()
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_reverse_ip():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Reverse IP lookup for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = reverse_ip_lookup(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        self.create_button_row(
            frame,
            [
                ("WHOIS + Age", do_whois),
                ("DNS Summary", do_dns),
                ("HTTPS Headers + Security", do_http_headers),
                ("ARP Table", do_arp),
                ("Reverse IP", do_reverse_ip),
            ],
        )

    def build_tab_advanced(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="Advanced")
        self.register("frame", frame)

        output = self.create_output_box(frame)

        def do_ssl():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Inspecting SSL certificate for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = ssl_certificate_info(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_geoip():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"GeoIP lookup for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = geoip_lookup(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_speedtest():
            self.set_status("Running speedtest...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = speedtest_run()
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_localinfo():
            self.set_status("Gathering local interface info...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = local_interface_info()
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        def do_tech_fingerprint():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Fingerprinting web stack for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = tech_fingerprint(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        self.create_button_row(
            frame,
            [
                ("SSL Certificate + Lifetime", do_ssl),
                ("GeoIP (rich)", do_geoip),
                ("Speed Test", do_speedtest),
                ("Local Interfaces + Routes", do_localinfo),
                ("Web Tech Fingerprint", do_tech_fingerprint),
            ],
        )

    def build_tab_summary(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="Summary")
        self.register("frame", frame)

        output = self.create_output_box(frame)

        def do_summary():
            target = self.get_target()
            if not target:
                return
            self.set_status(f"Building network health summary for {target}...", animate=True)
            output.delete("1.0", tk.END)

            def worker():
                result = network_health_summary(target)
                self.animation_manager.fade_in_output(output, result)
                self.set_status("Idle", animate=False)

            run_in_thread(worker)

        self.create_button_row(frame, [("Run Full Summary", do_summary)])

    def build_tab_settings(self, notebook):
        frame = tk.Frame(notebook)
        notebook.add(frame, text="Settings")
        self.register("frame", frame)

        label = tk.Label(frame, text="Theme Selection", font=("Consolas", 16, "bold"))
        label.pack(pady=10)
        self.register("label", label)

        theme_frame = tk.Frame(frame)
        theme_frame.pack(pady=5)
        self.register("frame", theme_frame)

        for theme_name in self.theme_manager.themes.keys():
            btn = tk.Button(
                theme_frame,
                text=theme_name,
                font=("Consolas", 10),
                command=lambda n=theme_name: self.change_theme(n),
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.register("button", btn)

        scanline_label = tk.Label(frame, text="Scanline Mode", font=("Consolas", 16, "bold"))
        scanline_label.pack(pady=10)
        self.register("label", scanline_label)

        scanline_frame = tk.Frame(frame)
        scanline_frame.pack(pady=5)
        self.register("frame", scanline_frame)

        modes = ["Off", "Soft", "Medium", "Heavy", "Dynamic"]
        scanline_dropdown = ttk.Combobox(
            scanline_frame,
            textvariable=self.scanline_mode,
            values=modes,
            state="readonly",
            width=15,
        )
        scanline_dropdown.pack(side=tk.LEFT, padx=5)
        self.register("entry", scanline_dropdown)

        apply_scanline_btn = tk.Button(
            scanline_frame,
            text="Apply",
            font=("Consolas", 10),
            command=self.apply_scanline_mode,
        )
        apply_scanline_btn.pack(side=tk.LEFT, padx=5)
        self.register("button", apply_scanline_btn)

        info_label = tk.Label(
            frame,
            text="Animations: status pulse + output fade-in are always enabled.\nScanlines affect only the main content area.",
            font=("Consolas", 9),
            justify=tk.LEFT,
        )
        info_label.pack(pady=10)
        self.register("label", info_label)

        tools_label = tk.Label(frame, text="Optional Tools (Modules)", font=("Consolas", 16, "bold"))
        tools_label.pack(pady=10)
        self.register("label", tools_label)

        tools_frame = tk.Frame(frame)
        tools_frame.pack(pady=5)
        self.register("frame", tools_frame)

        for key, info in REQUIRED_TOOLS.items():
            row = tk.Frame(tools_frame)
            row.pack(fill=tk.X, pady=2)
            self.register("frame", row)

            status = "Installed" if info["installed"] else "Missing"
            text = f"{info['module']} ({info['pip']}): {status}"
            lbl = tk.Label(row, text=text, font=("Consolas", 10))
            lbl.pack(side=tk.LEFT, padx=5)
            self.register("label", lbl)

            if not info["installed"]:
                btn = tk.Button(
                    row,
                    text=f"Install {info['pip']}",
                    font=("Consolas", 9),
                    command=lambda k=key: self.install_tool(k),
                )
                btn.pack(side=tk.LEFT, padx=5)
                self.register("button", btn)

    def change_theme(self, theme_name):
        self.theme_manager.apply_theme(theme_name)
        self.set_status(f"Theme changed to {theme_name}", animate=False)
        self.scanline_overlay.draw_scanlines()

    def apply_scanline_mode(self):
        mode = self.scanline_mode.get()
        self.scanline_overlay.set_mode(mode)
        self.set_status(f"Scanline mode: {mode}", animate=False)

    def install_tool(self, key):
        info = REQUIRED_TOOLS[key]
        pip_name = info["pip"]
        self.set_status(f"Installing {pip_name}...", animate=True)

        def worker():
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
                info["installed"] = True
                self.set_status(f"Installed {pip_name}. Restart NetTrace for full effect.", animate=False)
                messagebox.showinfo("Installed", f"{pip_name} installed.\nRestart NetTrace to reload modules.")
            except Exception as e:
                self.set_status("Idle", animate=False)
                messagebox.showerror("Install failed", f"Failed to install {pip_name}:\n{e}")

        run_in_thread(worker)


if __name__ == "__main__":
    root = tk.Tk()
    app = NetTraceApp(root)
    root.mainloop()

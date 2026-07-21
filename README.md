# PenTest Toolkit v1.0

Educational security testing framework with full RGB color UI. Created by **M.S.J**.

```
     ____           ______          __
    / __ \___  ____/_  __/__  _____/ /_
   / /_/ / _ \/ __ \/ / / _ \/ ___/ __/
  / ____/  __/ / / / / /  __(__  ) /_
 /_/    \___/_/ /_/_/  \___/____/\__/
```

## Features

| Module | Description |
|--------|-------------|
| **Port Scanner** | TCP connect, SYN stealth, UDP scan with service/banner detection |
| **DNS Enumeration** | A/AAAA/MX/NS/TXT/SOA/CNAME records, subdomain brute-force (90+ wordlist), zone transfer |
| **Directory Buster** | Path discovery (100+ paths, 16 extensions), threaded, redirect tracking |
| **HTTP Analyzer** | Header analysis, security header audit, HTTP method check, endpoint discovery, SSL/TLS cert check, weak cipher detection |
| **Network Recon** | WHOIS lookup, geo-IP location, traceroute, SMB share enumeration, ping sweep, common vuln checks |

## Quick Start

### Guided Installation
```bash
git clone https://github.com/hotsuper901/pen-tool.git
cd pen-tool
pip install -r requirements.txt
python3 pentest.py
```

### Usage
```bash
# Interactive HUD menu
python3 pentest.py

# CLI mode
python3 pentest.py scanme.nmap.org --scan
python3 pentest.py example.com --dns --brute
python3 pentest.py 192.168.1.1 --all
```

## Usage

### Interactive Mode

```
python3 pentest.py
```

Launches a menu-driven HUD interface. Navigate with arrow keys or number input, enter target, configure options.

### CLI Mode

```
python3 pentest.py <target> [options]
```

| Flag | Description |
|------|-------------|
| `--scan` | Port scan (TCP) |
| `--stealth` | SYN stealth scan |
| `--udp` | UDP scan |
| `--dns` | DNS record enumeration |
| `--brute` | Subdomain brute-force |
| `--dirbust` | Directory busting |
| `--http` | HTTP header analysis |
| `--methods` | Check HTTP methods |
| `--endpoints` | Check common endpoints |
| `--ssl` | SSL/TLS certificate check |
| `--recon` | Network recon |
| `--geo` | IP geolocation |
| `--whois` | WHOIS lookup |
| `--trace` | Traceroute |
| `--smb` | SMB enumeration |
| `--all` | Run all modules |
| `--theme` | Color theme (cyberpunk/matrix/fire/ocean/neon) |
| `--ports` | Port range (default: 1-1024) |
| `--timeout` | Request timeout (default: 3s) |
| `--threads` | Thread count (default: 50) |
| `--wordlist` | Custom wordlist file |
| `--ext` | File extensions (e.g., .php,.asp) |

### Examples

```bash
python3 pentest.py scanme.nmap.org --scan --ports 22,80,443
python3 pentest.py example.com --dns --brute --zone
python3 pentest.py example.com --http --ssl --methods
python3 pentest.py example.com --dirbust --ext .php,.asp --port 80
python3 pentest.py 192.168.1.0/24 --recon --ping
python3 pentest.py scanme.nmap.org --all
python3 pentest.py example.com --recon --geo --whois --trace
```

## Modules

### Port Scanner
- TCP connect scan with configurable port range
- Service fingerprinting via 70+ common port mapping
- Banner grabbing on open ports
- SYN stealth scan (limited port set)
- UDP probe scan

### DNS Enumeration
- Full DNS record enumeration (A, AAAA, MX, NS, TXT, SOA, CNAME, SRV, CAA)
- Subdomain brute-force (90+ common subdomains)
- DNS zone transfer attempt
- Wildcard DNS detection

### Directory Buster
- 100+ common web paths
- 16 file extension variants
- Concurrent threading
- Redirect and auth detection

### HTTP Analyzer
- Response header analysis
- Security header audit (HSTS, CSP, XFO, XCTO, XSS, Referrer-Policy, Permissions-Policy)
- HTTP method discovery
- Common endpoint detection
- SSL/TLS certificate inspection
- Weak cipher detection

### Network Reconnaissance
- WHOIS domain lookup
- IP geolocation (ip-api.com)
- Traceroute
- SMB share enumeration
- Ping sweep (CIDR)
- Common vulnerability checks (phpinfo, .git exposure, admin panels, etc.)

## Themes

```
--theme cyberpunk   Cyan/magenta (default)
--theme matrix      Green on black
--theme fire        Orange/red
--theme ocean       Blue/teal
--theme neon        Magenta/cyan
```

## Requirements

- Python 3.8+
- rich>=13.0.0
- pyfiglet>=1.0.0
- requests>=2.31.0
- dnspython>=2.4.0
- urllib3>=2.0.0

## License

For authorized testing and educational purposes only.
# pen-tool

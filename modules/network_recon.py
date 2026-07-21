import socket
import subprocess
import platform
import requests
from .rhud import console

def whois_lookup(domain):
    console.print(f"  [#00ccff]▶[/] WHOIS lookup for [bold]{domain}[/]")
    try:
        result = subprocess.run(["whois", domain], capture_output=True, text=True, timeout=10)
        for line in result.stdout[:2000].split("\n"):
            if line.strip():
                console.print(f"    {line}")
        return result.stdout
    except FileNotFoundError:
        console.print("  [bold #ff3c3c]✗[/] whois not found (apt install whois)")
    except subprocess.TimeoutExpired:
        console.print("  [bold #ff3c3c]✗[/] WHOIS timed out")
    return None

def geolocate_ip(ip):
    console.print(f"  [#00ccff]▶[/] Geolocating [bold]{ip}[/]")
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = r.json()
        if data.get("status") == "success":
            for k in ["country", "regionName", "city", "isp", "org", "as"]:
                console.print(f"    [bold #ffff64]{k}:[/] {data.get(k, 'N/A')}")
            console.print(f"    [bold #ffff64]Lat/Lon:[/] {data.get('lat')}, {data.get('lon')}")
            return data
        else:
            console.print(f"    [bold #ff3c3c]✗[/] {data.get('message', 'Failed')}")
    except Exception as e:
        console.print(f"    [bold #ff3c3c]✗[/] {e}")
    return None

def traceroute(target, max_hops=30):
    console.print(f"  [#00ccff]▶[/] Traceroute to [bold]{target}[/]")
    try:
        ip = socket.gethostbyname(target)
        console.print(f"    [bold #ffff64]Target IP:[/] {ip}")
    except:
        ip = target
    cmd = ["tracert", "-h", str(max_hops), target] if platform.system() == "Windows" else ["traceroute", "-m", str(max_hops), target]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        for line in result.stdout[:2000].split("\n"):
            if line.strip():
                console.print(f"    {line}")
        return result.stdout
    except FileNotFoundError:
        console.print("  [bold #ff3c3c]✗[/] traceroute not found")
    except subprocess.TimeoutExpired:
        console.print("  [bold #ff3c3c]✗[/] Traceroute timed out")
    return None

class NetworkScanner:
    def __init__(self, subnet):
        self.subnet = subnet

    def ping_sweep(self):
        import ipaddress
        live = []
        console.print(f"  [#00ccff]▶[/] Ping sweeping [bold]{self.subnet}[/]")
        try:
            for ip in ipaddress.ip_network(self.subnet, strict=False).hosts():
                ip_str = str(ip)
                cmd = ["ping", "-n", "1", "-w", "500", ip_str] if platform.system() == "Windows" else ["ping", "-c", "1", "-W", "0.5", ip_str]
                try:
                    r = subprocess.run(cmd, capture_output=True, text=True, timeout=1)
                    if r.returncode == 0:
                        live.append(ip_str)
                        console.print(f"    [bold #00ff64]+[/] {ip_str} is alive")
                except:
                    pass
        except Exception as e:
            console.print(f"  [bold #ff3c3c]✗[/] {e}")
        return live

def check_common_vulns(target, port=80):
    scheme = "https" if port in [443, 8443] else "http"
    base = f"{scheme}://{target}:{port}"
    console.print(f"  [#00ccff]▶[/] Checking common vulns on [bold]{base}[/]")
    results = {}
    checks = {"directory_listing": f"{base}/", "phpinfo": f"{base}/phpinfo.php",
              "server_status": f"{base}/server-status", "git_exposed": f"{base}/.git/config",
              "env_exposed": f"{base}/.env", "admin_panel": f"{base}/admin",
              "wp_admin": f"{base}/wp-admin"}
    for name, url in checks.items():
        try:
            r = requests.get(url, timeout=3, verify=False, allow_redirects=False)
            if r.status_code in [200, 403]:
                results[name] = (url, r.status_code)
                console.print(f"    [bold #ffc800]![/] {name}: {url} -> {r.status_code}")
        except:
            pass
    return results

def smb_enum(target):
    console.print(f"  [#00ccff]▶[/] SMB enum on [bold]{target}[/]")
    try:
        if platform.system() != "Windows":
            result = subprocess.run(["smbclient", "-L", f"//{target}/", "-N"],
                                    capture_output=True, text=True, timeout=10)
            if result.stdout:
                console.print(f"    [#00ff64]Shares:[/]")
                for line in result.stdout[:1000].split("\n"):
                    if line.strip():
                        console.print(f"      {line}")
                return result.stdout
            else:
                console.print(f"    [bold #ff3c3c]✗[/] No SMB shares")
        else:
            console.print(f"    [bold #ff3c3c]✗[/] SMB not supported on Windows")
    except FileNotFoundError:
        console.print(f"  [bold #ff3c3c]✗[/] smbclient not found (apt install smbclient)")
    return None

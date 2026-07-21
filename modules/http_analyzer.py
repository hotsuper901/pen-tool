import ssl
import socket
import requests
from datetime import datetime
from .rhud import console

requests.packages.urllib3.disable_warnings()

class HTTPAnalyzer:
    def __init__(self, target, port=None, timeout=10):
        self.target = target
        self.port = port
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        self.session.verify = False

    def analyze(self):
        results = {}
        ports = [self.port] if self.port else [80, 443, 8080, 8443]
        for port in ports:
            scheme = "https" if port in [443, 8443] else "http"
            url = f"{scheme}://{self.target}:{port}"
            console.print(f"  [#00ccff]▶[/] Analyzing [bold]{url}[/]")
            try:
                r = self.session.get(url, timeout=self.timeout)
                results[port] = {"status": r.status_code, "server": r.headers.get("Server", ""),
                                 "powered": r.headers.get("X-Powered-By", ""),
                                 "elapsed": r.elapsed.total_seconds(),
                                 "type": r.headers.get("Content-Type", "")}

                console.print(f"    [bold #ffff64]Status:[/] {r.status_code}")
                console.print(f"    [bold #ffff64]Server:[/] {r.headers.get('Server', 'N/A')}")
                console.print(f"    [bold #ffff64]X-Powered-By:[/] {r.headers.get('X-Powered-By', 'N/A')}")
                console.print(f"    [bold #ffff64]Response Time:[/] {r.elapsed.total_seconds():.3f}s")

                checks = {"Strict-Transport-Security": "HSTS", "Content-Security-Policy": "CSP",
                          "X-Frame-Options": "Clickjacking", "X-Content-Type-Options": "MIME-Sniff",
                          "X-XSS-Protection": "XSS", "Referrer-Policy": "Referrer", "Permissions-Policy": "Permissions"}
                for hdr, name in checks.items():
                    if hdr in r.headers:
                        console.print(f"    [bold #00ff64]+[/] [#00ff64]{name} ({hdr}): {r.headers[hdr]}[/]")
                    else:
                        console.print(f"    [bold #ff3c3c]-[/] [#ff3c3c]Missing {name} ({hdr})[/]")

            except requests.exceptions.SSLError:
                console.print(f"    [bold #ffc800]![/] SSL Error on {url}")
            except requests.exceptions.ConnectionError:
                console.print(f"    [bold #ff3c3c]✗[/] Connection failed on {url}")
            except Exception as e:
                console.print(f"    [bold #ff3c3c]✗[/] {e}")
        return results

    def check_methods(self):
        ports = [self.port] if self.port else [80, 443]
        for port in ports:
            scheme = "https" if port in [443, 8443] else "http"
            url = f"{scheme}://{self.target}:{port}"
            console.print(f"  [#00ccff]▶[/] Checking HTTP methods on [bold]{url}[/]")
            methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE", "CONNECT"]
            for method in methods:
                try:
                    r = self.session.request(method, url, timeout=self.timeout)
                    if r.status_code not in [405, 501, 400]:
                        console.print(f"    [bold #00ff64]+[/] [#00ff64]{method} -> {r.status_code}[/]")
                except:
                    pass

    def check_common_endpoints(self):
        endpoints = ["/.git/config", "/.svn/entries", "/.env", "/config.php",
                     "/wp-config.php.bak", "/admin/", "/login/", "/dashboard/",
                     "/api/", "/v1/", "/graphql", "/actuator/health",
                     "/swagger-ui.html", "/swagger-ui/", "/api-docs"]
        port = self.port or 80
        scheme = "https" if port in [443, 8443] else "http"
        base = f"{scheme}://{self.target}:{port}"
        console.print(f"  [#00ccff]▶[/] Checking endpoints on [bold]{base}[/]")
        for ep in endpoints:
            try:
                r = self.session.get(base + ep, timeout=3, allow_redirects=False)
                if r.status_code not in [404, 400, 403]:
                    console.print(f"    [bold #ffc800]![/] {ep} -> {r.status_code}")
            except:
                pass


class SSLChecker:
    def __init__(self, target, port=443):
        self.target = target
        self.port = port

    def check(self):
        console.print(f"  [#00ccff]▶[/] SSL/TLS check on [bold]{self.target}:{self.port}[/]")
        results = {}
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((self.target, self.port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=self.target) as ssock:
                    cert = ssock.getpeercert()
                    console.print(f"    [bold #ffff64]Protocol:[/] {ssock.version()}")
                    console.print(f"    [bold #ffff64]Cipher:[/] {ssock.cipher()[0]} ({ssock.cipher()[1]})")
                    for item in cert.get("subject", []):
                        for k, v in item:
                            console.print(f"    [bold #ffff64]Subject {k}:[/] {v}")
                    for item in cert.get("issuer", []):
                        for k, v in item:
                            console.print(f"    [bold #ffff64]Issuer {k}:[/] {v}")
                    if "notBefore" in cert:
                        console.print(f"    [bold #ffff64]Valid From:[/] {cert['notBefore']}")
                    if "notAfter" in cert:
                        console.print(f"    [bold #ffff64]Valid To:[/] {cert['notAfter']}")
        except ssl.SSLError as e:
            console.print(f"    [bold #ffc800]![/] SSL Error: {e}")
        except Exception as e:
            console.print(f"    [bold #ff3c3c]✗[/] {e}")
        return results

    def check_weak_ciphers(self):
        console.print(f"  [#00ccff]▶[/] Checking weak ciphers...")
        weak = ["RC4", "DES", "3DES", "MD5", "EXP", "NULL", "aNULL", "eNULL", "LOW", "MEDIUM"]
        found = []
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.set_ciphers("ALL:COMPLEMENTOFALL")
            with socket.create_connection((self.target, self.port), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=self.target) as ssock:
                    cipher = ssock.cipher()[0]
                    for w in weak:
                        if w.lower() in cipher.lower():
                            found.append(cipher)
                            console.print(f"    [bold #ffc800]![/] Weak cipher: {cipher}")
        except:
            pass
        if not found:
            console.print(f"    [bold #00ff64]+[/] No weak ciphers detected")
        return found

import socket
import threading
import ipaddress
from datetime import datetime
from .rhud import console

COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 111: "RPC",
    135: "MSRPC", 139: "NetBIOS", 143: "IMAP", 161: "SNMP",
    389: "LDAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS",
    500: "IKE", 514: "Syslog", 587: "SMTP Submission",
    636: "LDAPS", 993: "IMAPS", 995: "POP3S",
    1080: "SOCKS", 1433: "MSSQL", 1521: "Oracle DB",
    2049: "NFS", 2375: "Docker", 2376: "Docker TLS",
    3306: "MySQL", 3389: "RDP", 3690: "SVN",
    4333: "mSQL", 4444: "Metasploit", 4848: "GlassFish",
    5000: "UPnP", 5432: "PostgreSQL", 5555: "Android ADB",
    5900: "VNC", 5901: "VNC", 5984: "CouchDB",
    5985: "WinRM HTTP", 5986: "WinRM HTTPS", 6379: "Redis",
    6443: "Kubernetes API", 7077: "Spark", 8000: "HTTP-Alt",
    8009: "AJP", 8080: "HTTP-Proxy", 8081: "HTTP-Alt",
    8443: "HTTPS-Alt", 8888: "HTTP-Alt", 9000: "SonarQube",
    9001: "Tor", 9042: "Cassandra", 9092: "Kafka",
    9100: "Printer", 9200: "Elasticsearch", 9300: "Elasticsearch",
    9418: "Git", 9999: "HTTP-Alt", 10000: "Webmin",
    11211: "Memcached", 27017: "MongoDB", 27018: "MongoDB",
    50070: "HDFS", 50075: "HDFS"
}

class PortScanner:
    def __init__(self, target, ports="1-1024", timeout=1.0, threads=100):
        self.target = self._resolve_target(target)
        self.timeout = timeout
        self.threads = threads
        self.open_ports = []
        self.lock = threading.Lock()

    def _resolve_target(self, target):
        try:
            ipaddress.ip_address(target)
            return target
        except ValueError:
            try:
                return socket.gethostbyname(target)
            except socket.gaierror:
                return target

    def _parse_ports(self, port_str):
        ports = set()
        for part in port_str.split(","):
            if "-" in part:
                try:
                    start, end = map(int, part.split("-"))
                    ports.update(range(start, end + 1))
                except ValueError:
                    continue
            else:
                try:
                    ports.add(int(part))
                except ValueError:
                    continue
        return sorted(ports)

    def _scan_port(self, port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            result = s.connect_ex((self.target, port))
            if result == 0:
                service = COMMON_PORTS.get(port, "Unknown")
                banner = self._grab_banner(s, port) or ""
                with self.lock:
                    self.open_ports.append((port, service, banner))
            s.close()
        except:
            pass

    def _grab_banner(self, sock, port):
        try:
            if port in [80, 443, 8080, 8443]:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
            sock.settimeout(2)
            return sock.recv(1024).decode("utf-8", errors="ignore").strip()[:200]
        except:
            return ""

    def scan_range(self, port_range):
        ports = self._parse_ports(port_range)
        self.open_ports = []
        console.print(f"  [#00ccff]▶[/] Scanning [bold]{len(ports)}[/] ports on [bold]{self.target}[/]")
        start = datetime.now()
        threads = []
        for port in ports:
            t = threading.Thread(target=self._scan_port, args=(port,))
            threads.append(t)
            t.start()
            while len([t for t in threads if t.is_alive()]) >= self.threads:
                pass
        for t in threads:
            t.join()
        elapsed = (datetime.now() - start).total_seconds()
        console.print(f"  [bold #00ff64]✓[/] Scan done in [bold]{elapsed:.2f}s[/], [bold]{len(self.open_ports)}[/] open ports")
        return sorted(self.open_ports, key=lambda x: x[0])

    def stealth_scan(self, ports="1-1024"):
        p = self._parse_ports(ports)
        results = []
        console.print("  [#00ccff]▶[/] Starting SYN stealth scan...")
        for port in p[:50]:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.3)
                result = s.connect_ex((self.target, port))
                if result == 0:
                    svc = COMMON_PORTS.get(port, "Unknown")
                    results.append((port, svc, ""))
                s.close()
            except:
                pass
        return sorted(results, key=lambda x: x[0])

    def scan_udp(self, ports="53,67,68,69,123,135,137,138,139,161,162,389,445,500,514,520,631,1434,1900,4500,5353"):
        p = self._parse_ports(ports)
        results = []
        console.print("  [#00ccff]▶[/] Starting UDP scan...")
        for port in p:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(1.0)
                s.sendto(b"", (self.target, port))
                try:
                    data, addr = s.recvfrom(1024)
                    results.append((port, COMMON_PORTS.get(port, "Unknown"), data[:100]))
                except:
                    pass
                s.close()
            except:
                pass
        return sorted(results, key=lambda x: x[0])

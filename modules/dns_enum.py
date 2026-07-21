import socket
import dns.resolver
import dns.zone
import concurrent.futures
from .rhud import console

COMMON_SUBDOMAINS = [
    "www", "mail", "ftp", "admin", "api", "blog", "dev", "test",
    "staging", "app", "cdn", "static", "assets", "img", "css",
    "js", "docs", "wiki", "forum", "support", "help", "status",
    "portal", "login", "register", "shop", "store", "webmail",
    "remote", "vpn", "proxy", "ns1", "ns2", "mx", "smtp",
    "pop3", "imap", "web", "demo", "beta", "alpha", "release",
    "jenkins", "gitlab", "jira", "confluence", "nexus", "artifactory",
    "grafana", "prometheus", "kibana", "elastic", "sonar",
    "swagger", "api-docs", "graphql", "adminer", "phpmyadmin",
    "cpanel", "whm", "plesk", "webmin", "roundcube",
    "sso", "oauth", "auth", "identity", "accounts",
    "cloud", "console", "monitor", "analytics", "tracking",
    "backup", "db", "database", "mysql", "mongo", "redis",
    "mq", "queue", "rabbitmq", "kafka", "zookeeper",
    "intranet", "internal", "corp", "office", "hr",
    "pay", "payment", "checkout", "cart", "billing",
    "dashboard", "report", "logs", "logging", "splunk",
    "docker", "k8s", "kubernetes", "swarm", "traefik",
    "websocket", "socket", "chat", "live", "stream",
    "newsletter", "events", "calendar", "upload", "download",
    "video", "audio", "media", "files", "storage"
]

COMMON_DNS_RECORDS = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME", "SRV", "CAA"]

class DNSEnum:
    def __init__(self, domain, wordlist=None, threads=50):
        self.domain = domain.lower()
        self.wordlist = wordlist or COMMON_SUBDOMAINS
        self.threads = threads
        self.resolver = dns.resolver.Resolver()
        self.resolver.timeout = 2
        self.resolver.lifetime = 2

    def resolve_a(self, subdomain):
        target = f"{subdomain}.{self.domain}" if subdomain else self.domain
        try:
            answers = self.resolver.resolve(target, "A", raise_on_no_answer=False)
            return [str(r) for r in answers]
        except:
            return []

    def brute_subdomains(self):
        found = []
        console.print(f"  [#00ccff]▶[/] Brute-forcing [bold]{len(self.wordlist)}[/] subdomains on [bold]{self.domain}[/]")
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            fut_to_sub = {executor.submit(self.resolve_a, sub): sub for sub in self.wordlist}
            for future in concurrent.futures.as_completed(fut_to_sub):
                sub = fut_to_sub[future]
                try:
                    ips = future.result()
                    if ips:
                        found.append((f"{sub}.{self.domain}", ips))
                        console.print(f"    [bold #00ff64]+[/] [#00ff64]{sub}.{self.domain} -> {', '.join(ips)}[/]")
                except:
                    pass
        result = self.resolve_a("")
        if result:
            found.insert(0, (self.domain, result))
        return found

    def get_records(self, record_type="A"):
        results = []
        try:
            answers = self.resolver.resolve(self.domain, record_type)
            for r in answers:
                results.append(str(r))
        except dns.resolver.NoAnswer:
            pass
        except dns.resolver.NXDOMAIN:
            console.print(f"  [bold #ff3c3c]✗[/] [#ff3c3c]{self.domain} does not exist[/]")
        except Exception as e:
            console.print(f"  [bold #ff3c3c]✗[/] Error: {e}")
        return results

    def enumerate_all(self):
        data = {}
        console.print(f"  [#00ccff]▶[/] Enumerating DNS records for [bold]{self.domain}[/]")
        for rtype in COMMON_DNS_RECORDS:
            records = self.get_records(rtype)
            if records:
                data[rtype] = records
                for r in records:
                    console.print(f"    [bold #00ff64]+[/] [#00ff64]{rtype}: {r}[/]")
        return data

    def zone_transfer(self):
        console.print(f"  [#00ccff]▶[/] Attempting DNS zone transfer on [bold]{self.domain}[/]")
        try:
            ns_records = self.get_records("NS")
            for ns in ns_records:
                try:
                    zone = dns.zone.from_xfr(dns.query.xfr(ns, self.domain, timeout=5))
                    if zone:
                        console.print(f"    [bold #00ff64]+[/] [#00ff64]Zone transfer successful from {ns}![/]")
                        for n in zone.nodes.keys():
                            console.print(f"      {str(n)}.{self.domain}")
                        return zone
                except Exception as e:
                    console.print(f"    [bold #ff3c3c]✗[/] Transfer failed from {ns}: {e}")
        except Exception as e:
            console.print(f"  [bold #ff3c3c]✗[/] Error: {e}")
        return None

    def wildcard_check(self):
        import random, string
        random_sub = ''.join(random.choices(string.ascii_lowercase, k=12))
        try:
            answers = self.resolver.resolve(f"{random_sub}.{self.domain}", "A")
            if answers:
                console.print(f"  [bold #ffc800]![/] [#ffc800]Wildcard DNS! {random_sub}.{self.domain} -> {answers[0]}[/]")
                return True
        except:
            console.print("  [#00ccff]▶[/] No wildcard DNS detected")
        return False

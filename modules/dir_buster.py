import requests
import concurrent.futures
from urllib.parse import urljoin
from .rhud import console

COMMON_DIRS = [
    "admin", "wp-admin", "wp-content", "wp-includes", "administrator",
    "login", "backup", "backups", "db", "database", "config",
    "config.php", "config.php.bak", "config.php.old", ".env",
    "env", ".git/", ".svn/", ".htaccess", ".htpasswd",
    "index.php", "index.html", "default.aspx", "web.config",
    "robots.txt", "sitemap.xml", "crossdomain.xml",
    "phpinfo.php", "info.php", "test.php", "debug.php",
    "api", "v1", "v2", "docs", "swagger", "api-docs",
    "server-status", "server-info", "status",
    "cgi-bin/", "cgi", "cgi-bin/php",
    "assets", "static", "uploads", "files", "download",
    "tmp", "temp", "logs", "error_log", "access_log",
    "phpmyadmin", "pma", "sql", "sqladmin",
    "manager", "management", "console", "panel",
    "shell", "cmd", "exec", "command",
    "xmlrpc.php", "wp-login.php", "wp-json",
    "test", "tests", "testing", "demo",
    "src", "source", "app", "application",
    "old", "new", "dev", "beta", "staging",
    "graphql", "graphiql", "voyager",
    "jenkins", "jira", "confluence",
    "api/v1", "api/v2", "api/v3",
    "rest", "soap", "actuator",
    "swagger-ui.html", "swagger-ui",
    "dashboard", "monitor", "health", "healthcheck",
    "metrics", "prometheus", "grafana",
]

COMMON_EXTENSIONS = ["", ".php", ".asp", ".aspx", ".jsp", ".do", ".action", ".html", ".htm", ".txt", ".json", ".xml", ".bak", ".old", ".save", ".swp"]

class DirBuster:
    def __init__(self, base_url, wordlist=None, extensions=None, threads=30, timeout=5):
        self.base_url = base_url.rstrip("/")
        self.wordlist = wordlist or COMMON_DIRS
        self.extensions = extensions or COMMON_EXTENSIONS
        self.threads = threads
        self.timeout = timeout
        self.found = []
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })

    def _check_path(self, path):
        url = urljoin(self.base_url + "/", path)
        try:
            r = self.session.get(url, timeout=self.timeout, allow_redirects=False)
            if r.status_code in [200, 201, 204]:
                return (url, r.status_code, len(r.content), r.headers.get("Content-Type", ""))
            elif r.status_code in [301, 302, 303, 307, 308]:
                return (url, r.status_code, 0, f"Redirect: {r.headers.get('Location', '')}")
            elif r.status_code in [401, 403]:
                return (url, r.status_code, 0, r.headers.get("WWW-Authenticate", ""))
        except:
            pass
        return None

    def bust(self):
        total = len(self.wordlist) * len(self.extensions)
        console.print(f"  [#00ccff]▶[/] Busting [bold]{self.base_url}[/] with [bold]{total}[/] paths")

        variants = [w + e for w in self.wordlist for e in self.extensions]
        self.found = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            fut_to_path = {executor.submit(self._check_path, v): v for v in variants}
            for future in concurrent.futures.as_completed(fut_to_path):
                result = future.result()
                if result:
                    self.found.append(result)
                    url, status, size, extra = result
                    if status in [200, 201, 204]:
                        console.print(f"    [bold #00ff64]+[/] {url} [[bold]{status}[/]] ({size}b)")
                    elif status in [301, 302]:
                        console.print(f"    [bold #00ff64]+[/] {url} [[bold]{status}[/]] -> {extra}")
                    elif status in [401, 403]:
                        console.print(f"    [bold #ffc800]![/] {url} [[bold]{status}[/]]")

        console.print(f"  [bold #00ff64]✓[/] Found [bold]{len(self.found)}[/] interesting paths")
        return sorted(self.found, key=lambda x: x[1])

    def check_common_files(self):
        common = ["robots.txt", "sitemap.xml", "crossdomain.xml", ".htaccess", ".env", "phpinfo.php", "info.php"]
        results = []
        for f in common:
            r = self._check_path(f)
            if r:
                results.append(r)
                console.print(f"    [bold #00ff64]+[/] {r[0]} [[bold]{r[1]}[/]]")
        return results

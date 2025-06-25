import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import socket
import argparse
import threading
import queue
import time
import csv
import urllib.robotparser

def scan_ports(ip, ports, timeout=1.0):
    open_ports = []
    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                open_ports.append(port)
        except:
            continue
    return open_ports

class Crawler:
    def __init__(self, start_url, keyword, max_pages=20, num_threads=5, enable_portscan=False, ports_to_scan=None):
        self.start_url = start_url
        self.keyword = keyword.lower()
        self.max_pages = max_pages
        self.num_threads = num_threads
        self.enable_portscan = enable_portscan
        self.ports_to_scan = ports_to_scan if ports_to_scan else []
        self.visited = set()
        self.to_visit = queue.Queue()
        self.to_visit.put(start_url)
        self.lock = threading.Lock()
        self.results = []
        self.rp_cache = {}

    def get_ip(self, url):
        try:
            return socket.gethostbyname(urlparse(url).hostname)
        except:
            return "Unresolvable"

    def obey_robots(self, url):
        domain = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        if domain in self.rp_cache:
            rp = self.rp_cache[domain]
        else:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(urljoin(domain, "/robots.txt"))
            try:
                rp.read()
            except:
                rp = None
            self.rp_cache[domain] = rp
        return rp and rp.can_fetch("*", url)

    def crawl_page(self):
        while len(self.visited) < self.max_pages and not self.to_visit.empty():
            url = self.to_visit.get()
            with self.lock:
                if url in self.visited:
                    continue
                self.visited.add(url)

            if not self.obey_robots(url):
                continue

            try:
                response = requests.get(url, timeout=6)
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text().lower()
                fulltext = ' '.join(text.split())
            except:
                continue

            if self.keyword in text:
                title = soup.title.string.strip() if soup.title else "No Title"
                ip = self.get_ip(url)
                if self.enable_portscan and ip not in ("Unresolvable", "Nicht auflösbar"):
                    open_ports = scan_ports(ip, self.ports_to_scan)
                    ports_str = ", ".join(str(p) for p in open_ports) if open_ports else "None"
                else:
                    ports_str = "Not Scanned"

                with self.lock:
                    self.results.append({
                        "title": title,
                        "url": url,
                        "ip": ip,
                        "keyword": self.keyword,
                        "fulltext": fulltext,
                        "open_ports": ports_str
                    })

            for tag in soup.find_all("a", href=True):
                next_url = urljoin(url, tag['href'])
                if next_url.startswith("http") and urlparse(next_url).netloc:
                    with self.lock:
                        if next_url not in self.visited:
                            self.to_visit.put(next_url)

    def run(self):
        threads = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.crawl_page)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        return self.results

def save_csv(results, filename="crawler_results.csv"):
    if not results:
        print("⚠️ Nothing to save.")
        return
    fieldnames = list(results[0].keys())
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(row)
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import socket
import threading
import queue
import time
import csv
import os

DOCUMENT_EXTENSIONS = [".pdf", ".txt", ".json", ".doc", ".docx", ".csv", ".xls", ".xlsx", ".ppt", ".pptx", ".html", ".htm"]

def scan_ports(ip, ports, timeout=1.0):
    open_ports = []
    for port in ports:
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                open_ports.append(port)
        except:
            continue
    return open_ports

def extract_filename_from_url(url):
    return os.path.basename(urlparse(url).path)

def fetch_text_from_file(url, filetype, timeout=5):
    try:
        r = requests.get(url, timeout=timeout)
        if filetype in [".txt", ".json"]:
            return r.text[:5000].strip()
    except:
        return ""
    return ""

class Crawler:
    def __init__(self, start_url, keyword, max_pages=20, num_threads=5,
                 enable_portscan=False, ports_to_scan=None):
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
        self.active_thread_objects = []
        self.active_threads = 0

    def get_ip(self, url):
        try:
            return socket.gethostbyname(urlparse(url).hostname)
        except:
            return "Unresolvable"

    def obey_robots(self, url):
        return True  # Ignoring robots.txt on purpose

    def crawl_page(self):
        with self.lock:
            self.active_threads += 1
        try:
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
                    ports_str = "Not Scanned"
                    if self.enable_portscan and ip != "Unresolvable":
                        open_ports = scan_ports(ip, self.ports_to_scan)
                        ports_str = ", ".join(str(p) for p in open_ports) if open_ports else "None"
                    preview = fulltext[:300] + "..." if len(fulltext) > 300 else fulltext
                    with self.lock:
                        self.results.append({
                            "title": title,
                            "url": url,
                            "ip": ip,
                            "keyword": self.keyword,
                            "fulltext": fulltext,
                            "open_ports": ports_str,
                            "file_url": "",
                            "file_name": "",
                            "file_type": "",
                            "matched_content": "",
                            "preview": preview
                        })

                for tag in soup.find_all("a", href=True):
                    href = tag["href"]
                    next_url = urljoin(url, href)
                    if next_url.startswith("http") and urlparse(next_url).netloc:
                        ext = os.path.splitext(urlparse(next_url).path)[1].lower()
                        if ext in DOCUMENT_EXTENSIONS:
                            filename = extract_filename_from_url(next_url)
                            filetext = fetch_text_from_file(next_url, ext)
                            if self.keyword in filetext.lower():
                                preview = filetext[:300] + "..." if len(filetext) > 300 else filetext
                                with self.lock:
                                    self.results.append({
                                        "title": "Linked File",
                                        "url": url,
                                        "ip": self.get_ip(url),
                                        "keyword": self.keyword,
                                        "fulltext": "",
                                        "open_ports": "",
                                        "file_url": next_url,
                                        "file_name": filename,
                                        "file_type": ext.lstrip("."),
                                        "matched_content": filetext[:1000],
                                        "preview": preview
                                    })
                        else:
                            with self.lock:
                                if next_url not in self.visited:
                                    self.to_visit.put(next_url)
        finally:
            with self.lock:
                self.active_threads -= 1

    def run(self):
        self.active_thread_objects = []
        for _ in range(self.num_threads):
            t = threading.Thread(target=self.crawl_page)
            t.start()
            self.active_thread_objects.append(t)
        for t in self.active_thread_objects:
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

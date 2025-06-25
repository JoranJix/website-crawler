# 🕷️ Multi-Site Web Crawler with Fulltext & Port Scanning

A powerful Python-based crawler that performs keyword discovery, fulltext extraction, and optional per-host port scanning — across multiple domains at once.

## 🚀 Features

- 🔍 **Multi-Site, Multi-Keyword Search**  
  Crawl multiple starting URLs and search for multiple terms in parallel.

- 🧠 **Fulltext Capture**  
  Stores all visible page text for later NLP or forensic analysis.

- 📊 **CSV Export**  
  All metadata — titles, URLs, IPs, keywords, fulltext, open ports — is exported to `.csv`.

- 🔌 **Optional Custom Port Scan**  
  Scan user-defined ports on matched IP addresses to discover open services.

- 🖥️ **GUI & CLI Interface**  
  - Use `crawler_gui.py` with a browser interface (Streamlit)  
  - Use `crawler_cli.py` for headless jobs or automation

- 🐳 **Docker & Portainer Ready**  
  Ships with a `Dockerfile` and `docker-compose.yml` — deployable to cloud, local or container orchestration platforms.




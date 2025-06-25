import streamlit as st
import pandas as pd
import time
from webcrawler import Crawler, save_csv
from datetime import datetime

st.set_page_config(page_title="Multi-Site Web Crawler", layout="wide")
st.title("🕷️ Web Crawler with Fulltext + Port Scanning")

# User input fields
start_urls_input = st.text_area("Start URLs (comma-separated)", "https://example.com, https://example.org")
keywords_input = st.text_input("Keywords (comma-separated)", "AI, privacy")

max_pages = st.slider("Maximum pages per site", 5, 1000, 200)
threads = st.slider("Number of threads per crawl", 1, 20, 5)

enable_scan = st.checkbox("🔌 Enable custom port scan")
port_input = st.text_input("Ports to scan (comma-separated)", "22,80,443,8080") if enable_scan else ""

# Session history
if "search_history" not in st.session_state:
    st.session_state.search_history = []

if st.button("Start Crawling"):
    urls = [u.strip() for u in start_urls_input.split(",") if u.strip()]
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    ports = [int(p.strip()) for p in port_input.split(",") if p.strip().isdigit()] if enable_scan else []

    all_results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crawl_{timestamp}.csv"

    with st.spinner("Crawling… please wait"):
        for url in urls:
            for keyword in keywords:
                st.write(f"🔍 Crawling **{url}** for keyword '**{keyword}**'...")
                crawler = Crawler(
                    url,
                    keyword,
                    max_pages=max_pages,
                    num_threads=threads,
                    enable_portscan=enable_scan,
                    ports_to_scan=ports
                )
                results = crawler.run()
                for r in results:
                    r["keyword"] = keyword
                    r["start_url"] = url
                all_results.extend(results)

        save_csv(all_results, filename)
        st.session_state.search_history.append({
            "timestamp": str(datetime.now()),
            "start_urls": urls,
            "keywords": keywords,
            "file": filename
        })

    if all_results:
        df = pd.DataFrame(all_results)
        st.success(f"✅ {len(all_results)} results found.")
        st.dataframe(df)
        with open(filename, "rb") as f:
            st.download_button("📥 Download CSV", f, file_name=filename, mime="text/csv")
    else:
        st.warning("No matches found.")

# Sidebar search history
st.sidebar.header("📁 Search History")
for entry in reversed(st.session_state.search_history[-5:]):
    st.sidebar.write(f"🕓 {entry['timestamp']}")
    st.sidebar.write("Start URLs:", ", ".join(entry['start_urls']))
    st.sidebar.write("Keywords:", ", ".join(entry['keywords']))
    st.sidebar.write(f"📎 File: `{entry['file']}`")
    st.sidebar.markdown("---")
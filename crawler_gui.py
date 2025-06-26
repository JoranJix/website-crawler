import streamlit as st
import pandas as pd
from datetime import datetime
from webcrawler import Crawler, save_csv
from urllib.parse import urlparse
import time
import altair as alt

# Session init
if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Page setup
st.set_page_config(page_title="Web Crawler Pro", layout="wide")
st.title("🕷️ Web Crawler with File Search, Port Scan, Previews & Analytics")

# Inputs
start_urls_input = st.text_area("🌍 Start URLs (comma-separated)", "https://example.com, https://example.org")
keywords_input = st.text_input("🔎 Keywords (comma-separated)", "AI, privacy")
max_pages = st.slider("📄 Max pages per site", 5, 100, 20)
threads = st.slider("🧵 Threads per crawl", 1, 20, 5)

enable_scan = st.checkbox("🔌 Enable custom port scan")
port_input = st.text_input("Ports to scan (comma-separated)", "22,80,443") if enable_scan else ""

show_only_files = st.checkbox("📄 Show only file matches", value=False)
show_chart = st.checkbox("📊 Show keyword match chart", value=True)
show_domains = st.checkbox("🌐 Show domain stats", value=True)

start = st.button("🚀 Start Crawling")
log_display = st.empty()
thread_display = st.empty()
progress_display = st.empty()

if start:
    urls = [u.strip() for u in start_urls_input.split(",") if u.strip()]
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    ports = [int(p.strip()) for p in port_input.split(",") if p.strip().isdigit()] if enable_scan else []

    all_results = []
    total_jobs = len(urls) * len(keywords)
    job_index = 0
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"crawl_{timestamp}.csv"

    with st.spinner("Crawling in progress…"):
        for url in urls:
            for keyword in keywords:
                log_display.markdown(f"🔍 Crawling **{url}** for '**{keyword}**'...")
                crawler = Crawler(
                    start_url=url,
                    keyword=keyword,
                    max_pages=max_pages,
                    num_threads=threads,
                    enable_portscan=enable_scan,
                    ports_to_scan=ports
                )

                thread_display.markdown(f"🧵 Threads active: `{threads}`")
                progress_display.progress(0.0, text=f"Scanning {url}…")

                results = crawler.run()
                while any(t.is_alive() for t in crawler.active_thread_objects):
                    time.sleep(0.2)
                    ratio = min(len(crawler.visited) / max_pages, 1.0)
                    progress_display.progress(ratio, text=f"{int(ratio*100)}% of max pages for {url}")
                    thread_display.markdown(f"🧵 Threads active: `{crawler.active_threads}`")

                thread_display.markdown("🧵 Threads active: `0`")
                progress_display.progress(1.0, text="Done")

                for r in results:
                    r["keyword"] = keyword
                    r["start_url"] = url
                all_results.extend(results)

                job_index += 1
                progress_display.progress(job_index / total_jobs, text=f"Progress: {job_index}/{total_jobs}")

    if all_results:
        save_csv(all_results, filename)
        st.session_state.search_history.append({
            "timestamp": str(datetime.now()),
            "start_urls": urls,
            "keywords": keywords,
            "file": filename
        })

        df = pd.DataFrame(all_results)
        df["match_type"] = df["file_type"].apply(lambda x: "📄 File" if x else "🌐 Page")
        df["domain"] = df["url"].apply(lambda x: urlparse(x).netloc)

        if show_only_files:
            df = df[df["file_url"] != ""]

        st.success(f"✅ {len(df)} results found.")
        st.dataframe(df[["match_type", "title", "keyword", "domain", "url", "file_url", "file_type", "preview"]])

        with open(filename, "rb") as f:
            st.download_button("📥 Download CSV", f, file_name=filename, mime="text/csv")

        if show_chart and not df.empty:
            freq_df = df["keyword"].value_counts().reset_index()
            freq_df.columns = ["keyword", "matches"]
            st.subheader("📊 Keyword Match Frequency")
            chart = alt.Chart(freq_df).mark_bar().encode(
                x=alt.X("keyword", sort="-y"),
                y="matches",
                tooltip=["keyword", "matches"]
            ).properties(height=250)
            st.altair_chart(chart, use_container_width=True)

        if show_domains and not df.empty:
            dom_df = df["domain"].value_counts().reset_index()
            dom_df.columns = ["domain", "hits"]
            st.subheader("🌐 Domains with Most Matches")
            st.dataframe(dom_df)

    else:
        st.warning("No matches found.")

# Sidebar: History
st.sidebar.header("📁 Search History")
for entry in reversed(st.session_state.search_history[-5:]):
    st.sidebar.write(f"🕓 {entry['timestamp']}")
    st.sidebar.write("Start URLs:", ", ".join(entry['start_urls']))
    st.sidebar.write("Keywords:", ", ".join(entry['keywords']))
    st.sidebar.write(f"📎 File: `{entry['file']}`")
    st.sidebar.markdown("---")

# Footer
st.markdown("""
<hr>
<div style='text-align: center; font-size: 0.9em;'>
  Built by <a href='https://github.com/JoranJix/website-crawler' target='_blank'>@JoranJix</a> · MIT Licensed
</div>
""", unsafe_allow_html=True)

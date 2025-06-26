from webcrawler import Crawler, save_csv
import argparse
import time
from datetime import datetime

def parse_comma_list(value):
    return [v.strip() for v in value.split(",") if v.strip()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Headless Web Crawler with Fulltext + Portscan")
    parser.add_argument("urls", help="Comma-separated list of start URLs")
    parser.add_argument("keywords", help="Comma-separated list of keywords")
    parser.add_argument("-n", "--pages", type=int, default=20, help="Max pages per site")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of threads")
    parser.add_argument("--portscan", action="store_true", help="Enable custom port scan")
    parser.add_argument("--ports", type=str, default="", help="Ports to scan (comma-separated)")
    parser.add_argument("-o", "--output", help="Output CSV filename (optional)")

    args = parser.parse_args()

    urls = parse_comma_list(args.urls)
    keywords = parse_comma_list(args.keywords)
    ports = [int(p) for p in parse_comma_list(args.ports)] if args.portscan else []

    all_results = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = args.output or f"crawl_{timestamp}.csv"

    for url in urls:
        for keyword in keywords:
            print(f"\n🌐 Crawling '{url}' for keyword: '{keyword}'")
            crawler = Crawler(
                start_url=url,
                keyword=keyword,
                max_pages=args.pages,
                num_threads=args.threads,
                enable_portscan=args.portscan,
                ports_to_scan=ports
            )
            results = crawler.run()
            for r in results:
                r["keyword"] = keyword
                r["start_url"] = url
            all_results.extend(results)

    if all_results:
        save_csv(all_results, output)
        print(f"\n✅ Done: {len(all_results)} results saved to '{output}'")
    else:
        print("❌ No matches found.")

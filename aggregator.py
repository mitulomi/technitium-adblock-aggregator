import re
import logging
import requests
import idna
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Set, List, Tuple, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --- Konfiguration ---
SOURCES_FILE = "sources.txt"
WHITELIST_FILE = "whitelist.txt"
OUTPUT_FILE = "blocklist.txt"  # Technitium liest diese Datei
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) TechnitiumAggregator/1.0'
}
DOMAIN_REGEX = re.compile(
    r'^(?!-)[a-z0-9-\w]{1,63}(?:\.[a-z0-9-\w]{1,63})+(?<!-)$',
    re.IGNORECASE
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_session():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retry))
    session.mount('https://', HTTPAdapter(max_retries=retry))
    return session

def fetch_url(url: str) -> Optional[str]:
    session = get_session()
    try:
        r = session.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        return r.text
    except Exception as e:
        logger.error(f"Fehler bei {url}: {e}")
    return None

def process_line(line: str, whitelist: Set[str]) -> Optional[str]:
    line = line.split('#')[0].split('!')[0].strip().lower()
    line = line.replace('||', '').replace('^', '').split('$')[0]
    parts = line.split()
    if not parts: return None
    domain = parts[-1]
    if is_valid_domain(domain, whitelist):
        return domain
    return None

def is_valid_domain(domain: str, whitelist: Set[str]) -> bool:
    if not domain or domain in whitelist: return False
    if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain): return False
    try:
        encoded_domain = idna.encode(domain).decode('ascii')
        return bool(DOMAIN_REGEX.match(encoded_domain))
    except: return False

def hole_und_bereinige(urls: List[str], whitelist: Set[str]) -> Tuple[Set[str], List[str]]:
    alle_domains = set()
    stats = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_url, url): url for url in urls}
        for future in as_completed(futures):
            url = futures[future]
            content = future.result()
            if content:
                count = 0
                for line in content.splitlines():
                    domain = process_line(line, whitelist)
                    if domain:
                        alle_domains.add(domain)
                        count += 1
                stats.append(f"✅ {url}: {count} Domains")
            else:
                stats.append(f"❌ {url}: Download fehlgeschlagen")
    return alle_domains, stats

def speichern(domains: Set[str], stats: List[str]):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Technitium Blocklist Aggregator\n# Update: {timestamp}\n")
        f.write(f"# Total Unique Domains: {len(domains)}\n\n")
        for domain in sorted(domains):
            f.write(f"{domain}\n")
    
    if "GITHUB_STEP_SUMMARY" in os.environ:
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as gss:
            gss.write(f"### 🛡️ DNS Blocklist Update ({timestamp})\n")
            gss.write(f"- **Gesamtanzahl Domains:** {len(domains)}\n")
            for s in stats: gss.write(f"  - {s}\n")

if __name__ == "__main__":
    try:
        with open(SOURCES_FILE, 'r') as f:
            urls = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        with open(WHITELIST_FILE, 'r') as f:
            whitelist = {l.strip().lower() for l in f if l.strip() and not l.startswith("#")}
        domains, stats = hole_und_bereinige(urls, whitelist)
        speichern(domains, stats)
    except Exception as e:
        logger.error(f"Main Error: {e}")

# --- Konfiguration ---
OUTPUT_FILE = "blocklist.txt"

# In der Funktion speichern():
def speichern(domains, whitelist_count, stats):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(f"# Technitium Blocklist Aggregator\n# Updated: {timestamp}\n")
        f.write(f"# Total Domains: {len(domains)}\n")
        for domain in sorted(domains):
            f.write(f"{domain}\n")

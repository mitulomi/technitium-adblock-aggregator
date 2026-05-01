Technitium AdBlock Aggregator
Ein automatisierter Python-Aggregator zur Konsolidierung, Bereinigung und Optimierung mehrerer DNS-Blocklisten für den Technitium DNS Server.

Features
Automatisierte Aktualisierung: GitHub Actions führt das Skript täglich um 04:00 Uhr UTC aus.
Validierung: Entfernt Duplikate und ungültige Domain-Syntax mittels Regex und IDNA-Prüfung.
Ressourcenschonend: Reduziert die Systemlast auf dem DNS-Server (z. B. Orange Pi Zero 3), da nur eine einzige, bereinigte Datei verarbeitet werden muss.
Zentralisiertes Whitelisting: Abgleich gegen eine lokale Liste, um False Positives für kritische Infrastruktur zu vermeiden.

Installation in Technitium
Navigieren Sie im Technitium Dashboard zu Settings -> Blocking.
Klicken Sie auf Add Block List.
Kopieren Sie die Raw-URL der Datei blocklist.txt aus diesem Repository und fügen Sie diese ein.
Stellen Sie sicher, dass unter Settings -> DNS Server die Option Enable Blocking aktiviert ist.

Projektstruktur
aggregator.py: Das Python-Skript zur Datenverarbeitung.
sources.txt: Liste der Quell-URLs (z. B. Hagezi, URLHaus, PhishTank).
whitelist.txt: Liste von Domains, die explizit vom Blocking ausgeschlossen sind.
blocklist.txt: Die final generierte und optimierte Blockliste.

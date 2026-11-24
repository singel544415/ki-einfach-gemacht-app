# KI Einfach Gemacht – öffentliche App-Informationen

Statische, lokal prüfbare Informationswebsite für die Desktop-/Creator-Anwendung „KI Einfach Gemacht“ und deren TikTok-Content-Posting-API-Integration.

## Seiten

- Startseite und Produktablauf: `index.html`
- Datenschutz: `privacy.html`
- Nutzungsbedingungen: `terms.html`
- Support und Datenlöschung: `support.html`

Die Website enthält keine Zugangsdaten, Tokens oder privaten Videoinhalte und benötigt weder JavaScript noch externe CDN-Ressourcen.

## Lokale Prüfung

```bash
python3 tests/verify_site.py
python3 -m http.server 8000
```

Danach kann die Website unter `http://127.0.0.1:8000/` lokal geprüft werden.

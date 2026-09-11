# Opgavegenerator

Dansk matematik-opgavegenerator med den moderne GUI både lokalt og som en komplet browser-app.

## Online

Åbn [Opgavegeneratoren på GitHub Pages](https://augustolrik.github.io/opgaver_genrator/). Den online version kører direkte i browseren, har alle opgavetyper, forhåndsvisning og laver PDF-filer til download uden en server.

## Lokal version

Den komplette generator med alle opgavetyper kører lokalt:

```text
start_modern_html_gui.bat
```

Den lokale version kræver Python-pakkerne, som allerede bruges af projektet, blandt andet ReportLab og PyMuPDF.

Den online version ligger i [`docs/index.html`](docs/index.html) og bruger jsPDF fra jsDelivr til at lave PDF-filer i browseren. Den lokale Python-version er fortsat den autoritative version til den oprindelige ReportLab-layoutmotor.

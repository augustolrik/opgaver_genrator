# Project Status: opgaver_genrator

Last reviewed: 2026-09-11

## Purpose

Danish worksheet generator with a modern HTML GUI, PDF generation, shared metadata, and legacy/test material separated into folders.

## Current State

- Multiplication levels now generate one-digit × one-digit (easy), one-digit × two-digit (medium), and two-digit × two-digit (hard) problems; the modern GUI preview cache is versioned so old generated previews are not reused.
- Git: a complete browser port is prepared for GitHub Pages; pre-existing generated-PDF changes remain uncommitted in the working tree.
- GitHub repository is public. `docs/index.html` mirrors the modern GUI and runs the generator, preview, and PDF download entirely in the browser.
- Remote: `https://github.com/augustolrik/opgaver_genrator.git`.
- GitHub Pages is the intended host; no Render deployment is required.
- Active root files: `modern_html_app.py`, `shared_app_metadata.py`, `unikke_opgaver_set_up.py`, `start_modern_html_gui.bat`.
- Supporting folders: `legacy_gui/`, `old_code/`, `posters/`, `random_opgaver_pdf/`, `test_pdfs/`, `dr_transcripts/`.
- Prior context: live first-page preview and repo cleanup were already implemented in this checkout.

## Verification

- Verified the multiplication generators with repeated samples, Python compilation, the modern GUI preview path, a hosted-mode PDF smoke test, and the browser port's normal/test PDF downloads on 2026-09-11.

## Next Useful Step

Push the browser port, enable GitHub Pages from `/docs`, and verify the public URL.

## Maintenance Rule

When this project changes, update this file before finishing the chat. Include what changed, how to run or verify it, and any blockers.

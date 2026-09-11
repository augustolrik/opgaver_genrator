# Project Status: opgaver_genrator

Last reviewed: 2026-09-11

## Purpose

Danish worksheet generator with a modern HTML GUI, PDF generation, shared metadata, and legacy/test material separated into folders.

## Current State

- Multiplication levels now generate one-digit × one-digit (easy), one-digit × two-digit (medium), and two-digit × two-digit (hard) problems; the modern GUI preview cache is versioned so old generated previews are not reused.
- Git: the complete modern GUI is prepared for a Python/Docker web deployment; pre-existing generated-PDF changes remain uncommitted in the working tree.
- GitHub repository is public. The partial Pages prototype was taken offline; GitHub Pages is intentionally disabled until the complete modern GUI can be hosted without losing functionality.
- Remote: `https://github.com/augustolrik/opgaver_genrator.git`.
- Render deployment files are present: `Dockerfile`, `requirements.txt`, `.dockerignore`, and `render.yaml`; the app accepts Render's `PORT` and runs without opening a local browser.
- Active root files: `modern_html_app.py`, `shared_app_metadata.py`, `unikke_opgaver_set_up.py`, `start_modern_html_gui.bat`.
- Supporting folders: `legacy_gui/`, `old_code/`, `posters/`, `random_opgaver_pdf/`, `test_pdfs/`, `dr_transcripts/`.
- Prior context: live first-page preview and repo cleanup were already implemented in this checkout.

## Verification

- Verified the multiplication generators with repeated samples, Python compilation, the modern GUI preview path, and a hosted-mode PDF smoke test on 2026-09-11.

## Next Useful Step

Commit and push the deployment-ready modern GUI, then create and verify the free Render web service.

## Maintenance Rule

When this project changes, update this file before finishing the chat. Include what changed, how to run or verify it, and any blockers.

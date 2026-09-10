# Project Status: opgaver_genrator

Last reviewed: 2026-09-10

## Purpose

Danish worksheet generator with a modern HTML GUI, PDF generation, shared metadata, and legacy/test material separated into folders.

## Current State

- Multiplication levels now generate one-digit × one-digit (easy), one-digit × two-digit (medium), and two-digit × two-digit (hard) problems; the modern GUI preview cache is versioned so old generated previews are not reused.
- Git: `main...origin/main`; the online Pages version is committed and pushed as `e879595`, alongside pre-existing generated-PDF changes in the working tree.
- GitHub Pages activation is blocked because this private repository's current GitHub plan does not support Pages for private repositories.
- Remote: `https://github.com/augustolrik/opgaver_genrator.git`.
- Latest known commit before this file: `8993c74` - `Clean repo layout and add HTML preview` from 2026-07-03.
- Active root files: `modern_html_app.py`, `shared_app_metadata.py`, `unikke_opgaver_set_up.py`, `start_modern_html_gui.bat`.
- Supporting folders: `legacy_gui/`, `old_code/`, `posters/`, `random_opgaver_pdf/`, `test_pdfs/`, `dr_transcripts/`.
- Prior context: live first-page preview and repo cleanup were already implemented in this checkout.

## Verification

- Verified the multiplication generators with repeated samples, Python compilation, and the modern GUI preview path on 2026-09-10.

## Next Useful Step

Make the repository public or use a GitHub plan that supports Pages for private repositories, then enable the existing Pages workflow.

## Maintenance Rule

When this project changes, update this file before finishing the chat. Include what changed, how to run or verify it, and any blockers.

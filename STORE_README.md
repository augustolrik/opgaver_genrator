# Random Opgaver Store Version

Start the desktop app during development:

```powershell
cd C:\Python\opgaver_genrator
python store_app.py
```

Or double-click:

```text
start_store_app.bat
```

Modern HTML GUI for user testing:

```powershell
cd C:\Python\opgaver_genrator
python modern_html_app.py
```

Or double-click:

```text
start_modern_html_gui.bat
```

The app supports Danish and English UI from the language selector in the top right. It generates PDFs using the same assignment registry as `unikke_opgaver_set_up.py`, so new assignment types appear in the app when they are added to `BOKS_SKABELONER`.

Build an EXE before MSIX packaging:

```powershell
cd C:\Python\opgaver_genrator
pip install pyinstaller
pyinstaller RandomOpgaver.spec
```

The packaged app will be in:

```text
C:\Python\opgaver_genrator\dist\RandomOpgaver
```

Use that folder as the source for your MSIX packaging tool on the other device.

# Python Final Review

An offline-friendly Python final review site with practice questions, visual study cards, local assets, and a bundled Pyodide runtime for in-browser Python execution.

## Features

- Static review page in `index.html`
- Local Pyodide runtime under `pyodide/`
- Practice and explanation data under `data/`
- Image assets under `assets/`
- Build helper script: `build_review_page.py`

## Run Locally

Use the included Windows launcher:

```bat
启动本地服务器.bat
```

Then open:

```text
http://localhost:8000/index.html
```

You can also start the server manually from this directory:

```powershell
py -m http.server 8000
```

## Open Source Notes

This public source release excludes PDFs, generated release packages, Python bytecode caches, and temporary debug scripts. If you need reference documents while studying, keep them locally instead of committing them to the public repository.

## License

MIT

#!/usr/bin/env python3
"""Inyecta chatbot.js en todas las páginas HTML del sitio."""
import glob, os, re

REPO = r"C:\Users\artur\certificadoya"
SCRIPT_TAG = '<script src="/js/chatbot.js" defer></script>'
counter = 0

# HTML files in root
html_files = glob.glob(os.path.join(REPO, "*.html"))

# HTML files in subdirs (landings)
html_files += glob.glob(os.path.join(REPO, "certificado-energetico-*", "index.html"))
html_files += glob.glob(os.path.join(REPO, "cee-*", "index.html"))
html_files += glob.glob(os.path.join(REPO, "blog", "*.html"))
html_files += glob.glob(os.path.join(REPO, "tecnicos", "**", "*.html"))
html_files += glob.glob(os.path.join(REPO, "legal", "*.html"))
html_files += glob.glob(os.path.join(REPO, "descargables", "*.html"))
html_files += glob.glob(os.path.join(REPO, "habla-con-nosotros.html"))

for fp in sorted(set(html_files)):
    try:
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        continue
    
    # Skip if already injected
    if 'chatbot.js' in content:
        continue
    
    # Inject before </body>
    new_content = content.replace("</body>", f"{SCRIPT_TAG}\n</body>", 1)
    if new_content == content:
        # Try with newline
        new_content = content.replace("</body>", f"\n{SCRIPT_TAG}\n</body>", 1)
    
    if new_content != content:
        with open(fp, "w", encoding="utf-8") as f:
            f.write(new_content)
        counter += 1
        print(f"✅ {os.path.relpath(fp, REPO)}")

print(f"\n📊 Total: {counter} páginas actualizadas")

#!/usr/bin/env python3
"""Añade article:published_time y article:modified_time a todos los artículos del blog."""

import re
import subprocess
from pathlib import Path

BLOG_DIR = Path("/home/arturo/certificadoya/blog")

# Mapa: archivo -> fecha de creación (de git log)
def get_article_dates():
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%ai", "--diff-filter=A", "--name-only"],
        capture_output=True, text=True, cwd=BLOG_DIR.parent
    )
    lines = result.stdout.strip().split("\n")
    
    # Parse git log: cada commit tiene fecha + archivos
    dates = {}
    current_date = None
    for line in lines:
        if not line.strip():
            continue
        if re.match(r'\d{4}-\d{2}-\d{2}', line):
            current_date = line.split()[0]
        elif line.endswith('.html') and 'blog/' in line:
            fname = line.strip()
            if fname not in dates:
                dates[fname] = current_date
    
    # Fallback: si algún archivo no tiene fecha de creación, usar la primera fecha del log
    created = subprocess.run(
        ["git", "log", "--follow", "--format=%ai", "HEAD"],
        capture_output=True, text=True, cwd=BLOG_DIR.parent
    )
    first_commit_date = created.stdout.strip().split("\n")[-1].split()[0] if created.stdout.strip() else "2026-05-20"
    
    for f in BLOG_DIR.glob("*.html"):
        if f.name == "index.html":
            continue
        key = f"blog/{f.name}"
        if key not in dates:
            # Usar la fecha del primer commit del archivo
            fc = subprocess.run(
                ["git", "log", "--follow", "--format=%ai", "--", str(f)],
                capture_output=True, text=True, cwd=BLOG_DIR.parent
            )
            lines2 = fc.stdout.strip().split("\n")
            if lines2 and lines2[0]:
                dates[key] = lines2[-1].split()[0]
            else:
                dates[key] = first_commit_date
    
    return dates

def add_timestamps_to_file(filepath, pub_date, mod_date):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Verificar si ya tiene article:published_time
    if 'article:published_time' in content:
        print(f"  ⏭️ Ya tiene timestamps: {filepath.name}")
        return False
    
    # Buscar <link rel="canonical" y añadir después
    pattern = r'(<link rel="canonical"[^>]+>)'
    replacement = (
        r'\1\n'
        f'  <meta property="article:published_time" content="{pub_date}T00:00:00+02:00">\n'
        f'  <meta property="article:modified_time" content="{mod_date}T00:00:00+02:00">'
    )
    
    new_content = re.sub(pattern, replacement, content, count=1)
    
    if new_content == content:
        print(f"  ⚠️ No se pudo insertar en: {filepath.name}")
        return False
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"  ✅ {filepath.name} → pub: {pub_date}, mod: {mod_date}")
    return True

def main():
    dates = get_article_dates()
    
    print(f"📝 Añadiendo article:published_time a {len(dates)} artículos...\n")
    
    count = 0
    for rel_path, pub_date in sorted(dates.items()):
        filepath = BLOG_DIR / Path(rel_path).name
        if not filepath.exists():
            print(f"  ❌ No existe: {filepath}")
            continue
        
        modified = add_timestamps_to_file(filepath, pub_date, pub_date)
        if modified:
            count += 1
    
    print(f"\n✅ Hecho. {count} artículos actualizados.")

if __name__ == "__main__":
    main()

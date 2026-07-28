#!/usr/bin/env python3
"""Script universal para ejecutar el script Oracle"""
import subprocess
import sys

# Ejecutar el script de Oracle
result = subprocess.run(
    [sys.executable, "debug_oracle.py"],
    capture_output=True,
    text=True,
    cwd=r"C:\Users\artur\certificadoya"
)

print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.return_code)

# Ahora ejecutar el script oficial
result2 = subprocess.run(
    [sys.executable, r"C:\Users\artur\certificadoya\scripts\oracle_create_multiregion.py"],
    capture_output=True,
    text=True
)

print("\n=== SCRIPT OFICIAL ===")
print("STDOUT:", result2.stdout)
print("STDERR:", result2.stderr)
print("Return code:", result2.returncode)
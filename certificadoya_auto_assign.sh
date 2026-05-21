#!/bin/bash
# CertificaYA — Auto-assign leads by postal code
# Runs auto_assign.py with the Hermes venv python
cd /opt/data/projects/certificadoya
/opt/hermes/.venv/bin/python3 auto_assign.py "$@"

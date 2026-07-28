#!/usr/bin/env bash
cd /c/Users/artur/certificadoya
export SUPABASE_SERVICE_KEY=$(grep SUPABASE_SERVICE_KEY .env 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'")
bash auto_assign.sh

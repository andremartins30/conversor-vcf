#!/bin/bash

# Script para manter aplicação web ativa
# Uso: ./keepalive.sh [URL]

# URL da aplicação (substitua pela URL real)
APP_URL="${1:-https://vcf-converter.up.railway.app}"

# Arquivo de log
LOG_FILE="$HOME/keepalive.log"

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Faz a requisição
echo "[$TIMESTAMP] Fazendo requisição para: $APP_URL" >> "$LOG_FILE"

# Usa curl para fazer a requisição
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$APP_URL")

if [ "$HTTP_CODE" = "200" ]; then
    echo "[$TIMESTAMP] ✅ App ativo - Status: $HTTP_CODE" >> "$LOG_FILE"
    echo "✅ App ativo"
elif [ "$HTTP_CODE" = "000" ]; then
    echo "[$TIMESTAMP] ❌ Falha na conexão - Timeout ou erro de rede" >> "$LOG_FILE"
    echo "❌ Falha na conexão"
else
    echo "[$TIMESTAMP] ⚠️  App respondeu com status: $HTTP_CODE" >> "$LOG_FILE"
    echo "⚠️  Status: $HTTP_CODE"
fi

#!/bin/bash

# Script avançado para keepalive com configuração
# Lê configurações do arquivo keepalive.config

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/keepalive.config"

# Carrega configurações se o arquivo existir
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    # Configurações padrão
    APP_URL="https://seu-app.ondigitalocean.app"
    LOG_FILE="$HOME/keepalive.log"
    TIMEOUT=30
fi

# Permite sobrescrever URL via parâmetro
if [ $# -gt 0 ]; then
    APP_URL="$1"
fi

# Timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Função para log
log_message() {
    echo "[$TIMESTAMP] $1" >> "$LOG_FILE"
    echo "$1"
}

# Verifica se curl está instalado
if ! command -v curl &> /dev/null; then
    log_message "❌ curl não está instalado. Instale com: sudo apt install curl"
    exit 1
fi

# Faz a requisição
log_message "🔗 Fazendo requisição para: $APP_URL"

# Usa curl para fazer a requisição
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$APP_URL" 2>/dev/null)

case "$HTTP_CODE" in
    "200")
        log_message "✅ App ativo - Status: $HTTP_CODE"
        exit 0
        ;;
    "000")
        log_message "❌ Falha na conexão - Timeout ou erro de rede"
        exit 1
        ;;
    "")
        log_message "❌ Erro ao executar curl"
        exit 1
        ;;
    *)
        log_message "⚠️  App respondeu com status: $HTTP_CODE"
        exit 1
        ;;
esac

#!/bin/bash

# Script para configurar o cron job para manter a aplicação ativa
# Executa a cada 5 minutos

echo "🔧 Configurando cron job para manter aplicação ativa..."

# Caminho para o script keepalive
SCRIPT_PATH="/home/andre/Área de Trabalho/conversor_vcf/webapp/keepalive.sh"

# URL da aplicação (SUBSTITUA PELA URL REAL DO SEU DEPLOY)
APP_URL="http://vcf-converter.up.railway.app"

echo "📝 Configurações:"
echo "   Script: $SCRIPT_PATH"
echo "   URL: $APP_URL"
echo ""

# Verifica se o script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "❌ Erro: Script não encontrado em $SCRIPT_PATH"
    exit 1
fi

# Torna o script executável
chmod +x "$SCRIPT_PATH"

# Cria entrada do cron
CRON_ENTRY="*/5 * * * * $SCRIPT_PATH $APP_URL >/dev/null 2>&1"

# Verifica se já existe uma entrada similar
if crontab -l 2>/dev/null | grep -q "keepalive.sh"; then
    echo "⚠️  Já existe uma entrada de keepalive no cron."
    echo "   Removendo entrada antiga..."
    crontab -l 2>/dev/null | grep -v "keepalive.sh" | crontab -
fi

# Adiciona nova entrada
echo "➕ Adicionando nova entrada no cron..."
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job configurado com sucesso!"
echo ""
echo "📋 Configuração atual:"
echo "   Frequência: A cada 5 minutos"
echo "   Comando: $CRON_ENTRY"
echo ""
echo "🔍 Para verificar se está funcionando:"
echo "   tail -f ~/keepalive.log"
echo ""
echo "🗑️  Para remover o cron job:"
echo "   crontab -l | grep -v 'keepalive.sh' | crontab -"
echo ""
echo "⚠️  IMPORTANTE: Substitua a URL pela URL real do seu deploy!"
echo "   Edite o arquivo setup_cron.sh e altere APP_URL"

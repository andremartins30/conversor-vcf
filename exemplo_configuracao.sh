#!/bin/bash

# Exemplo de configuração para a aplicação real
# COPIE ESTE ARQUIVO E ADAPTE PARA SUA URL

echo "🔧 Configurando Keep Alive para aplicação em produção"
echo ""

# SUBSTITUA ESTA URL PELA URL REAL DA SUA APLICAÇÃO!
APP_URL="http://vcf-converter.up.railway.app"

echo "🌐 URL da aplicação: $APP_URL"
echo ""

# Testa se a URL está acessível
echo "🔍 Testando conectividade..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$APP_URL" 2>/dev/null)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Aplicação acessível (Status: $HTTP_CODE)"
else
    echo "⚠️  Aplicação retornou status: $HTTP_CODE"
    echo "   Verifique se a URL está correta!"
fi

echo ""
echo "📝 Para configurar o cron job:"
echo "   1. Edite keepalive.config com a URL correta"
echo "   2. Execute: ./setup_cron.sh"
echo ""
echo "💡 Comando do cron que será criado:"
SCRIPT_PATH="/home/andre/Área de Trabalho/conversor_vcf/webapp/keepalive_advanced.sh"
echo "*/5 * * * * $SCRIPT_PATH $APP_URL >/dev/null 2>&1"
echo ""
echo "📊 Para monitorar:"
echo "   tail -f ~/keepalive.log"

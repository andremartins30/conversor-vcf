#!/bin/bash

echo "🛑 Parando sistema Keep Alive"
echo ""

# Backup do crontab atual
crontab -l > crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null
echo "💾 Backup do crontab criado"

# Remove linhas que contenham keepalive do crontab
crontab -l 2>/dev/null | grep -v "keepalive" | crontab -

echo "✅ Jobs de keep alive removidos do cron"
echo ""
echo "📋 Crontab atual:"
crontab -l 2>/dev/null || echo "   (vazio)"
echo ""
echo "🔍 Para restaurar, use um dos backups:"
ls -la crontab_backup_*.txt 2>/dev/null || echo "   (nenhum backup encontrado)"

# 🔄 Keep Alive - Evitar Sleep da Aplicação

Este diretório contém scripts para manter sua aplicação web ativa, evitando que entre em modo sleep.

## 📁 Arquivos

### Scripts Principais:
- **`keepalive.sh`** - Script simples com curl
- **`keepalive_advanced.sh`** - Script avançado com configurações
- **`keepalive.py`** - Script Python com requests
- **`setup_cron.sh`** - Configuração automática do cron job

### Configuração:
- **`keepalive.config`** - Arquivo de configuração
- **`KEEPALIVE.md`** - Este arquivo de documentação

## 🚀 Como usar

### 1. Configurar a URL da aplicação

Edite o arquivo `keepalive.config` e substitua a URL:

```bash
# Substitua pela URL real da sua aplicação
APP_URL="https://sua-app-real.ondigitalocean.app"
```

### 2. Configurar o cron job

Execute o script de configuração:

```bash
./setup_cron.sh
```

Ou configure manualmente:

```bash
# Abre o editor do cron
crontab -e

# Adiciona esta linha (substitua o caminho e URL):
*/5 * * * * /caminho/para/keepalive.sh https://sua-app.com >/dev/null 2>&1
```

### 3. Verificar se está funcionando

```bash
# Ver os logs em tempo real
tail -f ~/keepalive.log

# Ver últimas entradas
tail ~/keepalive.log

# Verificar cron jobs ativos
crontab -l
```

## ⚙️ Configurações

### Frequência das requisições

No cron job, altere `*/5` para o intervalo desejado:
- `*/5` = A cada 5 minutos
- `*/10` = A cada 10 minutos  
- `*/15` = A cada 15 minutos

### Timeout das requisições

No arquivo `keepalive.config`:
```bash
TIMEOUT=30  # 30 segundos
```

## 🧹 Manutenção

### Remover cron job:
```bash
crontab -l | grep -v 'keepalive' | crontab -
```

### Limpar logs:
```bash
> ~/keepalive.log  # Limpa o arquivo
# ou
rm ~/keepalive.log  # Remove o arquivo
```

### Testar manualmente:
```bash
./keepalive.sh https://sua-app.com
```

## 🔍 Monitoramento

### Status codes comuns:
- **200** ✅ - App funcionando
- **404** ⚠️  - Página não encontrada
- **500** ❌ - Erro interno do servidor
- **000** ❌ - Falha de conexão/timeout

### Logs são salvos em:
- `~/keepalive.log`

## 🚨 Troubleshooting

### Problema: "Permissão negada"
```bash
chmod +x keepalive.sh keepalive_advanced.sh setup_cron.sh
```

### Problema: "curl não encontrado"
```bash
sudo apt update && sudo apt install curl
```

### Problema: Cron não executa
```bash
# Verificar se o serviço cron está rodando
sudo systemctl status cron

# Iniciar se necessário
sudo systemctl start cron
```

### Problema: Logs não aparecem
- Verifique se o caminho do script no cron está correto
- Teste o script manualmente primeiro
- Verifique permissões do diretório home

## 📊 Exemplo de uso

```bash
# 1. Configurar
nano keepalive.config  # Editar URL

# 2. Instalar cron
./setup_cron.sh

# 3. Monitorar
tail -f ~/keepalive.log
```

## 💡 Dicas

1. **Use URLs HTTPS** sempre que possível
2. **Monitore os logs** regularmente  
3. **Ajuste a frequência** conforme necessário
4. **Teste primeiro** com a aplicação local
5. **Configure alertas** se a aplicação ficar offline por muito tempo

## 🌐 Plataformas compatíveis

Este sistema funciona com:
- ✅ DigitalOcean App Platform
- ✅ Heroku
- ✅ Render
- ✅ Railway
- ✅ Vercel
- ✅ Qualquer serviço que faça sleep por inatividade

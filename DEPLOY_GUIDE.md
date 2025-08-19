# 🚀 GUIA RÁPIDO DE IMPLANTAÇÃO

## Passos para configurar o Keep Alive após o deploy:

### 1. Obtenha a URL do seu app
Após fazer o deploy no DigitalOcean, você receberá uma URL como:
```
https://conversor-vcf-12345.ondigitalocean.app
```

### 2. Configure o keep alive
```bash
# Edite o arquivo de configuração
nano keepalive.config

# Substitua a URL pela URL real
URL="https://sua-url-real.ondigitalocean.app"
```

### 3. Teste a configuração
```bash
# Execute o teste
./exemplo_configuracao.sh
```

### 4. Ative o cron job
```bash
# Configure automaticamente
./setup_cron.sh

# OU configure manualmente:
crontab -e
# Adicione a linha:
# */5 * * * * /caminho/para/keepalive_advanced.sh https://sua-url.ondigitalocean.app >/dev/null 2>&1
```

### 5. Monitore o funcionamento
```bash
# Veja o log em tempo real
tail -f ~/keepalive.log

# Verifique se o cron está ativo
crontab -l
```

## 🔧 Solução de Problemas

### Se a aplicação ainda dorme:
1. Verifique se o cron está rodando: `ps aux | grep cron`
2. Verifique se o script tem permissão: `ls -la keepalive*`
3. Teste o script manualmente: `./keepalive.sh https://sua-url.app`

### Para parar o keep alive:
```bash
# Remove o cron job
crontab -e
# Delete a linha do keepalive

# OU use o script automático:
./stop_keepalive.sh
```

## 📊 Estatísticas

O sistema enviará uma requisição GET a cada 5 minutos:
- **24h**: 288 requisições
- **Semana**: 2.016 requisições  
- **Mês**: ~8.640 requisições

Isso manterá sua aplicação sempre ativa! ✅

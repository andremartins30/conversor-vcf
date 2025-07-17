# Conversor VCF para CSV/Excel

Uma aplicação web simples e elegante para converter arquivos de contatos VCF (vCard) para formatos CSV e Excel.

## 🚀 Características

- **Interface moderna e responsiva** com Bootstrap 5
- **Drag & Drop** para upload de arquivos
- **Conversão automática** para CSV e Excel
- **Download direto** dos arquivos convertidos
- **100% gratuito** e open source

## 🛠️ Tecnologias

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Processamento**: Pandas, Regex
- **Deploy**: Render, Heroku, Railway

## 📦 Instalação Local

1. **Clone o repositório**:
```bash
git clone <seu-repositorio>
cd webapp
```

2. **Crie um ambiente virtual**:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**:
```bash
python app.py
```

5. **Acesse**: http://localhost:5000

## 🌐 Deploy Gratuito

### 1. Render (Recomendado)

**Render** é uma plataforma moderna e gratuita:

1. **Crie uma conta**: [render.com](https://render.com)
2. **Conecte seu GitHub**: Autorize o Render a acessar seus repositórios
3. **Crie um novo Web Service**:
   - Escolha "Web Service"
   - Selecione seu repositório
   - Configurações:
     - **Environment**: Python 3
     - **Build Command**: `./build.sh`
     - **Start Command**: `gunicorn app:app`
     - **Instance Type**: Free
4. **Deploy automático**: O Render fará o deploy automaticamente

**Vantagens do Render**:
- ✅ SSL gratuito
- ✅ Deploy automático do GitHub
- ✅ 750 horas gratuitas por mês
- ✅ Não hiberna (melhor que Heroku)

### 2. Railway

**Railway** é outra excelente opção gratuita:

1. **Acesse**: [railway.app](https://railway.app)
2. **Login com GitHub**
3. **Deploy from GitHub**:
   - Selecione seu repositório
   - Configurações automáticas
   - Deploy instantâneo

**Vantagens do Railway**:
- ✅ $5 de crédito gratuito por mês
- ✅ Deploy mais rápido
- ✅ Interface mais simples

### 3. Heroku (com limitações)

**Heroku** ainda oferece plano gratuito limitado:

1. **Instale o Heroku CLI**
2. **Login**: `heroku login`
3. **Crie o app**: `heroku create seu-app-name`
4. **Deploy**:
```bash
git add .
git commit -m "Deploy inicial"
git push heroku main
```

**Limitações**:
- ⚠️ App hiberna após 30 min de inatividade
- ⚠️ 1000 horas gratuitas por mês

### 4. Vercel (Para SPAs)

Se quiser converter para uma SPA (Single Page Application):

1. **Acesse**: [vercel.com](https://vercel.com)
2. **Import from GitHub**
3. **Configure**:
   - Framework: Other
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `.`

## 📁 Estrutura do Projeto

```
webapp/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── Procfile              # Configuração Heroku
├── build.sh              # Script de build para Render
├── .gitignore            # Arquivos ignorados pelo Git
├── templates/
│   ├── upload.html       # Página de upload
│   └── resultado.html    # Página de resultado
├── static/               # Arquivos estáticos (CSS/JS)
├── uploads/              # Arquivos VCF temporários
└── downloads/            # Arquivos convertidos
```

## 🔧 Configuração de Produção

Para deploy em produção, considere:

1. **Variáveis de ambiente**:
```python
import os
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')
```

2. **Limpeza automática**:
```python
# Adicione um job para limpar arquivos antigos
import schedule
schedule.every(1).hours.do(limpar_arquivos_antigos)
```

3. **Limite de upload**:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

## 🎯 Passos para Publicar

### Opção 1: Render (Mais Fácil)

1. **Suba para GitHub**:
```bash
git init
git add .
git commit -m "Primeira versão"
git branch -M main
git remote add origin https://github.com/seu-usuario/conversor-vcf.git
git push -u origin main
```

2. **Deploy no Render**:
   - Acesse [render.com](https://render.com)
   - "New Web Service"
   - Conecte o repositório GitHub
   - Configurações automáticas
   - Deploy!

### Opção 2: Railway

1. **Mesmo processo do GitHub**
2. **Acesse [railway.app](https://railway.app)**
3. **"Deploy from GitHub"**
4. **Selecione o repositório**

## 🆘 Solução de Problemas

**Erro de módulos**: Verifique se `requirements.txt` está completo
**Erro de porta**: Use `PORT` do ambiente: `port=int(os.environ.get('PORT', 5000))`
**Arquivos não encontrados**: Verifique se as pastas `uploads` e `downloads` existem

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar!

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

---

**🎉 Agora você tem um conversor VCF profissional rodando na web gratuitamente!**

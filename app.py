from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
import re
import os
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vcf_converter_secret_key_2025')  # Para flash messages

# Configurações
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
ALLOWED_EXTENSIONS = {'vcf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extrair_contatos_vcf(arquivo_path):
    """Extrai contatos do arquivo VCF usando regex"""
    contatos = []
    
    try:
        with open(arquivo_path, "r", encoding="utf-8", errors='ignore') as f:
            conteudo = f.read()
        
        # Divide o arquivo em blocos de VCARD
        vcards = re.split(r'BEGIN:VCARD', conteudo)
        
        for vcard_text in vcards[1:]:  # Pula o primeiro elemento vazio
            if 'END:VCARD' not in vcard_text:
                continue
                
            # Extrai nome
            nome_match = re.search(r'FN:(.+)', vcard_text)
            nome = nome_match.group(1).strip() if nome_match else ''
            
            # Extrai telefones - busca apenas números válidos
            telefones = re.findall(r'TEL[^:]*:([+\d\-\s\(\)]+)', vcard_text)
            telefones_limpos = []
            
            for tel in telefones:
                tel_limpo = tel.strip()
                # Verifica se é um número válido (tem pelo menos 3 dígitos)
                if re.search(r'\d.*\d.*\d', tel_limpo):
                    telefones_limpos.append(tel_limpo)
            
            # Remove duplicatas mantendo a ordem
            telefones_unicos = []
            for tel in telefones_limpos:
                if tel not in telefones_unicos:
                    telefones_unicos.append(tel)
            
            if telefones_unicos:
                for telefone in telefones_unicos:
                    contatos.append({
                        'Nome': nome,
                        'Telefone': telefone
                    })
            else:
                contatos.append({
                    'Nome': nome,
                    'Telefone': ''
                })
        
        return contatos
    
    except Exception as e:
        raise Exception(f"Erro ao processar arquivo VCF: {str(e)}")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("POST request recebido")  # Debug
        
        # Verifica se foi enviado um arquivo
        if 'file' not in request.files:
            print("Nenhum campo 'file' encontrado no request")  # Debug
            flash('Nenhum arquivo foi selecionado')
            return redirect(request.url)
        
        file = request.files['file']
        print(f"Arquivo recebido: {file.filename}")  # Debug
        
        if file.filename == '':
            print("Nome do arquivo está vazio")  # Debug
            flash('Nenhum arquivo foi selecionado')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            print(f"Arquivo válido: {file.filename}")  # Debug
            # Salva o arquivo enviado
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"Arquivo salvo em: {filepath}")  # Debug
            
            try:
                # Processa o arquivo VCF
                contatos = extrair_contatos_vcf(filepath)
                print(f"Contatos extraídos: {len(contatos)}")  # Debug
                
                if not contatos:
                    flash('Nenhum contato foi encontrado no arquivo VCF')
                    return redirect(request.url)
                
                # Cria DataFrame
                df = pd.DataFrame(contatos)
                
                # Gera nomes dos arquivos de saída
                base_name = filename.rsplit('.', 1)[0]
                csv_filename = f"{base_name}.csv"
                xlsx_filename = f"{base_name}.xlsx"
                
                csv_path = os.path.join(app.config['DOWNLOAD_FOLDER'], csv_filename)
                xlsx_path = os.path.join(app.config['DOWNLOAD_FOLDER'], xlsx_filename)
                
                # Salva os arquivos
                df.to_csv(csv_path, index=False)
                df.to_excel(xlsx_path, index=False)
                print(f"Arquivos salvos: {csv_filename}, {xlsx_filename}")  # Debug
                
                # Remove o arquivo VCF original
                os.remove(filepath)
                
                # Mostra resultado
                return render_template('resultado.html', 
                                     csv_file=csv_filename, 
                                     xlsx_file=xlsx_filename,
                                     total_contatos=len(contatos))
                
            except Exception as e:
                print(f"Erro ao processar arquivo: {str(e)}")  # Debug
                flash(f'Erro ao processar arquivo: {str(e)}')
                if os.path.exists(filepath):
                    os.remove(filepath)
                return redirect(request.url)
        else:
            print(f"Arquivo não permitido: {file.filename}")  # Debug
            flash('Tipo de arquivo não permitido. Apenas arquivos .vcf são aceitos.')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/download/<filename>')
def download_file(filename):
    try:
        return send_file(os.path.join(app.config['DOWNLOAD_FOLDER'], filename), 
                        as_attachment=True)
    except Exception as e:
        flash(f'Erro ao baixar arquivo: {str(e)}')
        return redirect(url_for('upload_file'))

@app.route('/limpar')
def limpar_arquivos():
    """Remove arquivos antigos para economizar espaço"""
    try:
        for folder in [app.config['UPLOAD_FOLDER'], app.config['DOWNLOAD_FOLDER']]:
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        flash('Arquivos limpos com sucesso!')
    except Exception as e:
        flash(f'Erro ao limpar arquivos: {str(e)}')
    
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    # Cria as pastas se não existirem
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
    
    # Configuração para produção
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug, host='0.0.0.0', port=port)

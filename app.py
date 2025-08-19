from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import pandas as pd
import re
import os
import tempfile
from datetime import datetime
from werkzeug.utils import secure_filename
import zipfile

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'vcf_converter_secret_key_2025')  # Para flash messages

# Configurações
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'vcf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE  # 16MB max

# Cria diretório de upload se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extrair_contatos_manual(arquivo_vcf):
    """Extrai contatos usando regex"""
    contatos = []
    
    try:
        with open(arquivo_vcf, "r", encoding="utf-8", errors='ignore') as f:
            conteudo = f.read()
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")
        return contatos
    
    # Divide o arquivo em blocos de VCARD
    vcards = re.split(r'BEGIN:VCARD', conteudo)
    
    for vcard_text in vcards[1:]:  # Pula o primeiro elemento vazio
        if 'END:VCARD' not in vcard_text:
            continue
            
        # Extrai nome
        nome_match = re.search(r'FN:(.+)', vcard_text)
        nome = nome_match.group(1).strip() if nome_match else ''
        
        # Extrai telefones
        telefones = re.findall(r'TEL[^:]*:([+\d\-\s\(\)]+)', vcard_text)
        telefones_limpos = []
        
        for tel in telefones:
            tel_limpo = tel.strip()
            # Verifica se é um número válido
            if re.search(r'\d.*\d.*\d', tel_limpo):
                telefones_limpos.append(tel_limpo)
        
        # Remove duplicatas mantendo a ordem
        telefones_unicos = []
        for tel in telefones_limpos:
            if tel not in telefones_unicos:
                telefones_unicos.append(tel)
        
        # Filtra entradas que não são nomes válidos (evita telefones como nomes)
        if nome and not re.match(r'^[\d\+\-\s\(\)]+$', nome):
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

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template('upload.html')
    
    print("=== INÍCIO DO UPLOAD ===")
    print(f"Request method: {request.method}")
    print(f"Request files: {request.files}")
    print(f"Request form: {request.form}")
    
    if 'file' not in request.files:
        print("Erro: Nenhum arquivo na requisição")
        flash('Nenhum arquivo foi selecionado')
        return redirect(url_for('upload_file'))
    
    file = request.files['file']
    print(f"Arquivo recebido: {file.filename}")
    
    if file.filename == '':
        print("Erro: Nome do arquivo vazio")
        flash('Nenhum arquivo foi selecionado')
        return redirect(url_for('upload_file'))
    
    if file and allowed_file(file.filename):
        print("Arquivo válido, processando...")
        filename = secure_filename(file.filename)
        
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.vcf') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            # Processa o arquivo
            print(f"Extraindo contatos de: {temp_path}")
            contatos = extrair_contatos_manual(temp_path)
            print(f"Contatos extraídos: {len(contatos)}")
            
            if not contatos:
                flash('Nenhum contato foi encontrado no arquivo VCF')
                return redirect(url_for('upload_file'))
            
            # Cria DataFrame
            df = pd.DataFrame(contatos)
            
            # Gera arquivos de saída em diretório temporário
            with tempfile.TemporaryDirectory() as temp_dir:
                csv_path = os.path.join(temp_dir, 'contatos.csv')
                excel_path = os.path.join(temp_dir, 'contatos.xlsx')
                zip_path = os.path.join(temp_dir, 'contatos_convertidos.zip')
                
                # Salva arquivos
                df.to_csv(csv_path, index=False, encoding='utf-8')
                df.to_excel(excel_path, index=False)
                
                # Cria ZIP com ambos os arquivos
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    zipf.write(csv_path, 'contatos.csv')
                    zipf.write(excel_path, 'contatos.xlsx')
                
                # Copia o ZIP para um local permanente temporário
                final_zip_path = os.path.join(UPLOAD_FOLDER, f'resultado_{filename}.zip')
                import shutil
                shutil.copy2(zip_path, final_zip_path)
                
                return render_template('resultado.html', 
                                     num_contatos=len(contatos),
                                     download_file=f'resultado_{filename}.zip')
                
        except Exception as e:
            print(f"Erro ao processar arquivo: {e}")
            flash(f'Erro ao processar arquivo: {str(e)}')
            return redirect(url_for('upload_file'))
        finally:
            # Remove arquivo temporário
            try:
                os.unlink(temp_path)
            except:
                pass
    else:
        print("Arquivo inválido")
        flash('Tipo de arquivo não permitido. Use apenas arquivos .vcf')
        return redirect(url_for('upload_file'))

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f'Erro ao baixar arquivo: {str(e)}')
        return redirect(url_for('upload_file'))

# Configuração para produção
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

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
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'vcf', 'xlsx', 'xls', 'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE  # 16MB max

# Cria diretório de upload se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detectar_tipo_arquivo(filename):
    """Detecta o tipo do arquivo baseado na extensão"""
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext == 'vcf':
        return 'vcf'
    elif ext in ['xlsx', 'xls', 'csv']:
        return 'planilha'
    return 'desconhecido'

def gerar_vcf_contatos(contatos):
    """Gera conteúdo VCF a partir de lista de contatos"""
    vcf_content = []
    
    for contato in contatos:
        codigo = contato.get('Codigo', '').strip()
        nome = contato.get('Nome', '').strip()
        telefone = contato.get('Telefone', '').strip()
        
        if not nome and not telefone:
            continue
        
        # Monta o nome completo incluindo o código se disponível
        nome_completo = nome
        if codigo and codigo not in ['', 'nan']:
            nome_completo = f"{codigo} - {nome}" if nome else codigo
            
        vcf_content.append("BEGIN:VCARD")
        vcf_content.append("VERSION:3.0")
        
        if nome_completo:
            # Nome formatado (obrigatório)
            vcf_content.append(f"FN:{nome_completo}")
            
            # Nome estruturado (sobrenome;nome;;;) - mais compatível com WhatsApp
            # Separa código do nome para melhor estruturação
            if ' - ' in nome_completo:
                partes = nome_completo.split(' - ', 1)
                codigo_parte = partes[0]
                nome_parte = partes[1] if len(partes) > 1 else ''
                
                if nome_parte:
                    partes_nome = nome_parte.split(' ', 1)
                    if len(partes_nome) > 1:
                        vcf_content.append(f"N:{partes_nome[-1]};{partes_nome[0]};{codigo_parte};;")
                    else:
                        vcf_content.append(f"N:{nome_parte};{codigo_parte};;;")
                else:
                    vcf_content.append(f"N:{codigo_parte};;;;")
            else:
                partes_nome = nome_completo.split(' ', 1)
                if len(partes_nome) > 1:
                    vcf_content.append(f"N:{partes_nome[-1]};{partes_nome[0]};;;")
                else:
                    vcf_content.append(f"N:{nome_completo};;;;")
        
        if telefone:
            # Remove caracteres especiais do telefone, mas mantém + no início
            telefone_limpo = re.sub(r'[^\d\+]', '', telefone)
            if telefone_limpo:
                # Adiciona +55 se não tiver DDI (para WhatsApp Brasil)
                if not telefone_limpo.startswith('+'):
                    if len(telefone_limpo) == 11:  # DDD + 9 dígitos
                        telefone_limpo = f"+55{telefone_limpo}"
                    elif len(telefone_limpo) == 10:  # DDD + 8 dígitos
                        telefone_limpo = f"+55{telefone_limpo}"
                
                # Formato compatível com WhatsApp
                vcf_content.append(f"TEL;TYPE=CELL:{telefone_limpo}")
        
        # Adiciona organização se tiver código
        if codigo and codigo not in ['', 'nan']:
            vcf_content.append(f"ORG:Vendedor {codigo}")
        
        # Adiciona nota com informações extras
        if codigo and codigo not in ['', 'nan']:
            vcf_content.append(f"NOTE:Código Vendedor: {codigo}")
        
        vcf_content.append("END:VCARD")
        vcf_content.append("")  # Linha em branco entre contatos
    
    return '\n'.join(vcf_content)

def ler_planilha_contatos(arquivo_path):
    """Lê contatos de arquivo Excel/CSV"""
    contatos = []
    
    try:
        print(f"=== INICIANDO LEITURA DA PLANILHA ===")
        print(f"Arquivo: {arquivo_path}")
        
        # Detecta extensão
        ext = arquivo_path.rsplit('.', 1)[1].lower()
        print(f"Extensão detectada: {ext}")
        
        if ext == 'csv':
            # Tenta diferentes encodings para CSV
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    df = pd.read_csv(arquivo_path, encoding=encoding)
                    print(f"CSV lido com encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    print(f"Falha com encoding: {encoding}")
                    continue
            else:
                raise Exception("Não foi possível detectar a codificação do arquivo CSV")
        else:
            # Excel
            print("Tentando ler arquivo Excel...")
            df = pd.read_excel(arquivo_path)
            print("Arquivo Excel lido com sucesso!")
        
        print(f"Shape do DataFrame: {df.shape}")
        print(f"Colunas encontradas: {list(df.columns)}")
        print(f"DataFrame vazio?: {df.empty}")
        
        # Limpa os nomes das colunas removendo espaços extras
        df.columns = df.columns.str.strip()
        print(f"Colunas após limpeza: {list(df.columns)}")
        
        # Verifica se o DataFrame não está vazio
        if df.empty:
            print("ERRO: DataFrame está vazio!")
            return contatos
        
        # Detecta colunas automaticamente
        codigo_col = None
        nome_col = None
        telefone_col = None
        
        print("\n=== DETECTANDO COLUNAS ===")
        
        # Procura por colunas de código
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(palavra in col_lower for palavra in ['cod', 'código', 'codigo', 'code']):
                codigo_col = col
                print(f"✓ Coluna de código encontrada: {col}")
                break
        
        # Procura por colunas de nome
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(palavra in col_lower for palavra in ['nome', 'name', 'contato', 'pessoa', 'cliente']):
                nome_col = col
                print(f"✓ Coluna de nome encontrada: {col}")
                break
        
        # Procura por colunas de telefone
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if any(palavra in col_lower for palavra in ['telefone', 'phone', 'fone', 'celular', 'tel', 'mobile', 'numero']):
                telefone_col = col
                print(f"✓ Coluna de telefone encontrada: {col}")
                break
        
        # Se não encontrou, usa as colunas por posição
        if not codigo_col and len(df.columns) > 0:
            codigo_col = df.columns[0]
            print(f"Usando primeira coluna como código: {codigo_col}")
        if not nome_col and len(df.columns) > 1:
            nome_col = df.columns[1]
            print(f"Usando segunda coluna como nome: {nome_col}")
        if not telefone_col and len(df.columns) > 2:
            telefone_col = df.columns[2]
            print(f"Usando terceira coluna como telefone: {telefone_col}")
        elif not telefone_col and len(df.columns) > 1:
            telefone_col = df.columns[-1]  # Última coluna se só tiver 2 colunas
            print(f"Usando última coluna como telefone: {telefone_col}")
        
        print(f"\n=== COLUNAS SELECIONADAS ===")
        print(f"Coluna código: {codigo_col}")
        print(f"Coluna nome: {nome_col}")
        print(f"Coluna telefone: {telefone_col}")
        
        # Extrai contatos
        print(f"\n=== PROCESSANDO LINHAS ===")
        linhas_processadas = 0
        linhas_validas = 0
        
        for index, row in df.iterrows():
            linhas_processadas += 1
            
            codigo = str(row[codigo_col]).strip() if codigo_col and pd.notna(row[codigo_col]) else ''
            nome = str(row[nome_col]).strip() if nome_col and pd.notna(row[nome_col]) else ''
            telefone = str(row[telefone_col]).strip() if telefone_col and pd.notna(row[telefone_col]) else ''
            
            # Ignora linhas vazias ou com 'nan'
            if nome.lower() in ['nan', ''] and telefone.lower() in ['nan', '']:
                continue
            if nome.lower() == 'nan':
                nome = ''
            if telefone.lower() == 'nan':
                telefone = ''
            if codigo.lower() == 'nan':
                codigo = ''
            
            nome_higienizado = higienizar_nome(nome)
            telefone_formatado = formatar_telefone(telefone)
            
            # Verifica se tem pelo menos nome ou telefone válido
            if not nome_higienizado and not telefone_formatado:
                continue
                
            contatos.append({
                'Codigo': codigo,
                'Nome': nome_higienizado,
                'Telefone': telefone_formatado
            })
            linhas_validas += 1
        
        print(f"\n=== RESUMO DO PROCESSAMENTO ===")
        print(f"Linhas processadas: {linhas_processadas}")
        print(f"Linhas válidas: {linhas_validas}")
        print(f"Total de contatos: {len(contatos)}")
        
        return contatos
        
    except Exception as e:
        print(f"=== ERRO AO LER PLANILHA ===")
        print(f"Erro: {e}")
        import traceback
        print(f"Traceback completo:")
        traceback.print_exc()
        raise Exception(f"Erro ao processar planilha: {str(e)}")

def formatar_nome(nome):
    """Formata o nome para caixa alta"""
    if not nome or nome.strip() == '':
        return ''
    return nome.strip().upper()

def higienizar_nome(nome):
    """Remove números e caracteres especiais do nome, mantendo apenas letras e espaços"""
    if not nome or nome.strip() == '':
        return ''
    
    # Remove números e caracteres especiais, mantém apenas letras e espaços
    import re
    nome_limpo = re.sub(r'[^A-Za-zÀ-ÿ\s]', '', nome.strip())
    
    # Remove espaços extras
    nome_limpo = ' '.join(nome_limpo.split())
    
    return nome_limpo.upper() if nome_limpo else ''

def formatar_telefone(telefone):
    """Formata o telefone no formato brasileiro (DDD)1234-1234, removendo DDI +55"""
    if not telefone or telefone.strip() == '':
        return ''
    
    # Remove todos os caracteres não numéricos, exceto o +
    telefone_limpo = re.sub(r'[^\d\+]', '', telefone.strip())
    
    # Remove DDI +55 se presente
    if telefone_limpo.startswith('+55'):
        telefone_limpo = telefone_limpo[3:]
    elif telefone_limpo.startswith('55') and len(telefone_limpo) >= 13:
        # Remove 55 do início se o número tem 13 dígitos ou mais (55 + DDD + 9 dígitos)
        telefone_limpo = telefone_limpo[2:]
    
    # Remove zeros à esquerda
    telefone_limpo = telefone_limpo.lstrip('0')
    
    # Verifica se tem pelo menos 10 dígitos (DDD + 8 dígitos) ou 11 (DDD + 9 dígitos)
    if len(telefone_limpo) == 10:
        # Formato: DDD + 8 dígitos
        ddd = telefone_limpo[:2]
        numero = telefone_limpo[2:6] + '-' + telefone_limpo[6:]
        return f"({ddd}){numero}"
    elif len(telefone_limpo) == 11:
        # Formato: DDD + 9 dígitos
        ddd = telefone_limpo[:2]
        numero = telefone_limpo[2:7] + '-' + telefone_limpo[7:]
        return f"({ddd}){numero}"
    else:
        # Se não conseguir formatar, retorna o número limpo
        return telefone_limpo

def higienizar_planilha_vcf(contatos):
    """Higieniza dados extraídos de VCF para planilha"""
    contatos_limpos = []
    
    for contato in contatos:
        codigo = contato.get('Codigo', '').strip()
        nome = contato.get('Nome', '').strip()
        telefone = contato.get('Telefone', '').strip()
        
        # Higieniza o nome removendo números
        nome_limpo = higienizar_nome(nome)
        
        # Se o nome ficou vazio após limpeza, pula o contato
        if not nome_limpo:
            continue
        
        contatos_limpos.append({
            'Codigo': '',  # Sempre vazio conforme solicitado
            'Nome': nome_limpo,
            'Telefone': telefone
        })
    
    return contatos_limpos

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
        
        # Extrai código da organização ou nota
        codigo = ''
        org_match = re.search(r'ORG:.*Vendedor\s+([^\s\n]+)', vcard_text)
        if org_match:
            codigo = org_match.group(1).strip()
        else:
            # Tenta extrair da nota
            note_match = re.search(r'NOTE:.*Código Vendedor:\s*([^\s\n]+)', vcard_text)
            if note_match:
                codigo = note_match.group(1).strip()
            else:
                # Tenta extrair do próprio nome se tiver formato "COD - NOME"
                if ' - ' in nome:
                    partes = nome.split(' - ', 1)
                    if len(partes) == 2:
                        codigo = partes[0].strip()
                        nome = partes[1].strip()
        
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
                        'Codigo': codigo,
                        'Nome': higienizar_nome(nome),  # Usa higienizar_nome
                        'Telefone': formatar_telefone(telefone)
                    })
            else:
                contatos.append({
                    'Codigo': codigo,
                    'Nome': higienizar_nome(nome),  # Usa higienizar_nome
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
        tipo_arquivo = detectar_tipo_arquivo(filename)
        
        # Cria arquivo temporário com extensão correta
        file_extension = filename.rsplit('.', 1)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as temp_file:
            file.save(temp_file.name)
            temp_path = temp_file.name
        
        try:
            print(f"Tipo de arquivo detectado: {tipo_arquivo}")
            print(f"Processando arquivo: {temp_path}")
            
            # Processa baseado no tipo
            if tipo_arquivo == 'vcf':
                # VCF para CSV/Excel
                print("=== PROCESSANDO VCF PARA PLANILHA ===")
                
                contatos = extrair_contatos_manual(temp_path)
                print(f"Contatos extraídos do VCF: {len(contatos)}")
                
                if not contatos:
                    flash('Nenhum contato foi encontrado no arquivo VCF')
                    return redirect(url_for('upload_file'))
                
                # Higieniza os contatos extraídos do VCF
                contatos_higienizados = higienizar_planilha_vcf(contatos)
                print(f"Contatos após higienização: {len(contatos_higienizados)}")
                
                if not contatos_higienizados:
                    flash('Nenhum contato válido foi encontrado após a higienização')
                    return redirect(url_for('upload_file'))
                
                # Gera CSV e Excel separadamente
                df = pd.DataFrame(contatos_higienizados)
                df.columns = ['COD', 'NOMES CLIENTES', 'NUMEROS TELEFONE']
                base_name = filename.rsplit('.', 1)[0]
                
                # Salva CSV
                csv_filename = f'{base_name}_contatos.csv'
                csv_path = os.path.join(UPLOAD_FOLDER, csv_filename)
                df.to_csv(csv_path, index=False, encoding='utf-8')
                
                # Salva Excel
                excel_filename = f'{base_name}_contatos.xlsx'
                excel_path = os.path.join(UPLOAD_FOLDER, excel_filename)
                df.to_excel(excel_path, index=False)
                
                return render_template('resultado.html', 
                                     num_contatos=len(contatos),
                                     csv_file=csv_filename,
                                     xlsx_file=excel_filename,
                                     tipo_conversao='vcf_para_planilha')
            
            elif tipo_arquivo == 'planilha':
                # Excel/CSV para VCF
                print(f"=== PROCESSANDO PLANILHA PARA VCF ===")
                print(f"Arquivo original: {filename}")
                
                contatos = ler_planilha_contatos(temp_path)
                print(f"Contatos extraídos da planilha: {len(contatos)}")
                
                if not contatos:
                    print("ERRO: Nenhum contato foi encontrado na planilha")
                    flash('Nenhum contato foi encontrado na planilha. Verifique se o arquivo possui dados válidos nas colunas corretas.')
                    return redirect(url_for('upload_file'))
                
                # Gera VCF
                print("Gerando conteúdo VCF...")
                vcf_content = gerar_vcf_contatos(contatos)
                print(f"VCF gerado com {len(vcf_content)} caracteres")
                
                base_name = filename.rsplit('.', 1)[0]
                vcf_filename = f'{base_name}_contatos.vcf'
                vcf_path = os.path.join(UPLOAD_FOLDER, vcf_filename)
                
                # Salva arquivo VCF
                with open(vcf_path, 'w', encoding='utf-8') as f:
                    f.write(vcf_content)
                
                print(f"Arquivo VCF salvo: {vcf_filename}")
                
                return render_template('resultado.html', 
                                     num_contatos=len(contatos),
                                     vcf_file=vcf_filename,
                                     tipo_conversao='planilha_para_vcf')
            
            else:
                flash('Tipo de arquivo não suportado')
                return redirect(url_for('upload_file'))
                
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
        flash('Tipo de arquivo não permitido. Use apenas arquivos .vcf, .xlsx, .xls ou .csv')
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

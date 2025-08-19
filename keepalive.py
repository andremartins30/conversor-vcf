#!/usr/bin/env python3
"""
Script para manter a aplicação web ativa
Faz uma requisição HTTP a cada execução para evitar que o app entre em sleep
"""

import requests
import sys
import datetime
import os

# URL da sua aplicação (substitua pela URL real do seu deploy)
APP_URL = "https://vcf-converter.up.railway.app"  # Substitua pela URL real

# Arquivo de log (opcional)
LOG_FILE = os.path.expanduser("~/keepalive.log")

def fazer_requisicao():
    """Faz uma requisição simples para manter o app ativo"""
    try:
        # Faz uma requisição GET simples
        response = requests.get(APP_URL, timeout=30)
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if response.status_code == 200:
            log_message = f"[{timestamp}] ✅ App ativo - Status: {response.status_code}"
            print(log_message)
        else:
            log_message = f"[{timestamp}] ⚠️  App respondeu com status: {response.status_code}"
            print(log_message)
        
        # Escreve no arquivo de log
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
            
        return True
        
    except requests.exceptions.RequestException as e:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"[{timestamp}] ❌ Erro ao acessar {APP_URL}: {str(e)}"
        print(error_message)
        
        # Escreve erro no log
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(error_message + "\n")
            
        return False
    
    except Exception as e:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_message = f"[{timestamp}] ❌ Erro inesperado: {str(e)}"
        print(error_message)
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(error_message + "\n")
            
        return False

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        # Permite passar URL como parâmetro
        global APP_URL
        APP_URL = sys.argv[1]
    
    print(f"Fazendo requisição para: {APP_URL}")
    fazer_requisicao()

if __name__ == "__main__":
    main()

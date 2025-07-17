#!/usr/bin/env python3
import requests

# Testa o upload de arquivo
url = 'http://localhost:5000'

# Primeiro, faz um GET para pegar a página
print("Testando GET...")
response = requests.get(url)
print(f"GET Status: {response.status_code}")

# Agora testa o POST com arquivo
print("\nTestando POST com arquivo...")
try:
    with open('vcards_20250717_092847.vcf', 'rb') as f:
        files = {'file': ('test.vcf', f, 'text/vcard')}
        response = requests.post(url, files=files)
        print(f"POST Status: {response.status_code}")
        
        if response.status_code == 200:
            if 'Conversão Concluída' in response.text:
                print("✅ Upload e conversão funcionaram!")
            else:
                print("⚠️ Upload feito, mas pode haver problemas na conversão")
        else:
            print(f"❌ Erro no upload: {response.status_code}")
            
except FileNotFoundError:
    print("❌ Arquivo VCF não encontrado para teste")
except Exception as e:
    print(f"❌ Erro no teste: {e}")

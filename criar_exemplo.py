import pandas as pd

# Criar dados de exemplo
contatos_exemplo = [
    {'Nome': 'João Silva', 'Telefone': '+5511987654321'},
    {'Nome': 'Maria Santos', 'Telefone': '11999887766'},
    {'Nome': 'Pedro Oliveira', 'Telefone': '+5511988776655'},
    {'Nome': 'Ana Costa', 'Telefone': '11977665544'},
    {'Nome': 'Carlos Ferreira', 'Telefone': '+5511966554433'}
]

# Criar DataFrame
df = pd.DataFrame(contatos_exemplo)

# Salvar como Excel
df.to_excel('exemplo_contatos.xlsx', index=False)
df.to_csv('exemplo_contatos.csv', index=False)

print("Arquivos de exemplo criados:")
print("- exemplo_contatos.xlsx")
print("- exemplo_contatos.csv")
print("\nConteúdo:")
print(df)

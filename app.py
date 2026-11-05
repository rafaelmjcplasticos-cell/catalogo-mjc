import csv
from bs4 import BeautifulSoup
import requests
import streamlit as st

st.set_page_config(
page_title='Gestor de Catálogo - MJC Plásticos', layout='centered'
)

st.title('📦 Gestor de Catálogo e Precificação')
st.write(
'Extraia produtos do fornecedor e aplique sua margem de lucro'
' automaticamente.'
)

Entrada da margem de lucro pelo usuário
margem_porcentagem = st.number_input(
'Digite a sua margem de lucro (%):',
min_value=0.0,
max_value=300.0,
value=30.0,
step=5.0,
)
fator_margem = 1 + (margem_porcentagem / 100)

if st.button('🚀 Atualizar e Baixar Catálogo'):
st.info('Conectando ao fornecedor e atualizando preços...')

URL_FORNECEDOR = 'https://www.atacadodolojista.com.br/'
HEADERS = {
'User-Agent': (
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
)
}

try:
resposta = requests.get(URL_FORNECEDOR, headers=HEADERS, timeout=15)
soup = BeautifulSoup(resposta.text, 'html.parser')
itens = soup.select('.produto-item, .item-grid, .vitrine-item') or soup.select(
'div[class*="produto"]'
)

produtos = []
for item in itens:
try:
nome_elem = item.select_one(
'a.nome-produto, .produto-nome, h2 a, h3 a'
) or item.find('a')
preco_elem = item.select_one(
'.preco-por, .preco-atual, .valor, span[class*="preco"]'
)

if nome_elem and preco_elem:
nome = nome_elem.get_text(strip=True)
preco_custo = float(
preco_elem.get_text(strip=True)
.replace('R$`', '')
.replace('.', '')
.replace(',', '.')
.strip()
)
preco_venda = round(preco_custo * fator_margem, 2)

produtos.append({
'Nome do Produto': nome,
'Preço Custo (R$)': preco_custo, 'Preço Venda (R$)': preco_venda,
})
except Exception:
continue

if produtos:
st.success(f'{len(produtos)} produtos processados com sucesso!')
st.dataframe(produtos)

# Preparar CSV para download
csv_buffer = 'Nome do Produto;Preço Custo;Preço Venda\n' + '\n'.join(
[
f"{p['Nome do Produto']};{p['Preço Custo (R`$)']};{p['Preço Venda (R$)']}"
for p in produtos
]
)

st.download_button(
label='📥 Baixar Arquivo CSV para Importação',
data=csv_buffer,
file_name='catalogo_precificado.csv',
mime='text/csv',
)
else:
st.warning(
'Nenhum produto foi localizado no momento. Verifique a conexão ou a'
' estrutura do site.'
)

except Exception as e:
st.error(f'Erro durante a execução: {e}')
## 🧾 Descrição do Script

Este script automatiza a extração de informações de documentos CRLV em PDF e organiza os dados em planilhas Excel e CSV, facilitando o cadastro e o controle de veículos da frota.

### 🔧 Funcionalidades

- **Leitura de PDFs**: Utiliza `pdfplumber` para extrair o texto de todas as páginas dos documentos.
- **Processamento em lote**: Processa os arquivos `.pdf` encontrados na pasta configurada.
- **Identificação de campos**: Localiza informações por rótulos e expressões regulares.
- **Reconhecimento de placas**: Identifica placas nos formatos antigo (`ABC1234`) e Mercosul (`ABC1D23`).
- **Exportação dos resultados**: Utiliza `pandas` para gerar planilhas Excel e CSV.
- **Rastreabilidade**: Inclui o nome do arquivo de origem em cada registro.

### 🚘 Dados Extraídos

- Código RENAVAM
- Placa
- Ano de fabricação
- Ano do modelo
- Marca, modelo e versão
- Cor predominante
- Chassi — identificado como `teste_chassi` na versão atual

### 📌 Observações

- O código está configurado para uso no **Google Colab**, com os PDFs na pasta `/content`.
- Os PDFs precisam conter texto selecionável. O script não realiza OCR de documentos digitalizados como imagem.
- Alterações no layout do CRLV podem exigir ajustes na localização dos campos.
- Campos não encontrados são exportados como células vazias.
- Confira os dados extraídos antes de utilizá-los em cadastros ou análises.
- Os arquivos de saída são sobrescritos a cada execução.
- Na versão atual, o bloco de exportação deve ficar dentro do `else`, após o laço de processamento, para evitar erro quando nenhum PDF for encontrado.

### 📦 Dependências

- `pdfplumber`
- `pandas`
- `openpyxl`

### ▶️ Execução no Google Colab

**1. Instale as dependências:**

```python
%pip install pdfplumber pandas openpyxl
```

**2. Envie os PDFs e o arquivo `extracao_crlv.py` para a pasta `/content`.**

**3. Execute o script:**

```python
%run /content/extracao_crlv.py
```

Também é possível colar o código diretamente em uma célula do notebook.

### 📊 Arquivos Gerados

Após o processamento, os resultados serão salvos em:

- `/content/resultado_crlv.xlsx`
- `/content/resultado_crlv.csv`

Cada linha representa um PDF processado, com o nome do arquivo e os dados extraídos.

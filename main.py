import boto3
import os
import fitz  # PyMuPDF para processar PDFs
import requests
from botocore.exceptions import NoCredentialsError
from fastapi import FastAPI, UploadFile, File, Form

app = FastAPI()

# Configuração do DigitalOcean Spaces
s3 = boto3.client(
    "s3",
    region_name=os.getenv("SPACES_REGION", "nyc3"),  # Região padrão
    endpoint_url=os.getenv("SPACES_ENDPOINT", "https://acuracia-uploads.nyc3.digitaloceanspaces.com"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

def upload_to_spaces(file_content, file_name, bucket_name):
    """
    Faz o upload do conteúdo do arquivo diretamente para o Spaces.
    """
    try:
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content, ACL="public-read")
        return f"https://{bucket_name}.nyc3.digitaloceanspaces.com/{file_name}"
    except NoCredentialsError:
        print("Erro: Credenciais inválidas!")
        return None

def extract_text_from_pdf(pdf_content):
    """
    Converte o conteúdo de um PDF (bytes) em texto usando PyMuPDF.
    """
    texto_completo = ""
    with fitz.open(stream=pdf_content, filetype="pdf") as doc:
        for pagina in doc:
            texto_completo += pagina.get_text("text") + "\n"
    return texto_completo

def process_with_claude(text, api_key, model):
    """
    Envia o texto extraído para a API Claude 3.5 Sonnet.
    """
    api_url = "https://api.anthropic.com/v1/complete"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "prompt": f"Analise o seguinte texto do PDF:\n{text}",
        "model": model,  # Modelo informado pelo usuário
        "max_tokens": 1000,
        "temperature": 0.7
    }
    response = requests.post(api_url, json=data, headers=headers)
    return response.json()

@app.post("/processar-pdf/")
async def processar_pdf(
    file: UploadFile = File(...),
    claude_api_key: str = Form(None),  # Permite passar a chave na requisição
    claude_model: str = Form(None)  # Permite passar o modelo na requisição
):
    """
    Recebe um PDF via API, faz upload para o Spaces, extrai o texto e processa na Claude 3.5.
    """
    file_content = await file.read()
    file_name = file.filename
    bucket_name = "acuracia-uploads"

    # Upload do arquivo para o Spaces
    file_url = upload_to_spaces(file_content, file_name, bucket_name)
    if not file_url:
        return {"erro": "Falha no upload do arquivo para o Spaces"}

    # Extrair texto do PDF
    extracted_text = extract_text_from_pdf(file_content)
    
    # Definir API Key e modelo da Claude (usa a chave fixa como padrão)
    api_key = claude_api_key if claude_api_key else "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"
    model = claude_model if claude_model else os.getenv("CLAUDE_MODEL", "claude-3.5-sonnet")

    # Enviar para análise na Claude
    analysis_result = process_with_claude(extracted_text, api_key, model)

    return {
        "mensagem": "Arquivo processado com sucesso!",
        "arquivo": file_url,
        "modelo_utilizado": model,
        "texto_extraido": extracted_text,
        "analise_claude": analysis_result
    }

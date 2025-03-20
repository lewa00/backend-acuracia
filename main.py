import boto3
import os
import fitz  # PyMuPDF para processar PDFs
import requests
from botocore.exceptions import NoCredentialsError
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

# Configuração do DigitalOcean Spaces
s3 = boto3.client(
    "s3",
    region_name=os.getenv("SPACES_REGION"),  # Defina nas variáveis de ambiente
    endpoint_url=os.getenv("SPACES_ENDPOINT"),
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

def process_with_claude(text):
    """
    Envia o texto extraído para a API Claude 3.5 Sonnet.
    """
    api_url = "https://api.anthropic.com/v1/complete"
    api_key = os.getenv("CLAUDE_API_KEY")  # Defina sua chave nas variáveis de ambiente
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "prompt": f"Analise o seguinte texto do PDF:\n{text}",
        "model": "claude-3.5-sonnet",
        "max_tokens": 1000,
        "temperature": 0.7
    }
    response = requests.post(api_url, json=data, headers=headers)
    return response.json()

@app.post("/processar-pdf/")
async def processar_pdf(file: UploadFile = File(...)):
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
    
    # Enviar para análise na Claude
    analysis_result = process_with_claude(extracted_text)

    return {
        "mensagem": "Arquivo processado com sucesso!",
        "arquivo": file_url,
        "texto_extraido": extracted_text,
        "analise_claude": analysis_result
    }

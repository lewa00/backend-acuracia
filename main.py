import boto3
import os
from botocore.exceptions import NoCredentialsError
import requests

# Configuração do DigitalOcean Spaces
s3 = boto3.client(
    's3',
    region_name=os.getenv("SPACES_REGION", "acuracia-uploads"),
    endpoint_url=os.getenv("SPACES_ENDPOINT", "https://acuracia-uploads.nyc3.digitaloceanspaces.com"),
    aws_access_key_id=os.getenv("DO004TMXGE2EDPLNNXQ4"),
    aws_secret_access_key=os.getenv("dop_v1_48d8e3960b0a46efaeabeaee80699a3b0553cee54d6ddae9a6099268cb6c032a"),
)

def upload_to_spaces(file_path, file_name, bucket_name):
    try:
        s3.upload_file(file_path, bucket_name, file_name)
        return f"https://{bucket_name}.nyc3.digitaloceanspaces.com/{file_name}"
    except NoCredentialsError:
        print("Credenciais inválidas!")
        return None

# Integração com a API da Claude 3.5 Sonnet
def process_with_claude(pdf_content):
    api_url = "https://api.anthropic.com/v1/complete"
    api_key = os.getenv("CLAUDE_API_KEY")
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "prompt": "Extraia o texto do seguinte PDF:",
        "model": "claude-3.5-sonnet",
        "max_tokens": 1000,
        "temperature": 0.7,
        "document": pdf_content.decode("utf-8")
    }
    response = requests.post(api_url, json=data, headers=headers)
    return response.json()

# Exemplo de uso da integração
def processar_pdf(file_path, file_name, bucket_name):
    # Enviar o arquivo para o Spaces
    file_url = upload_to_spaces(file_path, file_name, bucket_name)
    if file_url:
        print(f"Arquivo enviado com sucesso: {file_url}")
    else:
        print("Erro ao enviar o arquivo.")
        return
    
    # Processar com Claude
    with open(file_path, "rb") as file:
        pdf_content = file.read()
    extracted_text = process_with_claude(pdf_content)
    print("Texto extraído:", extracted_text)
    return extracted_text

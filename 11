import boto3
import os

# Definir manualmente as credenciais (substitua pelos valores corretos)
os.environ["AWS_ACCESS_KEY_ID"] = "SUA_ACCESS_KEY_ID"
os.environ["AWS_SECRET_ACCESS_KEY"] = "SUA_SECRET_ACCESS_KEY"
os.environ["SPACES_REGION"] = "nyc3"
os.environ["SPACES_ENDPOINT"] = "https://acuracia-uploads.nyc3.digitaloceanspaces.com"

# Criando o cliente S3 (Spaces)
s3 = boto3.client(
    "s3",
    region_name=os.getenv("SPACES_REGION"),
    endpoint_url=os.getenv("SPACES_ENDPOINT"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

# Testando conexão
try:
    response = s3.list_buckets()
    print("Conexão bem-sucedida! Buckets disponíveis:", response["Buckets"])
except Exception as e:
    print("Erro ao conectar:", str(e))

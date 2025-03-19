from fastapi import FastAPI, UploadFile, File
import fitz  # PyMuPDF para manipular PDFs
import google.generativeai as genai

# Configuração da API Gemini (Google AI)
GOOGLE_API_KEY = "AIzaSyA4bBE02Usi7kc1tAuGJxb9r1I7-6ehiZ8"
genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()

@app.post("/processar-pdf/")
async def processar_pdf(file: UploadFile = File(...)):
    conteudo_pdf = await file.read()
    pdf_documento = fitz.open(stream=conteudo_pdf, filetype="pdf")

    texto_completo = ''
    for pagina in pdf_documento:
        texto_completo += pagina.get_text()

    # Enviar o texto para a API Gemini para gerar perguntas e respostas
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(
        f"Leia o seguinte conteúdo extraído de um PDF e gere um conjunto de perguntas e respostas úteis para ensino:\n\n{texto_completo}"
    )

    # Capturar resposta da Gemini
    perguntas_respostas = response.text

    return {"resultado": perguntas_respostas}

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import mercadopago
import os
import requests
import base64

app = FastAPI(title="Estúdio Pro AI - Full Suite")
sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))
IA_KEY = os.getenv("PHOTOROOM_API_KEY", "")

@app.get("/", response_class=HTMLResponse)
def interface():
    return """
    <!DOCTYPE html>
    <html class="bg-zinc-950 text-white"><script src="https://cdn.tailwindcss.com"></script>
    <body class="p-6 max-w-lg mx-auto">
        <h1 class="text-3xl font-bold text-center mb-6">Estúdio Pro <span class="text-blue-500">AI</span></h1>
        <input type="file" id="file" class="w-full bg-zinc-900 p-4 rounded border border-zinc-700">
        <button onclick="processar()" id="proc-btn" class="w-full mt-4 bg-blue-600 p-4 rounded font-bold">Gerar Cenário Profissional</button>
        <div id="preview" class="hidden mt-6 text-center">
            <img id="img-preview" class="w-full rounded mb-4">
            <button onclick="gerarPix()" id="pay-btn" class="w-full bg-emerald-600 p-4 rounded font-bold">Liberar Download (R$ 1,00)</button>
        </div>
        <div id="pix-area" class="hidden mt-6 p-4 bg-black border border-emerald-500 text-xs font-mono"></div>
        <button id="download-btn" class="hidden w-full mt-4 bg-white text-black p-4 rounded font-bold">DOWNLOAD FINAL</button>
        <script>
            let imageBase64 = "";
            async function processar() {
                const formData = new FormData();
                formData.append('file', document.getElementById('file').files[0]);
                const res = await fetch('/processar', {method: 'POST', body: formData});
                const data = await res.json();
                imageBase64 = data.image;
                document.getElementById('img-preview').src = 'data:image/png;base64,' + imageBase64;
                document.getElementById('preview').classList.remove('hidden');
            }
            async function gerarPix() {
                const res = await fetch('/gerar-pix', {method: 'POST'});
                const data = await res.json();
                document.getElementById('pix-area').innerHTML = "PIX: " + data.qr_code + "<br><button onclick='checarPagamento()' class='mt-2 text-blue-400'>Já Paguei</button>";
                document.getElementById('pix-area').classList.remove('hidden');
            }
            async function checarPagamento() {
                document.getElementById('download-btn').classList.remove('hidden');
                document.getElementById('download-btn').onclick = () => {
                    const link = document.createElement('a');
                    link.href = 'data:image/png;base64,' + imageBase64;
                    link.download = 'foto-profissional.png';
                    link.click();
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/processar")
async def processar(file: UploadFile = File(...)):
    contents = await file.read()
    # Endpoint da API Photoroom para backgrounds instantâneos
    response = requests.post(
        'https://sdk.photoroom.com/v1/instant-background', 
        files={'image_file': contents},
        headers={'x-api-key': IA_KEY}
    )
    if response.status_code == 200:
        return {"image": base64.b64encode(response.content).decode()}
    return JSONResponse(status_code=400, content={"error": "Falha na IA"})

@app.post("/gerar-pix")
async def gerar_pix():
    resposta = sdk.payment().create({"transaction_amount": 1.0, "description": "Composição HD", "payment_method_id": "pix"})
    return {"qr_code": resposta["response"]["point_of_interaction"]["transaction_data"]["qr_code"]}

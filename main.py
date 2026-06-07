from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
import mercadopago
import os
import requests
import base64

app = FastAPI(title="Estúdio Pro AI - Full Automation")
sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))
REMOVEBG_KEY = os.getenv("REMOVEBG_API_KEY", "")

@app.get("/", response_class=HTMLResponse)
def interface():
    return """
    <!DOCTYPE html>
    <html class="bg-zinc-950 text-white">
    <script src="https://cdn.tailwindcss.com"></script>
    <body class="p-6 max-w-lg mx-auto">
        <h1 class="text-3xl font-bold text-center mb-6">Estúdio Pro <span class="text-blue-500">AI</span></h1>
        <div id="app" class="space-y-4">
            <input type="file" id="file" class="w-full bg-zinc-900 p-4 rounded border border-zinc-700">
            <button onclick="uploadFoto()" class="w-full bg-blue-600 p-4 rounded font-bold">Processar Foto (IA)</button>
            <div id="preview" class="hidden">
                <img id="img-preview" class="w-full rounded border border-zinc-700">
                <button onclick="gerarPix()" class="w-full mt-4 bg-emerald-600 p-4 rounded font-bold">Baixar HD por R$ 1,00</button>
            </div>
            <div id="pix-area"></div>
        </div>
        <script>
            async function uploadFoto() {
                const file = document.getElementById('file').files[0];
                const formData = new FormData();
                formData.append('file', file);
                const res = await fetch('/processar', {method: 'POST', body: formData});
                const data = await res.json();
                document.getElementById('img-preview').src = 'data:image/png;base64,' + data.image;
                document.getElementById('preview').classList.remove('hidden');
            }
            async function gerarPix() {
                const res = await fetch('/gerar-pix', {method: 'POST'});
                const data = await res.json();
                document.getElementById('pix-area').innerHTML = `<p class='mt-4 p-2 bg-black text-xs font-mono break-all'>${data.qr_code}</p>`;
            }
        </script>
    </body>
    </html>
    """

@app.post("/processar")
async def processar_imagem(file: UploadFile = File(...)):
    contents = await file.read()
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': contents},
        data={'size': 'auto'},
        headers={'X-Api-Key': REMOVEBG_KEY}
    )
    if response.status_code == 200:
        return {"image": base64.b64encode(response.content).decode()}
    return JSONResponse(status_code=400, content={"error": "Falha na IA"})

@app.post("/gerar-pix")
async def gerar_pix():
    resposta = sdk.payment().create({"transaction_amount": 1.0, "description": "Foto HD", "payment_method_id": "pix"})
    return {"qr_code": resposta["response"]["point_of_interaction"]["transaction_data"]["qr_code"]}

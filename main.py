from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import mercadopago
import os
import requests
import base64

app = FastAPI(title="Estúdio Pro AI - Full Composition")
sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))
# A chave de API agora é para a Photoroom (ou ferramenta de composição generativa)
IA_KEY = os.getenv("PHOTOROOM_API_KEY", "")

@app.get("/", response_class=HTMLResponse)
def interface_vendas():
    return """
    <!DOCTYPE html>
    <html class="bg-zinc-950 text-white">
    <script src="https://cdn.tailwindcss.com"></script>
    <body class="p-6 max-w-lg mx-auto">
        <header class="text-center mb-10">
            <h1 class="text-4xl font-extrabold">Estúdio Pro <span class="text-blue-500">AI</span></h1>
            <p class="text-zinc-400">Transformação com IA Generativa</p>
        </header>

        <div class="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
            <input type="file" id="file" class="hidden" accept="image/*">
            <div id="drop-zone" onclick="document.getElementById('file').click()" 
                 class="border-2 border-dashed border-zinc-700 p-10 text-center rounded-xl cursor-pointer hover:border-blue-500 transition-all">
                <p>Suba sua foto para o Estúdio IA</p>
            </div>
        </div>

        <div id="result-area" class="hidden mt-6 bg-zinc-900 p-6 rounded-2xl border border-zinc-800 text-center">
            <p class="text-blue-400 text-sm font-bold mb-4">Composição Profissional (Preview)</p>
            <img id="img-preview" class="w-full rounded-lg mb-4 border border-zinc-700">
            <button onclick="gerarPix()" id="pay-btn" class="w-full bg-blue-600 p-4 rounded-xl font-bold">
                Download HD (Sem Marca) - R$ 1,00
            </button>
        </div>
        
        <div id="pix-area" class="hidden mt-6 bg-emerald-900/20 p-6 rounded-2xl border border-emerald-500/50 text-center">
            <textarea id="pix-code" class="w-full bg-black text-xs text-emerald-400 p-3 rounded font-mono" readonly></textarea>
        </div>

        <script>
            document.getElementById('file').onchange = async (e) => {
                const formData = new FormData();
                formData.append('file', e.target.files[0]);
                const res = await fetch('/processar', {method: 'POST', body: formData});
                const data = await res.json();
                document.getElementById('img-preview').src = 'data:image/png;base64,' + data.image;
                document.getElementById('result-area').classList.remove('hidden');
            };
            async function gerarPix() {
                const res = await fetch('/gerar-pix', {method: 'POST'});
                const data = await res.json();
                document.getElementById('pix-code').value = data.qr_code;
                document.getElementById('pix-area').classList.remove('hidden');
            }
        </script>
    </body>
    </html>
    """

@app.post("/processar")
async def processar(file: UploadFile = File(...)):
    contents = await file.read()
    # Integração com API de Composição Generativa
    response = requests.post(
        'https://sdk.photoroom.com/v1/segment', # Endpoint exemplo de composição
        files={'image_file': contents},
        headers={'x-api-key': IA_KEY}
    )
    if response.status_code == 200:
        return {"image": base64.b64encode(response.content).decode()}
    return JSONResponse(status_code=400, content={"error": "Falha na Composição IA"})

@app.post("/gerar-pix")
async def gerar_pix():
    resposta = sdk.payment().create({"transaction_amount": 1.0, "description": "Composição HD", "payment_method_id": "pix"})
    return {"qr_code": resposta["response"]["point_of_interaction"]["transaction_data"]["qr_code"]}

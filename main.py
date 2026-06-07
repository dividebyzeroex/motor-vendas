from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
import mercadopago
import os
import requests
import base64

app = FastAPI(title="Estúdio Pro AI")
sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))
IA_KEY = os.getenv("PHOTOROOM_API_KEY", "")

@app.get("/", response_class=HTMLResponse)
def interface():
    return """
    <!DOCTYPE html>
    <html class="bg-zinc-950 text-white">
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body class="p-4 md:p-10 font-sans">
        <div class="max-w-md mx-auto">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">Estúdio Pro AI</h1>
                <p class="text-zinc-500 text-sm">Qualidade de estúdio em um toque.</p>
            </div>

            <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-6 shadow-2xl">
                <div id="drop-zone" class="border-2 border-dashed border-zinc-700 p-8 rounded-2xl text-center cursor-pointer hover:border-blue-500 transition">
                    <p id="label-upload">Clique ou arraste sua foto aqui</p>
                    <input type="file" id="file" class="hidden" accept="image/*">
                </div>
                <img id="img-preview" class="hidden w-full rounded-2xl mt-4 border border-zinc-700">
                <button id="btn-processar" onclick="processar()" class="hidden w-full mt-6 bg-blue-600 p-4 rounded-xl font-bold">Processar com IA</button>
                <p id="error-msg" class="hidden text-red-400 text-sm mt-4 text-center"></p>
            </div>

            <div id="pay-area" class="hidden mt-6 bg-zinc-900 border border-emerald-500/30 p-6 rounded-3xl text-center">
                <h2 class="font-bold text-lg mb-2">Composição pronta!</h2>
                <button id="btn-pix" onclick="gerarPix()" class="w-full bg-emerald-600 p-4 rounded-xl font-bold">Liberar HD por R$ 1,00</button>
                <div id="pix-content" class="hidden mt-4">
                    <input type="text" id="pix-code" class="w-full bg-black p-3 rounded text-xs font-mono mb-2" readonly>
                    <button onclick="copiarPix()" class="text-blue-400 text-sm underline">Copiar código PIX</button>
                </div>
                <p id="pix-error" class="hidden text-red-400 text-sm mt-4 text-center"></p>
            </div>
        </div>

        <script>
            document.getElementById('drop-zone').onclick = () => document.getElementById('file').click();
            
            document.getElementById('file').onchange = (e) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('img-preview').src = e.target.result;
                    document.getElementById('img-preview').classList.remove('hidden');
                    document.getElementById('btn-processar').classList.remove('hidden');
                    document.getElementById('error-msg').classList.add('hidden');
                };
                reader.readAsDataURL(e.target.files[0]);
            };

            async function processar() {
                const btn = document.getElementById('btn-processar');
                const errorMsg = document.getElementById('error-msg');
                btn.innerText = "IA Processando (Aguarde)...";
                btn.disabled = true;
                errorMsg.classList.add('hidden');
                
                try {
                    const formData = new FormData();
                    formData.append('file', document.getElementById('file').files[0]);
                    
                    const res = await fetch('/processar', {method: 'POST', body: formData});
                    const data = await res.json();
                    
                    if (res.ok && data.image) {
                        document.getElementById('img-preview').src = 'data:image/png;base64,' + data.image;
                        document.getElementById('pay-area').classList.remove('hidden');
                        btn.classList.add('hidden');
                    } else {
                        errorMsg.innerText = "Falha na IA: Verifique a configuração da sua Chave API do Photoroom no Render.";
                        errorMsg.classList.remove('hidden');
                        btn.innerText = "Tentar Novamente";
                        btn.disabled = false;
                    }
                } catch (error) {
                    errorMsg.innerText = "Erro de conexão com o servidor.";
                    errorMsg.classList.remove('hidden');
                    btn.innerText = "Tentar Novamente";
                    btn.disabled = false;
                }
            }

            async function gerarPix() {
                const btnPix = document.getElementById('btn-pix');
                const pixError = document.getElementById('pix-error');
                btnPix.innerText = "Gerando PIX...";
                btnPix.disabled = true;
                pixError.classList.add('hidden');
                
                try {
                    const res = await fetch('/gerar-pix', {method: 'POST'});
                    const data = await res.json();
                    
                    if (res.ok && data.qr_code) {
                        document.getElementById('pix-code').value = data.qr_code;
                        document.getElementById('pix-content').classList.remove('hidden');
                        btnPix.classList.add('hidden');
                    } else {
                        pixError.innerText = "Falha no Mercado Pago: Verifique seu Access Token.";
                        pixError.classList.remove('hidden');
                        btnPix.innerText = "Tentar Novamente";
                        btnPix.disabled = false;
                    }
                } catch (error) {
                    pixError.innerText = "Erro de comunicação com o gateway de pagamento.";
                    pixError.classList.remove('hidden');
                    btnPix.innerText = "Tentar Novamente";
                    btnPix.disabled = false;
                }
            }

            function copiarPix() {
                const copyText = document.getElementById('pix-code');
                copyText.select();
                document.execCommand('copy');
                alert("Código PIX copiado com sucesso!");
            }
        </script>
    </body>
    </html>
    """

@app.post("/processar")
async def processar(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        response = requests.post(
            'https://sdk.photoroom.com/v1/instant-background', 
            files={'image_file': contents},
            headers={'x-api-key': IA_KEY}
        )
        if response.status_code == 200:
            return {"image": base64.b64encode(response.content).decode()}
        return JSONResponse(status_code=response.status_code, content={"error": "Falha na comunicação com a IA."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/gerar-pix")
async def gerar_pix():
    try:
        dados_pagamento = {
            "transaction_amount": 1.0, 
            "description": "Composição HD Estúdio Pro", 
            "payment_method_id": "pix",
            "payer": {
                "email": "cliente@estudiopro.com"
            }
        }
        resposta = sdk.payment().create(dados_pagamento)
        
        if resposta["status"] == 201:
            return {"qr_code": resposta["response"]["point_of_interaction"]["transaction_data"]["qr_code"]}
        return JSONResponse(status_code=400, content={"error": "Falha na geração do PIX."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

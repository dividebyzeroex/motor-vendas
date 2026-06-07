from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import mercadopago
import os

app = FastAPI(title="Estúdio Pro AI")
sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))

@app.get("/", response_class=HTMLResponse)
def interface_premium():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR" class="bg-zinc-950 text-white">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Estúdio Pro AI</title>
    </head>
    <body class="p-4 md:p-8">
        <div class="max-w-xl mx-auto space-y-6">
            <header class="text-center mb-8">
                <h1 class="text-3xl font-bold">Estúdio Pro <span class="text-blue-500">AI</span></h1>
                <p class="text-zinc-400">Qualidade de estúdio em 60 segundos.</p>
            </header>

            <div class="bg-zinc-900 p-6 rounded-2xl border border-zinc-800">
                <div id="drop-zone" class="border-2 border-dashed border-zinc-700 p-10 text-center rounded-xl cursor-pointer hover:border-blue-500 transition-all">
                    <p>Arraste ou clique para subir sua foto (Demo Grátis)</p>
                </div>
                <input type="file" id="file-input" class="hidden" accept="image/*">
            </div>

            <div id="preview-area" class="hidden bg-zinc-900 p-6 rounded-2xl border border-zinc-800 text-center">
                <p class="text-yellow-500 text-sm font-bold mb-4">Preview com Marca d'Água</p>
                <div class="h-64 bg-zinc-800 rounded-lg mb-4 flex items-center justify-center border border-zinc-700">
                    <img id="image-preview" class="max-h-full object-contain">
                </div>
                <button onclick="gerarPix()" id="pay-btn" class="w-full bg-blue-600 hover:bg-blue-700 p-4 rounded-xl font-bold transition-all">
                    Remover Marca d'Água (R$ 1,00)
                </button>
            </div>

            <div id="checkout-area" class="hidden bg-zinc-900 p-6 rounded-2xl border border-emerald-500/50 text-center">
                <h2 class="text-xl font-bold mb-4">Pagamento via PIX</h2>
                <div id="pix-container" class="bg-black p-4 rounded font-mono text-xs text-blue-400 break-all"></div>
                <p class="text-emerald-400 mt-4 animate-pulse">Aguardando confirmação...</p>
            </div>
        </div>

        <script>
            const dropZone = document.getElementById('drop-zone');
            const fileInput = document.getElementById('file-input');
            
            dropZone.onclick = () => fileInput.click();
            fileInput.onchange = (e) => {
                const reader = new FileReader();
                reader.onload = (e) => {
                    document.getElementById('image-preview').src = e.target.result;
                    document.getElementById('preview-area').classList.remove('hidden');
                };
                reader.readAsDataURL(e.target.files[0]);
            };

            async function gerarPix() {
                document.getElementById('pay-btn').disabled = true;
                const res = await fetch('/gerar-pix', {method: 'POST'});
                const data = await res.json();
                document.getElementById('checkout-area').classList.remove('hidden');
                document.getElementById('pix-container').innerText = data.qr_code;
            }
        </script>
    </body>
    </html>
    """

@app.post("/gerar-pix")
async def gerar_pix():
    resposta = sdk.payment().create({
        "transaction_amount": 1.0, 
        "description": "Otimizacao Estúdio Pro AI",
        "payment_method_id": "pix"
    })
    return {"qr_code": resposta["response"]["point_of_interaction"]["transaction_data"]["qr_code"]}

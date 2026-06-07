from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import mercadopago
import os
import uuid

app = FastAPI(title="Estúdio Pro AI - Motor de Conversão")
sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))

@app.get("/", response_class=HTMLResponse)
def interface_vendas():
    return """
    <!DOCTYPE html>
    <html class="bg-slate-950 text-white">
    <script src="https://cdn.tailwindcss.com"></script>
    <body class="p-6 max-w-lg mx-auto">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold mb-2">Estúdio Pro <span class="text-blue-500">AI</span></h1>
            <p class="text-slate-400">Qualidade de estúdio em 60 segundos.</p>
        </div>
        
        <div id="upload-zone" class="border-2 border-dashed border-slate-700 p-12 text-center rounded-2xl cursor-pointer hover:border-blue-500 transition-all">
            <p class="text-slate-300">Arraste ou clique para subir sua foto de produto (Demo Grátis)</p>
        </div>

        <div id="preview-area" class="hidden mt-8 text-center">
            <div class="bg-slate-900 p-4 rounded-xl border border-slate-700">
                <p class="text-sm text-yellow-500 mb-2">Preview com Marca d'Água</p>
                <div class="h-48 bg-slate-800 rounded flex items-center justify-center border border-slate-700 mb-4">IMAGEM PROCESSADA</div>
                <button onclick="showPayment()" class="w-full bg-blue-600 hover:bg-blue-700 p-4 rounded-xl font-bold transition-all">
                    Liberar Versão HD e Sem Marca (R$ 15,00)
                </button>
            </div>
        </div>

        <div id="checkout-area" class="hidden mt-6 p-6 bg-slate-900 rounded-xl border border-emerald-500">
            <h2 class="text-xl font-bold mb-4">Pagamento Seguro</h2>
            <div id="pix-container"></div>
            <p class="text-xs text-slate-500 mt-4 text-center italic">Após o pagamento, o download iniciará automaticamente.</p>
        </div>

        <script>
            document.getElementById('upload-zone').onclick = () => {
                document.getElementById('preview-area').classList.remove('hidden');
            };
            
            function showPayment() {
                document.getElementById('checkout-area').classList.remove('hidden');
                gerarPix();
            }

            async function gerarPix() {
                const res = await fetch('/gerar-pix', {method: 'POST'});
                const data = await res.json();
                document.getElementById('pix-container').innerHTML = `
                    <textarea class='w-full bg-black text-xs text-blue-400 p-3 rounded font-mono' readonly>${data.qr_code}</textarea>
                    <p class="text-center mt-2 text-emerald-400 text-sm font-bold animate-pulse">Aguardando confirmação...</p>
                `;
            }
        </script>
    </body>
    </html>
    """

@app.post("/gerar-pix")
async def gerar_pix():
    # Aqui o sistema fala com o banco e gera o PIX dinâmico
    resposta = sdk.payment().create({
        "transaction_amount": 15.0, 
        "description": "Otimizacao Estúdio Pro AI",
        "payment_method_id": "pix"
    })
    return {"qr_code": resposta["response"]["point_of_interaction"]["transaction_data"]["qr_code"]}

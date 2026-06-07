from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import mercadopago
import os

app = FastAPI(title="Estúdio Pro IA")
sdk = mercadopago.SDK(os.getenv("MERCADOPAGO_ACCESS_TOKEN", ""))

@app.get("/", response_class=HTMLResponse)
def interface_demo():
    return """
    <!DOCTYPE html>
    <html class="bg-slate-950 text-white">
    <script src="https://cdn.tailwindcss.com"></script>
    <body class="p-6 max-w-lg mx-auto">
        <h1 class="text-3xl font-bold mb-4">Veja a mágica da IA</h1>
        <p class="mb-6 text-slate-400">Suba uma foto e veja o fundo ser removido e o cenário ser recriado em segundos.</p>
        
        <div id="demo-zone" class="border-2 border-dashed border-slate-700 p-10 text-center rounded-xl cursor-pointer">
            <p>Clique ou arraste sua foto aqui (Demo Grátis)</p>
        </div>
        
        <div id="checkout" class="hidden mt-8 p-6 bg-slate-900 rounded-xl border border-blue-500">
            <h2 class="text-xl font-bold mb-2">Resultado Incrível!</h2>
            <p class="text-sm mb-4">Pague R$ 15,00 para baixar a versão em alta resolução sem marca d'água.</p>
            <button onclick="gerarPix()" class="w-full bg-blue-600 p-3 rounded">Pagar R$ 15,00 via PIX</button>
            <div id="pix-area" class="mt-4"></div>
        </div>

        <script>
            // Simulação da IA: Quando o usuário sobe a foto, mostramos o checkout
            document.getElementById('demo-zone').onclick = () => {
                document.getElementById('checkout').classList.remove('hidden');
            };
            
            async function gerarPix() {
                const res = await fetch('/gerar-pix', {method: 'POST'});
                const data = await res.json();
                document.getElementById('pix-area').innerHTML = `<textarea class='w-full bg-black text-xs text-blue-400 p-2'>${data.qr_code}</textarea>`;
            }
        </script>
    </body>
    </html>
    """

@app.post("/gerar-pix")
async def gerar_pix():
    # Integração real Mercado Pago
    resposta = sdk.payment().create({"transaction_amount": 15.0, "payment_method_id": "pix"})
    return {"qr_code": resposta["response"]["point_of_interaction"]["transaction_data"]["qr_code"]}

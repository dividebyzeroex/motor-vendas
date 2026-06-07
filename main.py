from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import mercadopago
import os

app = FastAPI(title="Estúdio Autônomo AI")
TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
sdk = mercadopago.SDK(TOKEN)

@app.get("/", response_class=HTMLResponse)
def interface_premium():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <title>Estúdio Pro AI | Otimização de Imagens</title>
    </head>
    <body class="bg-slate-950 text-slate-200 font-sans">
        <div class="max-w-xl mx-auto px-6 py-12">
            <!-- Header -->
            <header class="text-center mb-12">
                <h1 class="text-3xl font-bold text-white mb-2">Estúdio Pro <span class="text-blue-500">AI</span></h1>
                <p class="text-slate-400">Transforme fotos de celular em vitrines profissionais.</p>
            </header>

            <!-- Vantagens -->
            <div class="grid grid-cols-2 gap-4 mb-10">
                <div class="bg-slate-900 p-4 rounded-lg border border-slate-800">
                    <p class="text-blue-400 font-bold">✓ 3x mais vendas</p>
                    <small class="text-xs text-slate-500">Imagens otimizadas convertem mais.</small>
                </div>
                <div class="bg-slate-900 p-4 rounded-lg border border-slate-800">
                    <p class="text-emerald-400 font-bold">✓ Entrega em 60s</p>
                    <small class="text-xs text-slate-500">Processamento em nuvem ultra rápido.</small>
                </div>
            </div>

            <!-- Form -->
            <div class="bg-slate-900 p-8 rounded-2xl border border-slate-800 shadow-xl">
                <h2 class="text-xl font-semibold mb-6 text-white">Começar agora</h2>
                <input type="email" id="email" class="w-full bg-slate-950 border border-slate-700 p-3 rounded-lg mb-4" placeholder="Seu melhor e-mail">
                <input type="number" id="qtd" class="w-full bg-slate-950 border border-slate-700 p-3 rounded-lg mb-6" placeholder="Quantidade de produtos">
                <button onclick="gerarPix()" id="btn" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-4 rounded-lg transition-all">
                    Processar por R$ 15,00/un
                </button>
                <div id="resultado" class="mt-6 text-center"></div>
                <p class="text-[10px] text-slate-600 text-center mt-4 uppercase tracking-widest">Pagamento seguro via Mercado Pago</p>
            </div>
        </div>

        <script>
            async function gerarPix() {
                const btn = document.getElementById('btn');
                const resDiv = document.getElementById('resultado');
                const email = document.getElementById('email').value;
                const qtd = document.getElementById('qtd').value;
                
                if(!email || !qtd) { alert("Preencha os campos."); return; }
                
                btn.innerText = "Processando...";
                btn.disabled = true;
                
                try {
                    const response = await fetch(`/gerar-pix?email=${email}&quantidade=${qtd}`, { method: 'POST' });
                    const data = await response.json();
                    
                    if(data.qr_code_pix) {
                        resDiv.innerHTML = `
                            <div class="bg-emerald-900/20 p-4 rounded-lg border border-emerald-500/30">
                                <p class="text-emerald-400 font-bold text-sm mb-2">PIX GERADO COM SUCESSO</p>
                                <textarea class="w-full h-20 bg-slate-950 border border-slate-700 p-2 text-xs text-emerald-400 font-mono" readonly>${data.qr_code_pix}</textarea>
                                <p class="text-[10px] text-slate-400 mt-2">O sistema liberará seu acesso em instantes após o pagamento.</p>
                            </div>
                        `;
                    } else {
                        resDiv.innerHTML = "<p class='text-red-400'>Erro no sistema. Tente novamente.</p>";
                    }
                } catch(e) { resDiv.innerHTML = "Erro de conexão."; }
                btn.innerText = "Processar por R$ 15,00/un";
                btn.disabled = false;
            }
        </script>
    </body>
    </html>
    """

@app.post("/gerar-pix")
async def gerar_pix(email: str, quantidade: int):
    valor = float(quantidade * 15.00)
    dados = {
        "transaction_amount": valor,
        "description": f"Otimizacao de {quantidade} produtos",
        "payment_method_id": "pix",
        "payer": {"email": email}
    }
    resposta = sdk.payment().create(dados)
    if resposta["status"] == 201:
        pagamento = resposta["response"]
        return {"qr_code_pix": pagamento["point_of_interaction"]["transaction_data"]["qr_code"]}
    return {"erro": "Falha"}

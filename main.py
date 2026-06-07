from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import mercadopago
import os

app = FastAPI(title="Motor de Automação")

# O sistema puxa sua chave de produção automaticamente do Render
TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
sdk = mercadopago.SDK(TOKEN)

@app.get("/", response_class=HTMLResponse)
def interface_da_plataforma():
    html = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Estúdio Autônomo AI</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .container { background: #1e293b; padding: 30px; border-radius: 12px; width: 90%; max-width: 400px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
            h2 { margin-top: 0; font-size: 22px; text-align: center; color: #38bdf8; }
            p { color: #94a3b8; font-size: 14px; text-align: center; margin-bottom: 25px; line-height: 1.5; }
            input { width: 100%; box-sizing: border-box; padding: 12px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #334155; background: #0f172a; color: white; font-size: 16px; }
            button { width: 100%; padding: 15px; background: #10b981; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; }
            button:hover { background: #059669; }
            .resultado { margin-top: 20px; font-size: 14px; text-align: center; }
            textarea { width: 100%; height: 90px; margin-top: 10px; background: #0f172a; color: #10b981; border: 1px solid #334155; border-radius: 4px; padding: 10px; box-sizing: border-box; font-family: monospace; font-size: 13px; resize: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Otimização de Catálogo</h2>
            <p>Remova fundos, crie cenários de estúdio e gere descrições de alta conversão.</p>
            <input type="email" id="email" placeholder="Seu e-mail profissional" required>
            <input type="number" id="qtd" placeholder="Quantidade de produtos" min="1" required>
            <button onclick="gerarPix()">Iniciar Otimização e Pagar via PIX</button>
            <div id="resultado" class="resultado"></div>
        </div>
        <script>
            async function gerarPix() {
                const email = document.getElementById('email').value;
                const qtd = document.getElementById('qtd').value;
                const resDiv = document.getElementById('resultado');
                
                if(!email || !qtd) {
                    resDiv.innerText = "Por favor, preencha todos os campos.";
                    return;
                }
                
                resDiv.style.color = "white";
                resDiv.innerText = "Conectando ao gateway bancário...";
                
                try {
                    const response = await fetch(`/gerar-pix?email=${email}&quantidade=${qtd}`, { method: 'POST' });
                    const data = await response.json();
                    
                    if(data.qr_code_pix) {
                        resDiv.innerHTML = `
                            <p style="color: #38bdf8; margin-bottom: 5px; font-weight: bold;">Copie o código PIX abaixo:</p>
                            <textarea readonly onclick="this.select()">${data.qr_code_pix}</textarea>
                            <p style="color: #94a3b8; margin-top: 15px; font-size: 12px;">O sistema identificará o pagamento automaticamente.</p>
                        `;
                    } else {
                        resDiv.innerHTML = `<span style="color: #ef4444;">Erro ao gerar cobrança. Verifique as credenciais.</span>`;
                    }
                } catch(e) {
                    resDiv.innerHTML = `<span style="color: #ef4444;">Erro de conexão com o servidor.</span>`;
                }
            }
        </script>
    </body>
    </html>
    """
    return html

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
    return {"erro": "Falha ao gerar cobrança"}

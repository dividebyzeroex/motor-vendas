from fastapi import FastAPI, Request
import mercadopago
import os

app = FastAPI(title="Motor de Automação")

# O sistema puxará a chave que você colocará lá no Render
TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")
sdk = mercadopago.SDK(TOKEN)

@app.get("/")
def painel_status():
    return {"status": "Servidor Operacional", "modulo_vendas": "Ativo"}

@app.post("/gerar-pix")
async def gerar_pix(email: str, quantidade: int):
    valor = quantidade * 15.00
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

import json
import smtplib
import requests
from email.message import EmailMessage
import os
from dotenv import load_dotenv
import random
import string

# Carregar variáveis de ambiente
load_dotenv(dotenv_path="config.env")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
BITLY_TOKEN = os.getenv("BITLY_TOKEN")
DOMINIO = os.getenv("DOMINIO")  # exemplo: http://teu-ip-publico:50000

FICHEIRO_DADOS = "dados_colaboradores.json"

def gerar_token(tamanho=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=tamanho))

def encurtar_link(url):
    headers = {
        "Authorization": f"Bearer {BITLY_TOKEN}",
        "Content-Type": "application/json"
    }
    data = { "long_url": url }
    res = requests.post("https://api-ssl.bitly.com/v4/shorten", headers=headers, json=data)

    if res.status_code == 200:
        return res.json()["link"]
    else:
        print("Erro ao encurtar link:", res.text)
        return url  # fallback para o original

def enviar_emails_simulacao():
    with open(FICHEIRO_DADOS, "r") as f:
        dados = json.load(f)

    for email, info in dados["colaboradores"].items():
        token = gerar_token()
        info["token"] = token

        link_phishing = f"{DOMINIO}/phish?token={token}"
        link_encurtado = encurtar_link(link_phishing)

        msg = EmailMessage()
        msg["Subject"] = "Agendamento de reunião com Direção"
        msg["From"] = EMAIL_USER
        msg["To"] = email

        msg.set_content(f"""
Olá,

Para agendar a sua próxima reunião com a Direção, por favor utilize o seguinte link:

👉 {link_encurtado}

Com os melhores cumprimentos,  
Recursos Humanos
        """)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
            print(f"📨 E-mail enviado para {email}")

        # Guardar os novos tokens
        with open(FICHEIRO_DADOS, "w") as f_out:
            json.dump(dados, f_out, indent=2)

    print("Todos os e-mails foram enviados com sucesso.")

if __name__ == "__main__":
    enviar_emails_simulacao()

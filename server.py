from flask import Flask, request
import json
from email.message import EmailMessage
import smtplib
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="config.env")

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

app = Flask(__name__)


@app.route('/phish')
def phishing_sim():
    token = request.args.get('token')

    with open('dados_colaboradores.json', 'r') as f:
        dados = json.load(f)

    for email, info in dados["colaboradores"].items():
        if info.get("token") == token:
            print(info.get("superior"))
            info["falhas"] += 1
            enviar_feedback(info["superior"], email, info["falhas"])

            with open('dados_colaboradores.json', 'w') as f_out:
                json.dump(dados, f_out, indent=2)

            return f"Olá {email}, foste apanhado num teste de segurança. Falhas: {info['falhas']}"

    return "Token inválido ou expirado."


def enviar_feedback(superior, colaborador, falhas):
    msg = EmailMessage()
    msg["Subject"] = "Falha de segurança do colaborador"
    msg["From"] = "security@empresa.pt"
    msg["To"] = superior

    texto = f"O colaborador {colaborador} caiu num teste de phishing.\nTotal de falhas: {falhas}"
    if falhas >= 2:
        texto += "\nDeve agendar sessão de formação obrigatória."

    msg.set_content(texto)

    # Enviar via Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_USER, EMAIL_PASS)  # substitui pela tua senha ou app password
        smtp.send_message(msg)

    print("Email enviado")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


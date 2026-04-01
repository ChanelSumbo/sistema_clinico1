# ==========================================
# APP.PY - SISTEMA DE MALÁRIA (FINAL PROFISSIONAL)
# ==========================================

from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from fuzzy import calcular_risco
from database import conectar
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
from datetime import datetime, timedelta



# ==========================================
# CONFIGURAÇÃO
# ==========================================
app = Flask(__name__)
app.secret_key = "segredo_super_seguro"

BASE_URL = "https://sistema-clinico1.onrender.com"

EMAIL_USER = "channelsumbo@gmail.com"
EMAIL_PASS = "ucmxhiplicbqtsad"  # senha app

# ==========================================
# LOGIN OBRIGATÓRIO
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================
# 📧 EMAIL (CORRIGIDO)
# ==========================================
def enviar_email_link(destino, link):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_USER
        msg["To"] = destino
        msg["Subject"] = "🔐 Recuperação de Senha"

        corpo = f"""
        Clique no link para redefinir sua senha:

        {link}

        Expira em 15 minutos.
        """

        msg.attach(MIMEText(corpo, "plain"))

        # 🔥 CORREÇÃO IMPORTANTE
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.ehlo()
            servidor.starttls()
            servidor.ehlo()
            servidor.login(EMAIL_USER, EMAIL_PASS)
            servidor.sendmail(EMAIL_USER, destino, msg.as_string())

        print("✅ EMAIL ENVIADO COM SUCESSO")
        return True

    except Exception as e:
        print("❌ ERRO AO ENVIAR EMAIL:", e)
        return False

# ==========================================
# LOGIN
# ==========================================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        pw = request.form.get("password")

        if not email or not pw:
            flash("Preencha todos os campos", "warning")
            return render_template("login.html")

        db = conectar()
        cursor = db.cursor(buffered=True)

        cursor.execute(
            "SELECT * FROM usuarios WHERE email=%s AND password=%s",
            (email, pw)
        )

        user = cursor.fetchone()

        if user:
            session["user"] = email
            return redirect(url_for("menu"))
        else:
            flash("Email ou senha inválidos", "danger")

    return render_template("login.html")

# ==========================================
# MENU
# ==========================================
@app.route("/menu")
@login_required
def menu():
    return render_template("menu.html")

# ==========================================
# RECUPERAR SENHA
# ==========================================
@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    if request.method == "POST":

        email = request.form.get("email")

        if not email:
            flash("Digite o email", "warning")
            return render_template("recuperar.html")

        try:
            db = conectar()
            cursor = db.cursor(buffered=True)

            cursor.execute("SELECT * FROM usuarios WHERE email=%s", (email,))
            user = cursor.fetchone()

            if not user:
                flash("Email não encontrado", "danger")
                return render_template("recuperar.html")

            token = str(uuid.uuid4())
            expira = datetime.now() + timedelta(minutes=15)

            cursor.execute(
                "INSERT INTO password_resets (email, token, expira) VALUES (%s,%s,%s)",
                (email, token, expira)
            )
            db.commit()

            link = f"{BASE_URL}/resetar/{token}"

            enviado = enviar_email_link(email, link)

            if enviado:
                flash("Link enviado para o email!", "success")
            else:
                flash("Erro ao enviar email (ver console Render)", "danger")

            return redirect(url_for("login"))

        except Exception as e:
            print("❌ ERRO GERAL:", e)
            flash("Erro interno no servidor", "danger")
            return redirect(url_for("login"))

    return render_template("recuperar.html")

# ==========================================
# RESETAR SENHA
# ==========================================
@app.route("/resetar/<token>", methods=["GET", "POST"])
def resetar(token):

    db = conectar()
    cursor = db.cursor(buffered=True)

    cursor.execute(
        "SELECT * FROM password_resets WHERE token=%s",
        (token,)
    )
    data = cursor.fetchone()

    if not data:
        return "Token inválido"

    if datetime.now() > data[2]:
        return "Token expirado"

    if request.method == "POST":
        nova = request.form.get("senha")

        cursor.execute(
            "UPDATE usuarios SET password=%s WHERE email=%s",
            (nova, data[1])
        )

        cursor.execute(
            "DELETE FROM password_resets WHERE token=%s",
            (token,)
        )

        db.commit()

        flash("Senha alterada com sucesso!", "success")
        return redirect(url_for("login"))

    return render_template("resetar.html")

# ==========================================
# LOGOUT
# ==========================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==========================================
# EXECUÇÃO
# ==========================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
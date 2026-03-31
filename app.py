# ==========================================
# SISTEMA CLÍNICO DE MALÁRIA
# Flask + Fuzzy + MySQL
# Render Ready
# ==========================================

from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from database import conectar
from fuzzy import calcular_risco
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "segredo_super")

# ==========================================
# LOGIN REQUIRED
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ==========================================
# LOGIN
# ==========================================
@app.route("/", methods=["GET","POST"])
def login():

    if request.method=="POST":

        user=request.form["username"]
        pw=request.form["password"]

        db=conectar()
        cursor=db.cursor()

        cursor.execute("SELECT * FROM usuarios WHERE username=%s",(user,))
        usuario=cursor.fetchone()

        if usuario and check_password_hash(usuario[2],pw):
            session["user"]=user
            return redirect(url_for("menu"))

        flash("Login inválido","danger")

    return render_template("login.html")


# ==========================================
# REGISTRAR
# ==========================================
@app.route("/registrar",methods=["GET","POST"])
def registrar():

    if request.method=="POST":

        user=request.form["username"]
        senha_hash=generate_password_hash(request.form["password"])

        db=conectar()
        cursor=db.cursor()

        cursor.execute(
            "INSERT INTO usuarios(username,password) VALUES(%s,%s)",
            (user,senha_hash)
        )
        db.commit()

        flash("Usuário criado!","success")
        return redirect(url_for("login"))

    return render_template("registrar.html")


# ==========================================
# MENU
# ==========================================
@app.route("/menu")
@login_required
def menu():
    return render_template("menu.html")


# ==========================================
# FORMULÁRIO
# ==========================================
@app.route("/home")
@login_required
def home():
    return render_template("form.html")


# ==========================================
# DIAGNÓSTICO
# ==========================================
@app.route("/diagnostico",methods=["POST"])
@login_required
def diagnostico():

    febre=float(request.form["febre"])
    fadiga=float(request.form["fadiga"])
    anemia=float(request.form["anemia"])

    latitude=request.form.get("latitude",0)
    longitude=request.form.get("longitude",0)

    risco=round(calcular_risco(febre,fadiga,anemia),2)

    if risco<40:
        nivel="Baixo"
    elif risco<70:
        nivel="Moderado"
    else:
        nivel="Alto"

    db=conectar()
    cursor=db.cursor()

    cursor.execute("""
        INSERT INTO diagnosticos
        (febre,fadiga,anemia,risco,nivel,latitude,longitude)
        VALUES(%s,%s,%s,%s,%s,%s,%s)
    """,(febre,fadiga,anemia,risco,nivel,latitude,longitude))

    db.commit()

    return render_template("resultado.html",risco=risco,nivel=nivel)


# ==========================================
# RELATÓRIO
# ==========================================
@app.route("/relatorio")
@login_required
def relatorio():

    db=conectar()
    cursor=db.cursor()

    cursor.execute("SELECT * FROM diagnosticos ORDER BY id DESC")
    dados=cursor.fetchall()

    return render_template("relatorio.html",dados=dados)


# ==========================================
# DASHBOARD
# ==========================================
@app.route("/dashboard")
@login_required
def dashboard():

    db=conectar()
    cursor=db.cursor()

    cursor.execute("SELECT COUNT(*) FROM diagnosticos WHERE nivel='Baixo'")
    baixo=cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM diagnosticos WHERE nivel='Moderado'")
    moderado=cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM diagnosticos WHERE nivel='Alto'")
    alto=cursor.fetchone()[0]

    total=baixo+moderado+alto

    if total>0:
        p_baixo=round((baixo/total)*100,1)
        p_moderado=round((moderado/total)*100,1)
        p_alto=round((alto/total)*100,1)
    else:
        p_baixo=p_moderado=p_alto=0

    return render_template(
        "dashboard.html",
        baixo=baixo,
        moderado=moderado,
        alto=alto,
        p_baixo=p_baixo,
        p_moderado=p_moderado,
        p_alto=p_alto
    )


# ==========================================
# LOGOUT
# ==========================================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ==========================================
# EXECUÇÃO LOCAL
# ==========================================
if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)
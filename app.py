# ==========================================
# APP.PY - SISTEMA HOSPITALAR DE MALÁRIA
# Flask + Fuzzy + MySQL
# ==========================================

from flask import Flask, render_template, request, redirect, session, url_for, flash
from functools import wraps
from fuzzy import calcular_risco
from database import conectar

# ==========================================
# CONFIGURAÇÃO DO APP
# ==========================================
app = Flask(__name__)
app.secret_key = 'segredo'


# ==========================================
# 🔐 FUNÇÃO DE PROTEÇÃO (LOGIN OBRIGATÓRIO)
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# LOGIN
# ==========================================
@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']

        db = conectar()
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM usuarios WHERE username=%s AND password=%s",
            (user, pw)
        )

        res = cursor.fetchone()

        if res:
            session['user'] = user
            return redirect(url_for('menu'))
        else:
            flash("Usuário ou senha inválidos", "danger")

    return render_template('login.html')


# ==========================================
# MENU PRINCIPAL
# ==========================================
@app.route('/menu')
@login_required
def menu():
    return render_template('menu.html')


# ==========================================
# FORMULÁRIO DE DIAGNÓSTICO
# ==========================================
@app.route('/home')
@login_required
def home():
    return render_template('form.html')


# ==========================================
# DIAGNÓSTICO (COM GPS)
# ==========================================
@app.route('/diagnostico', methods=['POST'])
@login_required
def diagnostico():

    # Dados do formulário
    f = float(request.form['febre'])
    fa = float(request.form['fadiga'])
    a = float(request.form['anemia'])

    # GPS (opcional)
    lat = request.form.get('latitude') or 0
    lon = request.form.get('longitude') or 0

    # Calcular risco
    risco = round(calcular_risco(f, fa, a), 2)

    # Classificação
    if risco < 40:
        nivel = 'Baixo'
    elif risco < 70:
        nivel = 'Moderado'
    else:
        nivel = 'Alto'

    # Salvar no banco
    db = conectar()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO diagnosticos 
        (febre, fadiga, anemia, risco, nivel, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (f, fa, a, risco, nivel, lat, lon))

    db.commit()

    return render_template('resultado.html', risco=risco, nivel=nivel)


# ==========================================
# RELATÓRIO
# ==========================================
@app.route('/relatorio')
@login_required
def relatorio():

    db = conectar()
    cursor = db.cursor()

    cursor.execute("SELECT * FROM diagnosticos ORDER BY id DESC")
    dados = cursor.fetchall()

    return render_template('relatorio.html', dados=dados)


# ==========================================
# APAGAR REGISTRO
# ==========================================
@app.route('/apagar/<int:id>', methods=['POST'])
@login_required
def apagar(id):

    db = conectar()
    cursor = db.cursor()

    cursor.execute("DELETE FROM diagnosticos WHERE id=%s", (id,))
    db.commit()

    return redirect(url_for('relatorio'))


# ==========================================
# DASHBOARD (COM CONTAGEM + %)
# ==========================================
@app.route('/dashboard')
@login_required
def dashboard():

    db = conectar()
    cursor = db.cursor()

    # Corrigir registros sem nível
    cursor.execute("""
        UPDATE diagnosticos 
        SET nivel = 
        CASE 
            WHEN risco < 40 THEN 'Baixo'
            WHEN risco < 70 THEN 'Moderado'
            ELSE 'Alto'
        END
        WHERE nivel IS NULL
    """)
    db.commit()

    # Contagem
    cursor.execute("SELECT COUNT(*) FROM diagnosticos WHERE nivel='Baixo'")
    baixo = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM diagnosticos WHERE nivel='Moderado'")
    moderado = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM diagnosticos WHERE nivel='Alto'")
    alto = cursor.fetchone()[0]

    total = baixo + moderado + alto

    # Percentagens
    if total > 0:
        p_baixo = round((baixo / total) * 100, 1)
        p_moderado = round((moderado / total) * 100, 1)
        p_alto = round((alto / total) * 100, 1)
    else:
        p_baixo = p_moderado = p_alto = 0

    return render_template(
        'dashboard.html',
        baixo=baixo,
        moderado=moderado,
        alto=alto,
        p_baixo=p_baixo,
        p_moderado=p_moderado,
        p_alto=p_alto
    )


# ==========================================
# 🌍 MAPA (GPS)
# ==========================================
@app.route('/mapa')
@login_required
def mapa():

    db = conectar()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT latitude, longitude, nivel, data_registro 
        FROM diagnosticos
    """)

    dados = cursor.fetchall()

    return render_template('mapa.html', dados=dados)



# ==========================================
# REGISTRAR USUÁRIO
# ==========================================
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():

    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']

        db = conectar()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO usuarios (username, password) VALUES (%s, %s)",
            (user, pw)
        )
        db.commit()

        return redirect('/')

    return render_template('registrar.html')


# ==========================================
# RECUPERAR SENHA
# ==========================================
@app.route('/recuperar', methods=['GET', 'POST'])
def recuperar():

    if request.method == 'POST':
        user = request.form['username']
        nova = request.form['nova_senha']

        db = conectar()
        cursor = db.cursor()

        cursor.execute(
            "UPDATE usuarios SET password=%s WHERE username=%s",
            (nova, user)
        )
        db.commit()

        flash("Senha atualizada com sucesso!", "success")
        return redirect('/')

    return render_template('recuperar.html')


# ==========================================
# LOGOUT
# ==========================================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ==========================================
# EXECUTAR SISTEMA
# ==========================================
if __name__ == '__main__':
    import os

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
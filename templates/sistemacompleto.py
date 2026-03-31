# =============================================
# SISTEMA COMPLETO - DASHBOARD MALÁRIA (TCC)
# Flask + Bootstrap + Chart.js + Fuzzy
# =============================================

from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

app = Flask(__name__)
app.secret_key = '12345'

# =============================================
# SISTEMA FUZZY
# =============================================

febre = ctrl.Antecedent(np.arange(0, 11, 1), 'febre')
fadiga = ctrl.Antecedent(np.arange(0, 11, 1), 'fadiga')
anemia = ctrl.Antecedent(np.arange(0, 11, 1), 'anemia')
risco = ctrl.Consequent(np.arange(0, 101, 1), 'risco')

# Funções fuzzy
for var in [febre, fadiga, anemia]:
    var['baixa'] = fuzz.trimf(var.universe, [0, 2, 4])
    var['moderada'] = fuzz.trimf(var.universe, [3, 5, 7])
    var['alta'] = fuzz.trimf(var.universe, [6, 8, 10])

risco['baixo'] = fuzz.trimf(risco.universe, [0, 25, 50])
risco['moderado'] = fuzz.trimf(risco.universe, [25, 50, 75])
risco['alto'] = fuzz.trimf(risco.universe, [50, 75, 100])

regras = []
for f in ['baixa','moderada','alta']:
    for fa in ['baixa','moderada','alta']:
        for a in ['baixa','moderada','alta']:
            if a == 'alta' or (f == 'alta' and fa == 'alta'):
                r = 'alto'
            elif f == 'moderada' or fa == 'moderada':
                r = 'moderado'
            else:
                r = 'baixo'

            regras.append(ctrl.Rule(febre[f] & fadiga[fa] & anemia[a], risco[r]))

sistema = ctrl.ControlSystem(regras)
simulador = ctrl.ControlSystemSimulation(sistema)

# =============================================
# BASE DE DADOS SIMPLES (LISTA)
# =============================================

dados = []

# =============================================
# FUNÇÃO FUZZY
# =============================================

def calcular_risco(f, fa, a):
    simulador.input['febre'] = f
    simulador.input['fadiga'] = fa
    simulador.input['anemia'] = a
    simulador.compute()
    return simulador.output['risco']

# =============================================
# ROTAS
# =============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    f = float(request.form['febre'])
    fa = float(request.form['fadiga'])
    a = float(request.form['anemia'])

    r = calcular_risco(f, fa, a)

    if r < 40:
        nivel = 'Baixo'
    elif r < 70:
        nivel = 'Moderado'
    else:
        nivel = 'Alto'

    dados.append(nivel)

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    baixo = dados.count('Baixo')
    moderado = dados.count('Moderado')
    alto = dados.count('Alto')

    return render_template('dashboard.html', baixo=baixo, moderado=moderado, alto=alto)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# =============================================
# EXECUTAR
# =============================================

if __name__ == '__main__':
    app.run(debug=True)


# =============================================
# TEMPLATES (criar pasta 'templates')
# =============================================

# index.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>Sistema Malária</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container mt-5">
    <h2 class="text-center">Sistema de Diagnóstico</h2>

    <form method="POST" action="/calcular">
        <input class="form-control mt-3" name="febre" placeholder="Febre (0-10)" required>
        <input class="form-control mt-3" name="fadiga" placeholder="Fadiga (0-10)" required>
        <input class="form-control mt-3" name="anemia" placeholder="Anemia (0-10)" required>

        <button class="btn btn-primary mt-3 w-100">Calcular</button>
    </form>
</div>
</body>
</html>
"""

# dashboard.html
"""
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
<div class="container mt-5">
    <h2 class="text-center">Dashboard</h2>

    <canvas id="grafico"></canvas>

    <a href="/logout" class="btn btn-danger mt-4">Sair</a>
</div>

<script>
const ctx = document.getElementById('grafico');

new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Baixo', 'Moderado', 'Alto'],
        datasets: [{
            label: 'Casos',
            data: [{{baixo}}, {{moderado}}, {{alto}}],
            backgroundColor: [
                'green',
                'yellow',
                'red'
            ]
        }]
    }
});
</script>

</body>
</html>
"""

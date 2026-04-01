# ==========================================
# SISTEMA FUZZY - DIAGNÓSTICO DE MALÁRIA
# ==========================================

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


# ==========================================
# VARIÁVEIS DE ENTRADA (0 a 10)
# ==========================================

febre = ctrl.Antecedent(np.arange(0, 11, 1), 'febre')
fadiga = ctrl.Antecedent(np.arange(0, 11, 1), 'fadiga')
anemia = ctrl.Antecedent(np.arange(0, 11, 1), 'anemia')


# ==========================================
# VARIÁVEL DE SAÍDA (0 a 100)
# ==========================================

risco = ctrl.Consequent(np.arange(0, 101, 1), 'risco')


# ==========================================
# FUNÇÕES DE PERTINÊNCIA
# ==========================================

# FEBRE
febre['baixa'] = fuzz.trimf(febre.universe, [0, 2, 4])
febre['moderada'] = fuzz.trimf(febre.universe, [3, 5, 7])
febre['alta'] = fuzz.trimf(febre.universe, [6, 8, 10])

# FADIGA
fadiga['baixa'] = fuzz.trimf(fadiga.universe, [0, 2, 4])
fadiga['moderada'] = fuzz.trimf(fadiga.universe, [3, 5, 7])
fadiga['alta'] = fuzz.trimf(fadiga.universe, [6, 8, 10])

# ANEMIA
anemia['baixa'] = fuzz.trimf(anemia.universe, [0, 2, 4])
anemia['moderada'] = fuzz.trimf(anemia.universe, [3, 5, 7])
anemia['alta'] = fuzz.trimf(anemia.universe, [6, 8, 10])

# SAÍDA (RISCO)
risco['baixo'] = fuzz.trimf(risco.universe, [0, 25, 50])
risco['moderado'] = fuzz.trimf(risco.universe, [25, 50, 75])
risco['alto'] = fuzz.trimf(risco.universe, [50, 75, 100])


# ==========================================
# REGRAS FUZZY AUTOMÁTICAS
# ==========================================

regras = []

for f in ['baixa', 'moderada', 'alta']:
    for fa in ['baixa', 'moderada', 'alta']:
        for a in ['baixa', 'moderada', 'alta']:

            # Lógica médica
            if a == 'alta':
                r = 'alto'
            elif f == 'alta' and fa == 'alta':
                r = 'alto'
            elif f == 'moderada' or fa == 'moderada':
                r = 'moderado'
            else:
                r = 'baixo'

            regra = ctrl.Rule(
                febre[f] & fadiga[fa] & anemia[a],
                risco[r]
            )

            regras.append(regra)


# ==========================================
# CRIAR SISTEMA
# ==========================================

sistema = ctrl.ControlSystem(regras)
simulador = ctrl.ControlSystemSimulation(sistema)


# ==========================================
# FUNÇÃO PRINCIPAL (USADA NO APP.PY)
# ==========================================

def calcular_risco(f, fa, a):
    """
    Calcula o risco de malária

    Parâmetros:
    f  -> febre (0 a 10)
    fa -> fadiga (0 a 10)
    a  -> anemia (0 a 10)

    Retorna:
    risco (0 a 100)
    """

    simulador.input['febre'] = f
    simulador.input['fadiga'] = fa
    simulador.input['anemia'] = a

    simulador.compute()

    return simulador.output['risco']


# ==========================================
# TESTE (OPCIONAL)
# ==========================================

if __name__ == "__main__":
    teste = calcular_risco(8, 7, 6)
    print(f"Risco calculado: {teste:.2f}%")
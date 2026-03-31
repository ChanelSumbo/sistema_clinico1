# Importação das bibliotecas necessárias
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# ===============================
# DEFINIÇÃO DAS VARIÁVEIS DE ENTRADA
# ===============================
febre = ctrl.Antecedent(np.arange(0, 11, 1), 'febre')
fadiga = ctrl.Antecedent(np.arange(0, 11, 1), 'fadiga')
anemia = ctrl.Antecedent(np.arange(0, 11, 1), 'anemia')

# ===============================
# VARIÁVEL DE SAÍDA
# ===============================
risco = ctrl.Consequent(np.arange(0, 101, 1), 'risco')

# ===============================
# FUNÇÕES DE PERTINÊNCIA (Fuzzy)
# ===============================
febre['baixa'] = fuzz.trimf(febre.universe, [0, 2, 4])
febre['moderada'] = fuzz.trimf(febre.universe, [3, 5, 7])
febre['alta'] = fuzz.trimf(febre.universe, [6, 8, 10])

fadiga['baixa'] = fuzz.trimf(fadiga.universe, [0, 2, 4])
fadiga['moderada'] = fuzz.trimf(fadiga.universe, [3, 5, 7])
fadiga['alta'] = fuzz.trimf(fadiga.universe, [6, 8, 10])

anemia['baixa'] = fuzz.trimf(anemia.universe, [0, 2, 4])
anemia['moderada'] = fuzz.trimf(anemia.universe, [3, 5, 7])
anemia['alta'] = fuzz.trimf(anemia.universe, [6, 8, 10])

# Saída
risco['baixo'] = fuzz.trimf(risco.universe, [0, 25, 50])
risco['moderado'] = fuzz.trimf(risco.universe, [25, 50, 75])
risco['alto'] = fuzz.trimf(risco.universe, [50, 75, 100])

# ===============================
# REGRAS DO SISTEMA Gerar regras manuais 
# ===============================
r1 = ctrl.Rule(febre['alta'] & fadiga['alta'], risco['alto'])
r2 = ctrl.Rule(anemia['alta'], risco['alto'])
r3 = ctrl.Rule(febre['moderada'] & fadiga['alta'], risco['moderado'])
r4 = ctrl.Rule(febre['baixa'] & fadiga['baixa'] & anemia['baixa'], risco['baixo'])
r5 = ctrl.Rule(febre['moderada'] & fadiga['moderada'] & anemia['moderada'], risco['moderado'])  
# ===============================
# quando quiser a crescentar REGRAS nO SISTEMA deve ser aqui acima da escrita por ex. o pro vai ser R6
# ===============================

# Criar sistema de controle
sistema = ctrl.ControlSystem([r1, r2, r3, r4, r5])
simulador = ctrl.ControlSystemSimulation(sistema)   
# ===============================
# quando acrecentares na regra tambem tens que a crescentar a qui por ex. o proximo é R6
# ===============================

# ===============================
# FUNÇÃO PARA CALCULAR RISCO
# ===============================
def calcular_risco(f, fa, a):
    simulador.input['febre'] = f
    simulador.input['fadiga'] = fa
    simulador.input['anemia'] = a
    simulador.compute()
    return simulador.output['risco']
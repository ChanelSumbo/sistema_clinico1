# ==========================================
# CONEXÃO COM MYSQL
# ==========================================

import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # coloca tua senha se tiver
        database="sistema_clinico"
    )
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'mizu_polimix_2026'

def conectar():
    caminho_banco = os.path.join(os.path.dirname(__file__), "banco_mizu_final.db")
    conn = sqlite3.connect(caminho_banco)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    u = request.form.get('usuario', '').lower().strip()
    s = request.form.get('senha', '')
    if u == 'julia.silva' and s == '2318':
        session['perfil'] = 'ADMINISTRADOR'
        session['usuario_nome'] = 'Júlia Rebeca'
        return redirect(url_for('ver_ferramentas'))
    
    conn = conectar()
    user = conn.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (u, s)).fetchone()
    conn.close()
    if user:
        session['perfil'] = user['perfil'].upper().strip()
        session['usuario_nome'] = user['nome']
        return redirect(url_for('ver_ferramentas'))
    flash('Usuário ou senha incorretos.')
    return redirect(url_for('index'))

@app.route('/ver_ferramentas')
def ver_ferramentas():
    if 'perfil' not in session: return redirect(url_for('index'))
    conn = conectar()
    itens = conn.execute("SELECT * FROM itens ORDER BY codigo ASC").fetchall()
    conn.close()
    template = 'verdisponiveisadm.html' if session.get('perfil') == 'ADMINISTRADOR' else 'ver_ferramentas.html'
    return render_template(template, ferramentas=itens, titulo="Inventário Geral")

@app.route('/manutencao')
def manutencao():
    if 'perfil' not in session: return redirect(url_for('index'))
    return render_template('gestaomanutencao.html')

@app.route('/nova_remessa')
def nova_remessa():
    return redirect(url_for('manutencao'))

@app.route('/ferramentas_disponiveis')
def ferramentas_disponiveis():
    if 'perfil' not in session: return redirect(url_for('index'))
    conn = conectar()
    itens = conn.execute("SELECT * FROM itens ORDER BY status = 'Disponível'").fetchall()
    conn.close()
    return render_template('ver_ferramentas.html', ferramentas=itens)

@app.route('/cadastrar')
def cadastrar(): return render_template('cadastro.html')

@app.route('/solicitar_acesso')
def solicitar_acesso(): return render_template('solicitar_acesso.html')

@app.route('/enviar_formulario')
def enviar_formulario(): return render_template('formulario.html')

@app.route('/perfil_adm')
def perfil_adm():
    usuario_dados = {'nome': session.get('usuario_nome'), 'perfil': session.get('perfil')}
    return render_template('perfiladm.html', usuario=usuario_dados)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
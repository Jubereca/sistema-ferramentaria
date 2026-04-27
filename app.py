from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'mz$9#kLpQ2!vXwR7@nJcE5&hYtBuA3*sFdG8^iOz'
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'julia.silva@mizu.com.br'
app.config['MAIL_PASSWORD'] = 'Juh2318.'
app.config['MAIL_DEFAULT_SENDER'] = 'julia.silva@mizu.com.br'
app.config['MAIL_ASCII_ATTACHMENTS'] = False
mail = Mail(app)

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
    u = request.form.get('usuario', '').strip()
    s = request.form.get('senha', '').strip()
    if '@' not in u:
        u = u + '@mizu.com.br'
    u = u.lower()

    conn = conectar()
    user = conn.execute(
        "SELECT * FROM usuarios WHERE (email = ? OR email = ?) AND status IN ('Ativo', 'Aprovado')",
        (u, u.split('@')[0])
    ).fetchone()
    conn.close()

    if user and check_password_hash(user['senha'], s):
        session['perfil'] = user['perfil'].upper().strip()
        session['nome'] = user['nome']
        session['usuario_nome'] = user['nome']
        session['usuario_id'] = user['id']
        session['usuario_email'] = user['email']
        if session['perfil'] == 'ADMINISTRADOR':
            return redirect(url_for('ver_ferramentas'))
        return redirect(url_for('dashboard_funcionario'))

    if u in ('julia.silva@mizu.com.br', 'julia.silva') and s == '2318':
        session['perfil'] = 'ADMINISTRADOR'
        session['nome'] = 'Julia Rebeca'
        session['usuario_nome'] = 'Julia Rebeca'
        session['usuario_id'] = None
        session['usuario_email'] = 'julia.silva@mizu.com.br'
        return redirect(url_for('ver_ferramentas'))

    flash('Usuario ou senha incorretos.')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard_funcionario')
def dashboard_funcionario():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    busca = request.args.get('busca', '')
    conn = conectar()
    if busca:
        itens = conn.execute("SELECT * FROM itens WHERE nome LIKE ? ORDER BY codigo ASC", ('%'+busca+'%',)).fetchall()
    else:
        itens = conn.execute("SELECT * FROM itens ORDER BY codigo ASC").fetchall()
    conn.close()
    return render_template('dashboard_funcionario.html', ferramentas=itens)

@app.route('/ver_ferramentas')
def ver_ferramentas():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    busca = request.args.get('busca', '')
    conn = conectar()
    if busca:
        itens = conn.execute("SELECT * FROM itens WHERE nome LIKE ? ORDER BY codigo ASC", ('%' + busca + '%',)).fetchall()
    else:
        itens = conn.execute("SELECT * FROM itens ORDER BY codigo ASC").fetchall()
    conn.close()
    if session.get('perfil') == 'ADMINISTRADOR':
        return render_template('inventario_adm.html', ferramentas=itens)
    return render_template('ver_ferramentas_func.html', ferramentas=itens)

@app.route('/ferramentas_disponiveis')
def ferramentas_disponiveis():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    busca = request.args.get('busca', '')
    conn = conectar()
    if busca:
        itens = conn.execute("SELECT * FROM itens WHERE nome LIKE ? ORDER BY codigo ASC", ('%' + busca + '%',)).fetchall()
    else:
        itens = conn.execute("SELECT * FROM itens ORDER BY codigo ASC").fetchall()

    alertas = []
    if session.get('perfil') != 'ADMINISTRADOR':
        usuario_id = session.get('usuario_id')
        agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            vencidas = conn.execute("""
                SELECT itens.nome, itens.codigo, mov.prazo
                FROM itens
                JOIN movimentacao mov ON mov.codigo_ferramenta = itens.codigo
                WHERE itens.usuario_id = ?
                AND itens.status IN ('Em Uso', 'Reservado')
                AND REPLACE(mov.prazo, 'T', ' ') < ?
                AND mov.status IN ('Em Uso', 'Reservado')
                AND mov.id = (
                    SELECT id FROM movimentacao m2
                    WHERE m2.codigo_ferramenta = itens.codigo
                    ORDER BY m2.id DESC LIMIT 1
                )
            """, (usuario_id, agora)).fetchall()
            alertas = vencidas
        except Exception as e:
            print(f"Erro ao buscar alertas: {e}")
            alertas = []

    conn.close()
    if session.get('perfil') == 'ADMINISTRADOR':
        return render_template('ver_ferramentas_adm.html', ferramentas=itens)
    return render_template('ver_ferramentas_func.html', ferramentas=itens, alertas=alertas)

@app.route('/ferramentas_indisponiveis')
def ferramentas_indisponiveis():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    itens = conn.execute("SELECT * FROM itens WHERE status != 'Disponível' ORDER BY codigo ASC").fetchall()
    conn.close()
    return render_template('indisponiveis.html', ferramentas=itens)

@app.route('/uso_ferramentas')
def ferramentas_em_uso():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    if session.get('perfil') != 'ADMINISTRADOR':
        return redirect(url_for('dashboard_funcionario'))
    conn = conectar()
    try:
        itens = conn.execute("""
            SELECT
                itens.id,
                itens.codigo,
                itens.nome,
                itens.status,
                mov.quantidade,
                mov.responsavel as funcionario,
                mov.data_hora as data_saida,
                mov.prazo as prazo_devolucao,
                u.matricula
            FROM itens
            LEFT JOIN movimentacao mov ON mov.codigo_ferramenta = itens.codigo
                AND mov.id = (
                    SELECT id FROM movimentacao m2
                    WHERE m2.codigo_ferramenta = itens.codigo
                    ORDER BY m2.id DESC LIMIT 1
                )
            LEFT JOIN usuarios u ON u.nome = mov.responsavel
            WHERE itens.status IN ('Em Uso', 'Reservado')
            ORDER BY itens.status ASC, itens.codigo ASC
        """).fetchall()
    except Exception as e:
        print(f"Erro na consulta: {e}")
        itens = []
    finally:
        conn.close()
    agora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('usoferramentas.html', ferramentas=itens, agora=agora)

@app.route('/salvar_edicao_ferramenta', methods=['POST'])
def salvar_edicao_ferramenta():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    codigo      = request.form.get('codigo')
    nome        = request.form.get('nome')
    status      = request.form.get('status')
    observacoes = request.form.get('observacoes')
    conn = conectar()
    conn.execute("UPDATE itens SET nome=?, status=?, observacoes=? WHERE codigo=?", (nome, status, observacoes, codigo))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_ferramentas'))

@app.route('/excluir_ferramenta', methods=['POST'])
def excluir_ferramenta():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    codigo = request.form.get('codigo')
    conn = conectar()
    conn.execute("DELETE FROM itens WHERE codigo=?", (codigo,))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_ferramentas'))

@app.route('/devolver/<int:id>')
def devolver(id):
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    item = conn.execute("SELECT * FROM itens WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not item:
        return redirect(url_for('ferramentas_disponiveis'))
    return render_template('devolucao.html', item=item)

@app.route('/registrar_devolucao', methods=['POST'])
def registrar_devolucao():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    item_id      = request.form.get('item_id')
    codigo       = request.form.get('codigo')
    estado       = request.form.get('estado_conservacao')
    observacoes  = request.form.get('observacoes')
    usuario_id   = session.get('usuario_id')
    usuario_nome = session.get('usuario_nome')

    if estado in ('Com avarias graves', 'Inutilizável'):
        novo_status = 'Manutenção'
    else:
        novo_status = 'Disponível'

    conn = conectar()
    try:
        conn.execute("""
            UPDATE itens SET status = ?, usuario_id = NULL, reservado_ate = NULL WHERE id = ?
        """, (novo_status, item_id))
        conn.execute("""
            INSERT INTO devolucao (nome_colaborador, matricula, ferramenta, codigo_tag, quantidade, estado_conservacao, observacoes)
            VALUES (?, ?, (SELECT nome FROM itens WHERE id = ?), ?, 1, ?, ?)
        """, (usuario_nome, usuario_id, item_id, codigo, estado, observacoes))
        conn.execute("""
            UPDATE movimentacao SET status = 'Devolvido'
            WHERE codigo_ferramenta = ? AND status IN ('Em Uso', 'Reservado')
        """, (codigo,))
        item = conn.execute("SELECT nome FROM itens WHERE id = ?", (item_id,)).fetchone()
        descricao_log = f"Devolveu a ferramenta: {item['nome']} (Cód: {codigo}) — Estado: {estado}"
        conn.execute("INSERT INTO log_atividades (usuario_id, descricao) VALUES (?, ?)", (usuario_id, descricao_log))
        conn.commit()
        flash(f'Ferramenta devolvida com sucesso! Status: {novo_status}')
    except Exception as e:
        print(f"Erro ao registrar devolução: {e}")
        flash('Erro ao registrar devolução.')
    finally:
        conn.close()

    if session.get('perfil') == 'ADMINISTRADOR':
        return redirect(url_for('ferramentas_em_uso'))
    return redirect(url_for('ferramentas_disponiveis'))

@app.route('/cadastrar_uso', methods=['GET'])
def cadastrar_uso():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    codigo = request.args.get('codigo', '')
    conn = conectar()
    ferramentas = conn.execute("SELECT * FROM itens WHERE status = 'Disponível' ORDER BY nome ASC").fetchall()
    qtd_max = 1
    if codigo:
        item = conn.execute("SELECT quantidade FROM itens WHERE codigo = ?", (codigo,)).fetchone()
        if item:
            qtd_max = item['quantidade'] if item['quantidade'] else 1
    conn.close()
    return render_template('cadastrar_uso.html', ferramentas=ferramentas, qtd_max=qtd_max)

@app.route('/cadastrar_uso', methods=['POST'])
def salvar_uso():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    tipo            = request.form.get('tipo')
    nome_ferramenta = request.form.get('nome_ferramenta')
    codigo          = request.form.get('codigo_ferramenta')
    quantidade      = request.form.get('quantidade')
    data_reserva    = request.form.get('data_reserva')
    prazo           = request.form.get('prazo_devolucao')
    usuario_id      = session.get('usuario_id')
    usuario_nome    = session.get('usuario_nome')

    conn = conectar()
    try:
        if data_reserva:
            data_hora = data_reserva
        else:
            data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        status_mov = 'Em Uso' if (tipo == 'uso' or tipo == 'retirar') else 'Reservado'

        conn.execute("""
            INSERT INTO movimentacao (codigo_ferramenta, nome_ferramenta, quantidade, data_hora, prazo, status, responsavel)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (codigo, nome_ferramenta, quantidade, data_hora, prazo, status_mov, usuario_nome))

        if tipo == 'uso' or tipo == 'retirar':
            conn.execute("UPDATE itens SET status = 'Em Uso', usuario_id = ? WHERE codigo = ?", (usuario_id, codigo))
            descricao_log = f'Retirou a ferramenta: {nome_ferramenta} (Cód: {codigo})'
        else:
            conn.execute("UPDATE itens SET status = 'Reservado', usuario_id = ?, reservado_ate = ? WHERE codigo = ?", (usuario_id, prazo, codigo))
            descricao_log = f'Reservou a ferramenta: {nome_ferramenta} (Cód: {codigo})'

        conn.execute("INSERT INTO log_atividades (usuario_id, descricao) VALUES (?, ?)", (usuario_id, descricao_log))
        conn.commit()
    except Exception as e:
        print(f"Erro ao salvar uso: {e}")
    finally:
        conn.close()
    return redirect(url_for('dashboard_funcionario'))

@app.route('/cadastrar_devolucao', methods=['GET'])
def cadastrar_devolucao():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    item_id = request.args.get('id')
    conn = conectar()
    if item_id:
        item = conn.execute("SELECT * FROM itens WHERE id = ?", (item_id,)).fetchone()
        conn.close()
        return render_template('devolucao.html', item=item)
    # Se não veio com id, mostra lista das ferramentas que o funcionário tem em uso
    usuario_id = session.get('usuario_id')
    itens = conn.execute("""
        SELECT * FROM itens 
        WHERE usuario_id = ? AND status IN ('Em Uso', 'Reservado')
        ORDER BY nome ASC
    """, (usuario_id,)).fetchall()
    conn.close()
    return render_template('minhas_ferramentas.html', itens=itens)

@app.route('/perfil_adm')
def perfil_adm():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    usuario = conn.execute("SELECT * FROM usuarios WHERE nome = ?", (session.get('usuario_nome'),)).fetchone()
    conn.close()
    return render_template('perfiladm.html', usuario=usuario)

@app.route('/meu_perfil')
def meu_perfil():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    usuario = conn.execute("SELECT * FROM usuarios WHERE id = ?", (session.get('usuario_id'),)).fetchone()
    historico = conn.execute("""
        SELECT descricao, data FROM log_atividades
        WHERE usuario_id = ?
        ORDER BY data DESC
    """, (session.get('usuario_id'),)).fetchall()
    conn.close()
    return render_template('meuperfil.html', usuario=usuario, historico=historico)

@app.route('/salvar_perfil', methods=['POST'])
def salvar_perfil():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    novo_nome  = request.form.get('novo_nome')
    novo_email = request.form.get('novo_email')
    nova_senha = request.form.get('nova_senha')
    confirmar  = request.form.get('confirmar_senha')
    conn = conectar()
    try:
        if novo_nome:
            conn.execute("UPDATE usuarios SET nome = ? WHERE id = ?", (novo_nome, session.get('usuario_id')))
            session['usuario_nome'] = novo_nome
        if novo_email:
            conn.execute("UPDATE usuarios SET email = ? WHERE id = ?", (novo_email, session.get('usuario_id')))
            session['usuario_email'] = novo_email
        if nova_senha and nova_senha == confirmar:
            conn.execute("UPDATE usuarios SET senha = ? WHERE id = ?", (generate_password_hash(nova_senha), session.get('usuario_id')))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for('dashboard_funcionario'))

@app.route('/manutencao')
def manutencao():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    remessas = conn.execute("SELECT * FROM manutencao_remessas ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('gestaomanutencao.html', remessas=remessas)

@app.route('/nova_remessa', methods=['POST'])
def nova_remessa():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    tag            = request.form.get('tag')
    descricao      = request.form.get('descricao')
    qtd            = request.form.get('qtd')
    modelo         = request.form.get('modelo')
    fabricante     = request.form.get('fabricante')
    data_envio     = request.form.get('data_envio')
    resp_manutencao = request.form.get('resp_manutencao')
    nota_origem    = request.form.get('nota_origem')
    nota_envio     = request.form.get('nota_envio')
    sc             = request.form.get('sc')
    responsavel    = request.form.get('responsavel')
    status         = request.form.get('status')
    observacoes    = request.form.get('observacoes')
    conn = conectar()
    try:
        conn.execute("""
            INSERT INTO manutencao_remessas 
            (tag, descricao, qtd, modelo, fabricante, data_envio, resp_manutencao, nota_origem, nota_envio, sc, responsavel, status, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (tag, descricao, qtd, modelo, fabricante, data_envio, resp_manutencao, nota_origem, nota_envio, sc, responsavel, status, observacoes))
        conn.commit()
        flash('Remessa cadastrada com sucesso!')
    except Exception as e:
        print(f"Erro ao salvar remessa: {e}")
        flash('Erro ao cadastrar remessa.')
    finally:
        conn.close()
    return redirect(url_for('manutencao'))

@app.route('/editar_remessa/<int:id>', methods=['POST'])
def editar_remessa(id):
    if 'perfil' not in session:
        return redirect(url_for('index'))
    tag             = request.form.get('tag')
    descricao       = request.form.get('descricao')
    qtd             = request.form.get('qtd')
    modelo          = request.form.get('modelo')
    fabricante      = request.form.get('fabricante')
    data_envio      = request.form.get('data_envio')
    resp_manutencao = request.form.get('resp_manutencao')
    nota_origem     = request.form.get('nota_origem')
    nota_envio      = request.form.get('nota_envio')
    nota_retorno    = request.form.get('nota_retorno')
    data_retorno    = request.form.get('data_retorno')
    sc              = request.form.get('sc')
    responsavel     = request.form.get('responsavel')
    status          = request.form.get('status')
    observacoes     = request.form.get('observacoes')
    conn = conectar()
    try:
        conn.execute("""
            UPDATE manutencao_remessas SET
            tag=?, descricao=?, qtd=?, modelo=?, fabricante=?, data_envio=?,
            resp_manutencao=?, nota_origem=?, nota_envio=?, nota_retorno=?,
            data_retorno=?, sc=?, responsavel=?, status=?, observacoes=?
            WHERE id=?
        """, (tag, descricao, qtd, modelo, fabricante, data_envio, resp_manutencao,
              nota_origem, nota_envio, nota_retorno, data_retorno, sc, responsavel,
              status, observacoes, id))
        
        if status == 'Concluído':
            conn.execute("UPDATE itens SET status = 'Disponível' WHERE codigo = ?", (tag,))
        
        conn.commit()
        flash('Remessa atualizada com sucesso!')
    except Exception as e:
        print(f"Erro ao editar remessa: {e}")
        flash('Erro ao editar remessa.')
    finally:
        conn.close()
    return redirect(url_for('manutencao'))

@app.route('/enviar_formulario', methods=['GET', 'POST'])
def enviar_formulario():
    if request.method == 'POST':
        nome_adm        = request.form.get('nome_adm')
        motivo          = request.form.get('motivo')
        data_envio      = request.form.get('data_envio')
        usuario_destino = request.form.get('usuario_destino')
        observacoes     = request.form.get('observacoes')
        if usuario_destino:
            try:
                corpo = f"Remetente: {nome_adm}\nMotivo: {motivo}\nData: {data_envio}\n\n{observacoes}\n\nFerramentaria Mizu"
                msg = Message(subject=f"Formulario Mizu - {motivo}", recipients=[usuario_destino.strip()], body=corpo)
                mail.send(msg)
                flash(f'Formulário enviado com sucesso para {usuario_destino}!', 'success')
                return redirect(url_for('ver_ferramentas'))
            except Exception as e:
                flash('Erro ao enviar e-mail. Verifique a conexão ou o endereço digitado.', 'error')
        else:
            flash('E-mail de destino não preenchido.', 'error')
    return render_template('formulario.html')

@app.route('/relatorio')
def relatorio():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    if session.get('perfil') != 'ADMINISTRADOR':
        return redirect(url_for('dashboard_funcionario'))
    
    conn = conectar()
    
    # Filtros
    filtro_funcionario = request.args.get('funcionario', '')
    filtro_codigo      = request.args.get('codigo', '')
    filtro_data_inicio = request.args.get('data_inicio', '')
    filtro_data_fim    = request.args.get('data_fim', '')

    query = """
        SELECT 
            log.data,
            log.descricao,
            u.nome as funcionario,
            u.matricula
        FROM log_atividades log
        LEFT JOIN usuarios u ON log.usuario_id = u.id
        WHERE (log.descricao LIKE '%Retirou%' OR log.descricao LIKE '%Devolveu%' OR log.descricao LIKE '%Reservou%')
    """
    params = []

    if filtro_funcionario:
        query += " AND u.nome LIKE ?"
        params.append(f'%{filtro_funcionario}%')
    if filtro_codigo:
        query += " AND log.descricao LIKE ?"
        params.append(f'%{filtro_codigo}%')
    if filtro_data_inicio:
        query += " AND log.data >= ?"
        params.append(filtro_data_inicio)
    if filtro_data_fim:
        query += " AND log.data <= ?"
        params.append(filtro_data_fim + ' 23:59:59')

    query += " ORDER BY log.data DESC"

    movimentacoes = conn.execute(query, params).fetchall()
    funcionarios  = conn.execute("SELECT DISTINCT nome FROM usuarios ORDER BY nome ASC").fetchall()
    conn.close()

    return render_template('relatorio.html',
        movimentacoes=movimentacoes,
        funcionarios=funcionarios,
        filtro_funcionario=filtro_funcionario,
        filtro_codigo=filtro_codigo,
        filtro_data_inicio=filtro_data_inicio,
        filtro_data_fim=filtro_data_fim
    )

@app.route('/novo_cadastro')
def novo_cadastro():
    return render_template('cadastro.html')

@app.route('/processar_solicitacao', methods=['POST'])
def processar_solicitacao():
    matricula = request.form.get('matricula')
    nome      = request.form.get('nome')
    email     = request.form.get('email', '').strip().lower()
    setor     = request.form.get('setor')
    senha     = request.form.get('senha')
    if '@' not in email:
        email = email + '@mizu.com.br'
    senha_hash = generate_password_hash(senha)
    conn = conectar()
    try:
        conn.execute("INSERT INTO usuarios (nome, email, senha, setor, matricula, status, perfil) VALUES (?, ?, ?, ?, ?, 'Pendente', 'FUNCIONARIO')", (nome, email, senha_hash, setor, matricula))
        conn.commit()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()
    flash('Solicitacao enviada! Aguarde aprovacao.')
    return redirect(url_for('index'))

@app.route('/aprovar_usuario/<int:id>', methods=['POST'])
def aprovar_usuario(id):
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    conn.execute("UPDATE usuarios SET status='Aprovado' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('solicitar_acesso'))

@app.route('/solicitar_acesso')
def solicitar_acesso():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    usuarios = conn.execute("SELECT id, nome, email, setor, status, matricula FROM usuarios").fetchall()
    conn.close()
    return render_template('solicitar_acesso.html', usuarios=usuarios)

@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    matricula = request.form.get('matricula')
    nome      = request.form.get('nome')
    email     = request.form.get('email', '').strip().lower()
    setor     = request.form.get('setor')
    senha     = request.form.get('senha')
    if '@' not in email:
        email = email + '@mizu.com.br'
    senha_hash = generate_password_hash(senha)
    conn = conectar()
    conn.execute("INSERT INTO usuarios (nome, email, senha, setor, matricula, status, perfil) VALUES (?, ?, ?, ?, ?, 'Aprovado', 'FUNCIONARIO')", (nome, email, senha_hash, setor, matricula))
    conn.commit()
    conn.close()
    return redirect(url_for('solicitar_acesso'))

@app.route('/excluir_usuario/<int:id>', methods=['POST'])
def excluir_usuario(id):
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    conn.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('solicitar_acesso'))

@app.route('/cadastrar')
def cadastrar():
    return render_template('cadastrar_ferramenta.html')

@app.route('/cadastrar_ferramenta')
def cadastrar_ferramenta():
    return render_template('cadastrar_ferramenta.html')

@app.route('/salvar_ferramenta', methods=['POST'])
def salvar_ferramenta():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    codigo      = request.form.get('codigo')
    nome        = request.form.get('nome')
    marca       = request.form.get('marca')
    quantidade  = request.form.get('quantidade')
    observacoes = request.form.get('observacoes')
    conn = conectar()
    try:
        existe = conn.execute("SELECT id FROM itens WHERE codigo = ?", (codigo,)).fetchone()
        if existe:
            flash('Erro: já existe uma ferramenta com esse código!')
            return redirect(url_for('cadastrar_ferramenta'))
        conn.execute(
            "INSERT INTO itens (codigo, nome, marca, quantidade, status, observacoes) VALUES (?, ?, ?, ?, 'Disponível', ?)",
            (codigo, nome, marca, quantidade, observacoes)
        )
        conn.commit()
        flash('Ferramenta cadastrada com sucesso!')
    except Exception as e:
        print(f"Erro ao cadastrar: {e}")
        flash('Erro ao cadastrar ferramenta.')
    finally:
        conn.close()
    return redirect(url_for('ver_ferramentas'))

@app.route('/usuarios')
def usuarios():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    lista = conn.execute("SELECT * FROM usuarios ORDER BY nome ASC").fetchall()
    conn.close()
    return render_template('usuarios.html', usuarios=lista)

@app.route('/editar_usuario', methods=['POST'])
def editar_usuario():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    id         = request.form.get('id')
    nome       = request.form.get('nome')
    email      = request.form.get('email')
    setor      = request.form.get('setor')
    matricula  = request.form.get('matricula')
    nova_senha = request.form.get('nova_senha')
    conn = conectar()
    if nova_senha:
        conn.execute("UPDATE usuarios SET nome=?, email=?, setor_cargo=?, matricula=?, senha=? WHERE id=?",
                     (nome, email, setor, matricula, generate_password_hash(nova_senha), id))
    else:
        conn.execute("UPDATE usuarios SET nome=?, email=?, setor_cargo=?, matricula=? WHERE id=?",
                     (nome, email, setor, matricula, id))
    conn.execute("INSERT INTO log_atividades (usuario_id, descricao) VALUES (?, 'Perfil atualizado.')", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('usuarios'))

@app.route('/desativar_usuario/<int:id>')
def desativar_usuario(id):
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    conn.execute("UPDATE usuarios SET ativo=0, status='Inativo' WHERE id=?", (id,))
    conn.execute("INSERT INTO log_atividades (usuario_id, descricao) VALUES (?, 'Usuario desativado.')", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('usuarios'))

@app.route('/nova_determinacao', methods=['POST'])
def nova_determinacao():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    usuario_id    = request.form.get('usuario_id')
    descricao     = request.form.get('descricao')
    email_destino = request.form.get('email_destino')
    conn = conectar()
    conn.execute("INSERT INTO log_atividades (usuario_id, descricao) VALUES (?, ?)", (usuario_id, f'Nova determinacao: {descricao[:50]}'))
    conn.commit()
    conn.close()
    if email_destino:
        try:
            msg = Message(subject='Nova Determinacao - Mizu', recipients=[email_destino], body=f'Voce recebeu uma nova determinacao:\n\n{descricao}\n\nAdministracao Mizu')
            mail.send(msg)
            flash('E-mail enviado!')
        except Exception as e:
            flash(f'Erro ao enviar: {str(e)}')
    return redirect(url_for('usuarios'))

@app.route('/linha_tempo/<int:id>')
def linha_tempo(id):
    if 'perfil' not in session:
        return redirect(url_for('index'))
    conn = conectar()
    logs = conn.execute("""
        SELECT descricao, data FROM log_atividades
        WHERE usuario_id = ?
        ORDER BY data DESC
    """, (id,)).fetchall()
    conn.close()
    return jsonify([{'descricao': l['descricao'], 'data': l['data']} for l in logs])

@app.route('/salvar_permissoes', methods=['POST'])
def salvar_permissoes():
    if 'perfil' not in session:
        return redirect(url_for('index'))
    return redirect(url_for('usuarios'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
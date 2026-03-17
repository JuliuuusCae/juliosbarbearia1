from flask import Flask, render_template, request, redirect, session, url_for, flash, g
import datetime
import os
import urllib.parse
from config import Config
from database import get_db, close_db, init_app as init_db_app

# Geração de horários padrão
def gerar_horarios():
    horarios = []
    hora = 7
    minuto = 0
    while True:
        horarios.append(f"{hora:02d}:{minuto:02d}")
        minuto += 30
        if minuto == 60:
            minuto = 0
            hora += 1
        if hora == 18 and minuto == 30:
            break
    return horarios

HORARIOS_PADRAO = gerar_horarios()

app = Flask(__name__)
app.config.from_object(Config)
init_db_app(app)

@app.before_request
def load_logged_in_user():
    user_id = session.get("logado")
    if user_id is None:
        g.user = None
    else:
        g.user = user_id

@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()
    cursor = db.cursor()

    data_param = request.args.get("data")
    if not data_param:
        data_param = datetime.date.today().strftime("%Y-%m-%d")

    if request.method == "POST":
        nome = request.form["nome"]
        telefone = request.form.get("telefone", "")
        data_agendamento = request.form["data"]
        horario_agendamento = request.form["horario"]
        servico = request.form["servico"]

        cursor.execute(
            "SELECT * FROM agendamentos WHERE data=? AND horario=?",
            (data_agendamento, horario_agendamento)
        )
        existe = cursor.fetchone()

        if existe:
            flash("Este horário já está agendado. Por favor, escolha outro.", "error")
        else:
            cursor.execute(
                "INSERT INTO agendamentos(nome, telefone, data, horario, servico) VALUES (?, ?, ?, ?, ?)",
                (nome, telefone, data_agendamento, horario_agendamento, servico)
            )
            db.commit()

            data_br = datetime.datetime.strptime(data_agendamento, "%Y-%m-%d").strftime("%d/%m/%Y")
            flash(f"Agendamento confirmado para {data_br} às {horario_agendamento} - Serviço: {servico}", "success")

            # Preparar mensagem WhatsApp para o barbeiro
            whatsapp_message = (
                f"*NOVO AGENDAMENTO!*\n\n"
                f"*Cliente:* {nome}\n"
                f"*Telefone:* {telefone if telefone else 'Não informado'}\n"
                f"*Data:* {data_br}\n"
                f"*Horário:* {horario_agendamento}\n"
                f"*Serviço:* {servico}\n\n"
                f"Acesse o painel administrativo para mais detalhes."
            )
            # Codifica a mensagem para o formato de URL para evitar erro de caracteres de nova linha
            encoded_message = urllib.parse.quote(whatsapp_message)
            whatsapp_url = f"https://wa.me/{Config.BARBER_WHATSAPP_NUMBER}?text={encoded_message}"

            return redirect(whatsapp_url)

    cursor.execute("SELECT horario FROM horarios ORDER BY horario")
    horarios_disponiveis = [h[0] for h in cursor.fetchall()]

    cursor.execute("SELECT horario FROM agendamentos WHERE data=?", (data_param,))
    horarios_ocupados = [h[0] for h in cursor.fetchall()]

    return render_template(
        "index.html",
        horarios=horarios_disponiveis,
        ocupados=horarios_ocupados,
        data_selecionada=data_param,
        servicos=Config.SERVICOS_PADRAO,
        dias_semana=Config.DIAS_SEMANA
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("admin"))

    if request.method == "POST":
        username = request.form["usuario"]
        password = request.form["senha"]

        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session["logado"] = True
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("admin"))
        else:
            flash("Usuário ou senha inválidos.", "error")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logado", None)
    flash("Você foi desconectado.", "info")
    return redirect(url_for("index"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not g.user:
        flash("Você precisa estar logado para acessar esta página.", "warning")
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()

    data_filtro = None
    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_horarios":
            cursor.execute("DELETE FROM horarios")
            horarios_selecionados = request.form.getlist("horarios")
            for h in horarios_selecionados:
                cursor.execute("INSERT INTO horarios(horario) VALUES (?)", (h,))
            db.commit()
            flash("Horários atualizados com sucesso!", "success")
        elif action == "filter_agendamentos":
            data_filtro = request.form.get("data_filtro")

    cursor.execute("SELECT id, horario FROM horarios ORDER BY horario")
    horarios_configurados_com_id = cursor.fetchall()
    horarios_configurados = [h[1] for h in horarios_configurados_com_id]

    if data_filtro:
        cursor.execute("SELECT * FROM agendamentos WHERE data=? ORDER BY horario", (data_filtro,))
    else:
        cursor.execute("SELECT * FROM agendamentos ORDER BY data, horario")
    agendamentos = cursor.fetchall()

    return render_template(
        "admin.html",
        horarios_disponiveis=HORARIOS_PADRAO,
        horarios_configurados=horarios_configurados,
        horarios_configurados_com_id=horarios_configurados_com_id,
        servicos=Config.SERVICOS_PADRAO,
        dias_semana=Config.DIAS_SEMANA,
        agendamentos=agendamentos,
        data_filtro=data_filtro
    )

@app.route("/agendamento/excluir/<int:id_agendamento>")
def excluir_agendamento(id_agendamento):
    if not g.user:
        flash("Você precisa estar logado para realizar esta ação.", "warning")
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM agendamentos WHERE id=?", (id_agendamento,))
    db.commit()
    flash("Agendamento excluído com sucesso!", "success")
    return redirect(url_for("admin"))

@app.route("/horario/excluir/<int:id_horario>")
def excluir_horario(id_horario):
    if not g.user:
        flash("Você precisa estar logado para realizar esta ação.", "warning")
        return redirect(url_for("login"))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM horarios WHERE id=?", (id_horario,))
    db.commit()
    flash("Horário excluído com sucesso!", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

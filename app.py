from flask import Flask, render_template, request, redirect, session, url_for, flash, g
import datetime
import os
import urllib.parse
import sqlite3
from config import Config
from database import get_db, close_db, init_app as init_db_app

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

    # Determina o dia da semana para a data selecionada
    data_obj = datetime.datetime.strptime(data_param, "%Y-%m-%d").date()
    dia_semana_num = data_obj.weekday() # 0=Segunda, 6=Domingo
    dia_semana_nome = Config.DIAS_SEMANA[dia_semana_num]

    # Gera horários baseados na configuração HORARIOS_POR_DIA
    horarios_base_dia = []
    if dia_semana_nome in Config.HORARIOS_POR_DIA:
        for inicio_str, fim_str in Config.HORARIOS_POR_DIA[dia_semana_nome]:
            inicio_hora, inicio_min = map(int, inicio_str.split(":"))
            fim_hora, fim_min = map(int, fim_str.split(":"))

            current_time = datetime.datetime(1, 1, 1, inicio_hora, inicio_min)
            end_time = datetime.datetime(1, 1, 1, fim_hora, fim_min)

            while current_time < end_time:
                horarios_base_dia.append(current_time.strftime("%H:%M"))
                current_time += datetime.timedelta(minutes=30)

    # Recupera horários configurados para o dia da semana específico no banco de dados
    cursor.execute("SELECT horario FROM horarios WHERE dia_semana=? ORDER BY horario", (dia_semana_nome,))
    horarios_configurados_db = [h[0] for h in cursor.fetchall()]

    # Se houver horários configurados no DB para este dia, usa-os. Caso contrário, usa os horários base do dia.
    if horarios_configurados_db:
        horarios_disponiveis_para_exibir = [h for h in horarios_configurados_db if h in horarios_base_dia]
    else:
        horarios_disponiveis_para_exibir = horarios_base_dia

    # Remove horários duplicados e ordena
    horarios_disponiveis_para_exibir = sorted(list(set(horarios_disponiveis_para_exibir)))

    cursor.execute("SELECT horario FROM agendamentos WHERE data=?", (data_param,))
    horarios_ocupados = [h[0] for h in cursor.fetchall()]

    # Filtra os horários disponíveis removendo os horários ocupados
    horarios_finais_para_exibir = [h for h in horarios_disponiveis_para_exibir if h not in horarios_ocupados]

    return render_template(
        "index.html",
        horarios=horarios_finais_para_exibir,
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
    dia_selecionado = request.args.get("dia", "Segunda") # Dia padrão para exibir no admin

    if request.method == "POST":
        action = request.form.get("action")
        if action == "update_horarios":
            dia_para_atualizar = request.form.get("dia_semana")
            cursor.execute("DELETE FROM horarios WHERE dia_semana=?", (dia_para_atualizar,))
            horarios_selecionados = request.form.getlist("horarios")
            for h in horarios_selecionados:
                cursor.execute("INSERT INTO horarios(horario, dia_semana) VALUES (?, ?)", (h, dia_para_atualizar))
            db.commit()
            flash(f"Horários para {dia_para_atualizar} atualizados com sucesso!", "success")
            dia_selecionado = dia_para_atualizar # Mantém o dia selecionado após salvar
        elif action == "add_horario":
            dia_para_adicionar = request.form.get("dia_semana")
            horario_novo = request.form.get("horario_personalizado")
            if horario_novo:
                try:
                    # Valida o formato do horário
                    datetime.datetime.strptime(horario_novo, "%H:%M")
                    cursor.execute("INSERT INTO horarios(horario, dia_semana) VALUES (?, ?)", (horario_novo, dia_para_adicionar))
                    db.commit()
                    flash(f"Horário {horario_novo} adicionado para {dia_para_adicionar} com sucesso!", "success")
                except sqlite3.IntegrityError:
                    flash(f"O horário {horario_novo} já existe para {dia_para_adicionar}.", "error")
                except ValueError:
                    flash(f"Formato de horário inválido: {horario_novo}. Use HH:MM.", "error")
            else:
                flash("Nenhum horário foi fornecido para adicionar.", "error")
            dia_selecionado = dia_para_adicionar # Mantém o dia selecionado após adicionar
        elif action == "filter_agendamentos":
            data_filtro = request.form.get("data_filtro")

    # Recupera horários configurados para o dia selecionado no admin
    cursor.execute("SELECT id, horario FROM horarios WHERE dia_semana=? ORDER BY horario", (dia_selecionado,))
    horarios_configurados_com_id = cursor.fetchall()
    horarios_configurados = [h[1] for h in horarios_configurados_com_id]

    # Gera horários base para o dia selecionado para exibir como opções
    horarios_base_dia_admin = []
    if dia_selecionado in Config.HORARIOS_POR_DIA:
        for inicio_str, fim_str in Config.HORARIOS_POR_DIA[dia_selecionado]:
            inicio_hora, inicio_min = map(int, inicio_str.split(":"))
            fim_hora, fim_min = map(int, fim_str.split(":"))

            current_time = datetime.datetime(1, 1, 1, inicio_hora, inicio_min)
            end_time = datetime.datetime(1, 1, 1, fim_hora, fim_min)

            while current_time < end_time:
                horarios_base_dia_admin.append(current_time.strftime("%H:%M"))
                current_time += datetime.timedelta(minutes=30)

    if data_filtro:
        cursor.execute("SELECT * FROM agendamentos WHERE data=? ORDER BY horario", (data_filtro,))
    else:
        cursor.execute("SELECT * FROM agendamentos ORDER BY data, horario")
    agendamentos = cursor.fetchall()

    return render_template(
        "admin.html",
        horarios_disponiveis=horarios_base_dia_admin,
        horarios_configurados=horarios_configurados,
        horarios_configurados_com_id=horarios_configurados_com_id,
        servicos=Config.SERVICOS_PADRAO,
        dias_semana=Config.DIAS_SEMANA,
        dia_selecionado=dia_selecionado,
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

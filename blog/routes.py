import secrets
from flask import render_template, request, flash, redirect, url_for, abort
from blog import app, database, bcrypt
from blog.forms import FormCadastrar, FormLogin, FormEditarPerfil, FormCriarPost, FormRedefinirSenha
from blog.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import os
from PIL import Image
from datetime import datetime
import smtplib
import email.message




@app.route('/usuario')
@login_required
def usuario():
    lista_usuarios = list(Usuario.query.all())
    return render_template('usuario.html', lista_usuarios=lista_usuarios)


@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_cadastrar = FormCadastrar()
    form_login = FormLogin()

    if form_cadastrar.validate_on_submit() and 'botao_cadastrar' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_cadastrar.senha.data)
        usuario = Usuario(username=form_cadastrar.username.data, email=form_cadastrar.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'{form_cadastrar.email.data} cadastrado com sucesso!', 'alert-success')
        return redirect(url_for('home'))

    if form_login.validate_on_submit() and 'botao_logar' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.manter_dados.data)
            flash(f'{form_cadastrar.email.data} logado com sucesso!', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(' Email ou senha incorretos!', 'alert-danger')
    return render_template('login.html', form_cadastrar=form_cadastrar, form_login=form_login)

@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash('Logout feito com sucesso!', 'alert-success')
    return redirect(url_for('home'))

@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('home'))
    return render_template('criarpost.html', form=form)

@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    cursos = current_user.cursos.split(';')
    return render_template('perfil.html', foto_perfil=foto_perfil, cursos=cursos)


def salvar_imagem(img):
    # adicionar codigo ao nome da imagem
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(img.filename)
    nome_arquivo = nome + codigo + extensao

    # Passa o caminho em que a imagem sera salva
    caminho_completo = os.path.join(app.root_path, f'static/fotos_perfil', nome_arquivo)

    # tratar a imagem para ficar do tamanho padrao
    tamanho = (400, 400)
    imagem_reduzida = Image.open(img)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo


def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    return ';'.join(lista_cursos)


@app.route('/perfil/editar', methods=['POST', 'GET'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    foto_perfil = url_for('static', filename=f'fotos_perfil/{current_user.foto_perfil}')
    if form.validate_on_submit():
        senha_cript = bcrypt.generate_password_hash(form.senha.data)
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.senha = senha_cript
        current_user.cursos = atualizar_cursos(form)
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        database.session.commit()
        flash('Perfil atualizado com sucesso!', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    cursos = current_user.cursos.split(';')
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form, cursos=cursos)


@app.route('/post/<post_id>', methods=['POST', 'GET'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            post.data_criação = datetime.utcnow
            database.session.commit()
            flash('Post editado com sucesso!', 'alert-success')
            return redirect(url_for('home'))
    else:
        form = None
    return render_template('post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['POST', 'GET'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post excluido com sucesso!', 'alert-danger')
        return redirect(url_for('home'))

    else:
        abort(403)

def enviar_email(email_usuario):
    corpo_email = """
    TESTE
    """

    msg = email.message.Message()
    msg['Subject'] = "Assunto"
    msg['From'] = 'blog.flask001@gmail.com'
    msg['To'] = f'{email_usuario}'
    password = 'xoadtogzatldsydf'
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email )

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()
    # Login Credentials for sending the mail
    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')


@app.route('/redefinirsenha', methods=['POST', 'GET'])
def redefinir_senha():
    form = FormRedefinirSenha()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario:
            enviar_email(form.email.data)
            flash('Email enviado com sucesso!', 'alert-success')
            return redirect(url_for('home'))
        else:
            flash('Usuario não cadastrado!', 'alert-danger')
    return render_template('redefinirsenha.html', form=form)
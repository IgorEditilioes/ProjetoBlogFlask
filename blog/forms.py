from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import Length, Email, EqualTo, DataRequired, ValidationError
from blog.models import Usuario
from flask_login import current_user


class FormCadastrar(FlaskForm):
    username = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(4, 8)])
    confirma_senha = PasswordField('Confirma Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_cadastrar = SubmitField('Cadastrar')

    # sempre que uma coluna for de valor unico tem que criar um metodo para validar
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar')

class FormLogin(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    manter_dados = BooleanField('manter dados salvos')
    botao_logar = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    foto_perfil = FileField('Editar foto de perfil', validators=[FileAllowed(['jpg', 'png', 'JPEG'])])
    username = StringField('Nome', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(4, 8)])
    confirma_senha = PasswordField('Confirma Senha', validators=[DataRequired(), EqualTo('senha')])
    curso_excel = BooleanField('Excel')
    curso_python = BooleanField('Python')
    curso_sql = BooleanField('Sql')
    botao_editar_perfil = SubmitField('Confirmar')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('E-mail já cadastrado.')


class FormCriarPost(FlaskForm):
    titulo = StringField('Titulo do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu texto aqui', validators=[DataRequired()])
    botao_criar_post = SubmitField('Criar Post')


class FormRedefinirSenha(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    botao_redefinir_senha = SubmitField('Enviar')
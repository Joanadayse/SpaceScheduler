from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, IntegerField, TextAreaField, DateTimeLocalField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from datetime import datetime
from models import Booking

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateTimeField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Form for user login"""
    name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Entrar')


class SpaceForm(FlaskForm):
    """Form for creating/editing spaces"""
    name = StringField('Nome do Espaço', validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Tipo de Espaço', choices=[
        ('coworking', 'Coworking'),
        ('auditorium', 'Auditório'),
        ('meeting_room', 'Sala de Reunião')
    ], validators=[DataRequired()])
    capacity = IntegerField('Capacidade', validators=[DataRequired(), NumberRange(min=1)])
    resources = TextAreaField('Recursos Disponíveis')
    submit = SubmitField('Salvar Espaço')

class BookingForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=100)])
    space_id = SelectField('Espaço', coerce=int, validators=[DataRequired()])
    turn = SelectField('Turno', choices=[('manha', 'Manhã'), ('tarde', 'Tarde'), ('dia_inteiro', 'Dia Inteiro')], validators=[DataRequired()])
    description = StringField('Descrição', validators=[Length(max=500)])
    submit = SubmitField('Adicionar Reserva')

# class BookingForm(FlaskForm):
#     title = StringField('Título', validators=[DataRequired(), Length(max=100)])
#     space_id = SelectField('Espaço', coerce=int, validators=[DataRequired()])
#     start_time = DateTimeField('Início', validators=[DataRequired()])
#     end_time = DateTimeField('Fim', validators=[DataRequired()])
#     description = StringField('Descrição', validators=[Length(max=500)])
#     submit = SubmitField('Adicionar Reserva')



# class BookingForm(FlaskForm):
#     title = StringField('Título', validators=[DataRequired()])
#     description = TextAreaField('Descrição')
#     space_id = SelectField('Espaço', coerce=int, validators=[DataRequired()])
#     turn = SelectField('Turno', choices=[('manha', 'Manhã'), ('tarde', 'Tarde'), ('noite', 'Noite')], validators=[DataRequired()])
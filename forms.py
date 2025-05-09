from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, IntegerField, TextAreaField, DateTimeLocalField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from datetime import datetime
from models import Booking


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


# class BookingForm(FlaskForm):
#     """Form for creating/editing bookings"""
#     space_id = SelectField('Espaço', coerce=int, validators=[DataRequired()])
#     title = StringField('Título', validators=[DataRequired(), Length(max=200)])
#     description = TextAreaField('Finalidade/Descrição')
#     start_time = DateTimeLocalField('Hora de Início', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
#     end_time = DateTimeLocalField('Hora de Término', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
#     booking_id = HiddenField()  # For editing existing bookings
#     submit = SubmitField('Salvar Reserva')

#     def validate_end_time(self, field):
#         """Validate end time is after start time"""
#         if field.data <= self.start_time.data:
#             raise ValidationError('O horário de término deve ser posterior ao horário de início')
        
#         # Check for booking conflicts
#         booking_id = None if not self.booking_id.data else int(self.booking_id.data)
#         if Booking.check_conflict(self.space_id.data, self.start_time.data, field.data, exclude_id=booking_id):
#             raise ValidationError('Já existe uma reserva para este espaço no período selecionado')


class BookingForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired()])
    description = TextAreaField('Descrição')
    space_id = SelectField('Espaço', coerce=int, validators=[DataRequired()])
    turn = SelectField('Turno', choices=[('manha', 'Manhã'), ('tarde', 'Tarde'), ('noite', 'Noite')], validators=[DataRequired()])
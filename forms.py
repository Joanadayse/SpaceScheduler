from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, SelectField, IntegerField, TextAreaField, DateTimeLocalField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError
from datetime import datetime
from models import Booking


class LoginForm(FlaskForm):
    """Form for user login"""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Login')


class SpaceForm(FlaskForm):
    """Form for creating/editing spaces"""
    name = StringField('Space Name', validators=[DataRequired(), Length(min=2, max=100)])
    type = SelectField('Space Type', choices=[
        ('coworking', 'Coworking'),
        ('auditorium', 'Auditorium'),
        ('meeting_room', 'Meeting Room')
    ], validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1)])
    resources = TextAreaField('Available Resources')
    submit = SubmitField('Save Space')


class BookingForm(FlaskForm):
    """Form for creating/editing bookings"""
    space_id = SelectField('Space', coerce=int, validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Purpose/Description')
    start_time = DateTimeLocalField('Start Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    end_time = DateTimeLocalField('End Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    booking_id = HiddenField()  # For editing existing bookings
    submit = SubmitField('Save Booking')

    def validate_end_time(self, field):
        """Validate end time is after start time"""
        if field.data <= self.start_time.data:
            raise ValidationError('End time must be after start time')
        
        # Check for booking conflicts
        booking_id = None if not self.booking_id.data else int(self.booking_id.data)
        if Booking.check_conflict(self.space_id.data, self.start_time.data, field.data, exclude_id=booking_id):
            raise ValidationError('There is already a booking for this space during the selected time')

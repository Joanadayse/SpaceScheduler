from flask import render_template, redirect, url_for, flash, request, jsonify, session
from app import db
from models import User, Space, Booking
from forms import LoginForm, SpaceForm, BookingForm
from datetime import datetime, timedelta
import logging
from flask import Response
from ics import Calendar, Event
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import datetime
from datetime import time


from io import BytesIO
from datetime import datetime


TURNOS = [
    (time(8, 0), time(12, 0)),  # Turno 1: 08:00 - 12:00
    (time(12, 0), time(18, 0)),  # Turno 2: 12:00 - 18:00
    (time(18, 0), time(22, 0))   # Turno 3: 18:00 - 22:00
]


def check_turno(start_time, end_time):
    """Verifica se a reserva está dentro de um dos turnos definidos."""
    for turno_inicio, turno_fim in TURNOS:
        if turno_inicio <= start_time.time() < turno_fim and turno_inicio < end_time.time() <= turno_fim:
            return True
    return False          


def register_routes(app):
    @app.route('/')
    def index():
        """Home page - redirects to login if not logged in, otherwise to bookings"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return redirect(url_for('bookings'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        form = LoginForm()
        
        if form.validate_on_submit():
            # Check if the user exists, if not create a new user
            user = User.query.filter_by(email=form.email.data).first()
            
            if not user:
                # Create new user
                user = User(name=form.name.data, email=form.email.data)
                db.session.add(user)
                db.session.commit()
                logging.debug(f"Created new user: {user.name} ({user.email})")
            
            # Store user ID in session
            session['user_id'] = user.id
            session['user_name'] = user.name
            flash(f'Bem-vindo(a), {user.name}!', 'success')
            return redirect(url_for('bookings'))
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    def logout():
        """Logout user"""
        session.clear()
        flash('Você saiu do sistema', 'info')
        return redirect(url_for('login'))
    
    @app.route('/spaces')
    def spaces():
        """List all spaces"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        spaces = Space.query.all()
        return render_template('spaces.html', spaces=spaces)
    
    @app.route('/spaces/add', methods=['GET', 'POST'])
    def add_space():
        """Add a new space"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        form = SpaceForm()
        
        if form.validate_on_submit():
            space = Space(
                name=form.name.data,
                type=form.type.data,
                capacity=form.capacity.data,
                resources=form.resources.data
            )
            db.session.add(space)
            db.session.commit()
            flash(f'Espaço "{space.name}" foi adicionado com sucesso', 'success')
            return redirect(url_for('spaces'))
        
        return render_template('add_space.html', form=form)
    
    @app.route('/spaces/edit/<int:space_id>', methods=['GET', 'POST'])
    def edit_space(space_id):
        """Edit an existing space"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        space = Space.query.get_or_404(space_id)
        form = SpaceForm(obj=space)
        
        if form.validate_on_submit():
            form.populate_obj(space)
            db.session.commit()
            flash(f'Espaço "{space.name}" foi atualizado com sucesso', 'success')
            return redirect(url_for('spaces'))
        
        return render_template('edit_space.html', form=form, space=space)
    
    @app.route('/bookings')
    def bookings():
        """List bookings in a list view"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        # Get filter parameters
        space_id = request.args.get('space_id', type=int)
        date_str = request.args.get('date')
        
        # Build query
        query = Booking.query
        
        if space_id:
            query = query.filter_by(space_id=space_id)
        
        if date_str:
            try:
                filter_date = datetime.strptime(date_str, '%Y-%m-%d')
                query = query.filter(
                    db.func.date(Booking.start_time) == filter_date.date()
                )
            except ValueError:
                flash('Formato de data inválido', 'error')
        
        # Get all bookings (recent first)
        bookings = query.order_by(Booking.start_time.desc()).all()
        
        # Get all spaces for filter dropdown
        spaces = Space.query.all()
        
        return render_template('bookings.html', bookings=bookings, spaces=spaces, selected_space=space_id, selected_date=date_str)
    
    @app.route('/calendar')
    def calendar():
        """Calendar view of bookings"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        spaces = Space.query.all()
        space_id = request.args.get('space_id', type=int)
        
        return render_template('calendar.html', spaces=spaces, selected_space=space_id)
    
   

      

    @app.route('/api/bookings')
    def get_bookings():
        """API endpoint to get bookings for calendar"""
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        
        space_id = request.args.get('space_id', type=int)
        start = request.args.get('start')
        end = request.args.get('end')
        
        # Build query
        query = Booking.query
        
        if space_id:
            query = query.filter_by(space_id=space_id)
        
        if start:
            start_date = datetime.fromisoformat(start.replace('Z', '+00:00'))
            query = query.filter(Booking.end_time >= start_date)
        
        if end:
            end_date = datetime.fromisoformat(end.replace('Z', '+00:00'))
            query = query.filter(Booking.start_time <= end_date)
        
        bookings = query.all()
        
        events = []
        for booking in bookings:
            space = Space.query.get(booking.space_id)
            user = User.query.get(booking.user_id)
            
            # Obtenha o turno
            turno = check_turno(booking.start_time.hour)
            
            events.append({
                'id': booking.id,
                'title': f"{booking.title} ({turno})",  # Inclui o turno no título
                'start': booking.start_time.isoformat(),
                'end': booking.end_time.isoformat(),
                'extendedProps': {
                    'space': space.name,
                    'description': booking.description,
                    'user': user.name,
                    'spaceId': space.id,
                    'userId': user.id
                }
            })
        
        return jsonify(events)
    
   

    
    @app.route('/bookings/edit/<int:booking_id>', methods=['GET', 'POST'])
    def edit_booking(booking_id):
        """Edit an existing booking"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        booking = Booking.query.get_or_404(booking_id)
        form = BookingForm(obj=booking)
        
        # Set choices for space_id
        form.space_id.choices = [(s.id, s.name) for s in Space.query.all()]
        
        # Set the booking_id for conflict validation
        form.booking_id.data = booking_id
        
        if form.validate_on_submit():
            form.populate_obj(booking)
            db.session.commit()
            flash('Reserva atualizada com sucesso', 'success')
            return redirect(url_for('bookings'))
        
        return render_template('edit_booking.html', form=form, booking=booking)
    
    @app.route('/bookings/delete/<int:booking_id>', methods=['POST'])
    def delete_booking(booking_id):
        """Delete a booking"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        flash('Reserva excluída com sucesso', 'success')
        
        # If the request came from an AJAX call, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True)
        
        return redirect(url_for('bookings'))
    
    @app.route('/history')
    def history():
        """View booking history for the current user"""
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        user_id = session['user_id']
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.start_time.desc()).all()
        
        return render_template('history.html', bookings=bookings)
    
    @app.context_processor
    def inject_user():
        """Make user info and current datetime available to all templates"""
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return {'current_user': user, 'now': datetime.now()}
    
    


    # @app.route('/export_bookings_pdf')
    # def export_bookings_pdf():
    #     bookings = [
    #         {
    #             'space_name': 'Sala 1',
    #             'title': 'Reunião de Projeto',
    #             'date': '2025-05-10',
    #             'time': '10:00 - 12:00',
    #             'responsible': 'Alice',
    #         },
    #         # Adicione mais reservas conforme necessário
    #     ]

    #     # Cria um buffer em memória para o PDF
    #     buffer = BytesIO()
    #     c = canvas.Canvas(buffer, pagesize=letter)
    #     c.setFont("Helvetica", 12)

    #     y = 750  # Posição vertical inicial
    #     for booking in bookings:
    #         c.drawString(100, y, f"Espaço: {booking['space_name']}")
    #         c.drawString(100, y - 20, f"Título: {booking['title']}")
    #         c.drawString(100, y - 40, f"Data: {booking['date']}")
    #         c.drawString(100, y - 60, f"Horário: {booking['time']}")
    #         c.drawString(100, y - 80, f"Responsável: {booking['responsible']}")
    #         y -= 100  # Espaço entre as reservas

    #     c.save()
    #     buffer.seek(0)  # Rewind the buffer to the beginning

    #     response = Response(buffer.getvalue(), content_type='application/pdf')
    #     response.headers['Content-Disposition'] = 'attachment; filename=reservas.pdf'
    #     return response


    @app.route('/export_bookings_pdf')
    def export_bookings_pdf():
        bookings = Booking.query.order_by(Booking.start_time).all()

        # Cria um buffer em memória para o PDF
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica", 12)

        y = 750  # Posição vertical inicial

        for booking in bookings:
            # Formata as datas/horários
            date_str = booking.start_time.strftime('%d/%m/%Y')
            time_str = f"{booking.start_time.strftime('%H:%M')} - {booking.end_time.strftime('%H:%M')}"
            responsible = booking.user.name if booking.user else 'N/A'
            space_name = booking.space.name if booking.space else 'N/A'

            # Adiciona ao PDF
            c.drawString(100, y, f"Espaço: {space_name}")
            c.drawString(100, y - 20, f"Título: {booking.title}")
            c.drawString(100, y - 40, f"Data: {date_str}")
            c.drawString(100, y - 60, f"Horário: {time_str}")
            c.drawString(100, y - 80, f"Responsável: {responsible}")
            y -= 100

            # Quebra de página se necessário
            if y < 100:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = 750

        c.save()
        buffer.seek(0)

        return Response(buffer.getvalue(),
                        content_type='application/pdf',
                        headers={'Content-Disposition': 'attachment; filename=reservas.pdf'})

  


    @app.route('/bookings/add', methods=['GET', 'POST'])
    def add_booking():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        form = BookingForm()
        form.space_id.choices = [(space.id, space.name) for space in Space.query.all()]

        if form.validate_on_submit():
            # Mapeamento de turnos para horários
            turn_map = {
                'manha': (datetime.strptime('08:00', '%H:%M').time(), datetime.strptime('12:00', '%H:%M').time()),
                'tarde': (datetime.strptime('12:00', '%H:%M').time(), datetime.strptime('17:00', '%H:%M').time()),
                'noite': (datetime.strptime('17:00', '%H:%M').time(), datetime.strptime('22:00', '%H:%M').time())
            }

            # Obter o turno selecionado
            selected_turn = form.turn.data
            start_time, end_time = turn_map[selected_turn]

            # Verificação de conflito de horário
            conflict = Booking.query.filter(
                Booking.space_id == form.space_id.data,
                Booking.start_time < datetime.combine(datetime.today(), end_time),
                Booking.end_time > datetime.combine(datetime.today(), start_time)
            ).first()

            if conflict:
                flash('Já existe uma reserva nesse horário para esse espaço.', 'error')
                return render_template('add_booking.html', form=form)

            # Criação da reserva
            booking = Booking(
                user_id=session['user_id'],
                space_id=form.space_id.data,
                title=form.title.data,
                description=form.description.data,
                start_time=datetime.combine(datetime.today(), start_time),
                end_time=datetime.combine(datetime.today(), end_time)
            )
            db.session.add(booking)
            db.session.commit()

            flash('Reserva adicionada com sucesso!', 'success')
            return redirect(url_for('bookings'))

        return render_template('add_booking.html', form=form)
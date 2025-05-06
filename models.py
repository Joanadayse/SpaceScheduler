from datetime import datetime
from app import db


class User(db.Model):
    """User model for storing user information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'


class Space(db.Model):
    """Space model for storing space information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # coworking, auditorium, meeting room
    capacity = db.Column(db.Integer, nullable=False)
    resources = db.Column(db.Text, nullable=True)  # Description of available resources
    bookings = db.relationship('Booking', backref='space', lazy=True)
    
    def __repr__(self):
        return f'<Space {self.name}>'


class Booking(db.Model):
    """Booking model for storing booking information"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('space.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Booking {self.title} for {self.space.name}>'
    
    @staticmethod
    def check_conflict(space_id, start_time, end_time, exclude_id=None):
        """Check if there's a booking conflict for the given space and time"""
        query = Booking.query.filter(
            Booking.space_id == space_id,
            db.or_(
                db.and_(Booking.start_time <= start_time, Booking.end_time > start_time),
                db.and_(Booking.start_time < end_time, Booking.end_time >= end_time),
                db.and_(Booking.start_time >= start_time, Booking.end_time <= end_time)
            )
        )
        
        if exclude_id:
            query = query.filter(Booking.id != exclude_id)
            
        return query.first() is not None

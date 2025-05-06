document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('booking-form');
    
    if (form) {
        form.addEventListener('submit', function(event) {
            const startTime = document.getElementById('start_time').value;
            const endTime = document.getElementById('end_time').value;
            
            // Convert to Date objects
            const startDate = new Date(startTime);
            const endDate = new Date(endTime);
            
            // Check if end time is after start time
            if (endDate <= startDate) {
                event.preventDefault();
                alert('O horário de término deve ser posterior ao horário de início.');
                return false;
            }
            
            // Check if duration is too long (more than 8 hours)
            const durationMs = endDate - startDate;
            const durationHours = durationMs / (1000 * 60 * 60);
            
            if (durationHours > 8) {
                if (!confirm('A reserva tem duração superior a 8 horas. Deseja continuar?')) {
                    event.preventDefault();
                    return false;
                }
            }
            
            // Check if booking is in the past
            const now = new Date();
            if (startDate < now) {
                if (!confirm('A data/hora de início está no passado. Deseja continuar?')) {
                    event.preventDefault();
                    return false;
                }
            }
            
            return true;
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // Get the space filter value
    const spaceFilter = document.getElementById('space-filter');
    let selectedSpaceId = spaceFilter.value;
    
    // Initialize calendar
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        slotMinTime: '07:00:00',
        slotMaxTime: '22:00:00',
        allDaySlot: false,
        locale: 'pt-br',
        timeZone: 'local',
        selectable: true,
        selectMirror: true,
        eventTimeFormat: {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        },
        businessHours: {
            daysOfWeek: [1, 2, 3, 4, 5], // Monday - Friday
            startTime: '08:00',
            endTime: '20:00',
        },
        height: 'auto',
        
        // Select date range to create new booking
        select: function(info) {
            const url = new URL('/bookings/add', window.location.origin);
            url.searchParams.append('start', info.startStr);
            
            if (selectedSpaceId) {
                url.searchParams.append('space_id', selectedSpaceId);
            }
            
            window.location.href = url.toString();
        },
        
        // Click on event to view details
        eventClick: function(info) {
            const event = info.event;
            const props = event.extendedProps;
            
            // Fill modal with event details
            document.getElementById('event-title').textContent = event.title;
            document.getElementById('event-space').textContent = props.space;
            
            // Format date and time
            const startDate = new Date(event.start);
            const endDate = new Date(event.end);
            const dateFormatted = startDate.toLocaleDateString('pt-BR');
            const startTimeFormatted = startDate.toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false 
            });
            const endTimeFormatted = endDate.toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit',
                hour12: false
            });
            
            document.getElementById('event-date').textContent = dateFormatted;
            document.getElementById('event-time').textContent = `${startTimeFormatted} - ${endTimeFormatted}`;
            document.getElementById('event-user').textContent = props.user;
            
            // Display description or placeholder
            const description = props.description || 'Nenhuma descrição fornecida';
            document.getElementById('event-description').textContent = description;
            
            // Set up edit button
            const editBtn = document.getElementById('edit-event-btn');
            editBtn.href = `/bookings/edit/${event.id}`;
            
            // Set up delete button
            const deleteBtn = document.getElementById('delete-event-btn');
            deleteBtn.setAttribute('data-event-id', event.id);
            deleteBtn.setAttribute('data-event-title', event.title);
            
            // Show the modal
            const eventModal = new bootstrap.Modal(document.getElementById('event-modal'));
            eventModal.show();
        },
        
        // Load events from API
        events: function(info, successCallback, failureCallback) {
            const url = new URL('/api/bookings', window.location.origin);
            
            // Add query parameters
            url.searchParams.append('start', info.startStr);
            url.searchParams.append('end', info.endStr);
            
            if (selectedSpaceId) {
                url.searchParams.append('space_id', selectedSpaceId);
            }
            
            fetch(url.toString())
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Failed to fetch events');
                    }
                    return response.json();
                })
                .then(data => {
                    // Color events based on space type
                    const events = data.map(event => {
                        let backgroundColor;
                        let borderColor;
                        
                        if (event.extendedProps.spaceId === 1 || event.extendedProps.spaceId === 2) {
                            // Coworking
                            backgroundColor = 'var(--bs-info)';
                            borderColor = 'var(--bs-info)';
                        } else if (event.extendedProps.spaceId === 3) {
                            // Auditorium
                            backgroundColor = 'var(--bs-warning)';
                            borderColor = 'var(--bs-warning)';
                        } else {
                            // Meeting rooms
                            backgroundColor = 'var(--bs-success)';
                            borderColor = 'var(--bs-success)';
                        }
                        
                        return {
                            ...event,
                            backgroundColor,
                            borderColor
                        };
                    });
                    
                    successCallback(events);
                })
                .catch(error => {
                    console.error('Error fetching events:', error);
                    failureCallback(error);
                });
        }
    });
    
    calendar.render();
    
    // Handle space filter changes
    spaceFilter.addEventListener('change', function() {
        selectedSpaceId = this.value;
        
        // Update URL without reloading
        const url = new URL(window.location.href);
        if (selectedSpaceId) {
            url.searchParams.set('space_id', selectedSpaceId);
        } else {
            url.searchParams.delete('space_id');
        }
        history.pushState({}, '', url);
        
        // Refetch events with new filter
        calendar.refetchEvents();
    });
    
    // Handle delete event button click
    document.getElementById('delete-event-btn').addEventListener('click', function() {
        const eventId = this.getAttribute('data-event-id');
        const eventTitle = this.getAttribute('data-event-title');
        
        // Close the event details modal
        const eventModal = bootstrap.Modal.getInstance(document.getElementById('event-modal'));
        eventModal.hide();
        
        // Set up the delete confirmation modal
        document.getElementById('delete-event-title').textContent = eventTitle;
        
        const confirmBtn = document.getElementById('confirm-delete-btn');
        confirmBtn.setAttribute('data-event-id', eventId);
        
        // Show the delete confirmation modal
        const deleteModal = new bootstrap.Modal(document.getElementById('delete-confirm-modal'));
        deleteModal.show();
    });
    
    // Handle confirm delete button click
    document.getElementById('confirm-delete-btn').addEventListener('click', function() {
        const eventId = this.getAttribute('data-event-id');
        
        // Send delete request
        fetch(`/bookings/delete/${eventId}`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to delete booking');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Close the modal
                const deleteModal = bootstrap.Modal.getInstance(document.getElementById('delete-confirm-modal'));
                deleteModal.hide();
                
                // Show success message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success alert-dismissible fade show';
                alertDiv.innerHTML = `
                    <i class="fas fa-check-circle me-2"></i>Reserva excluída com sucesso.
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                `;
                
                // Insert alert before the calendar
                const calendarContainer = document.getElementById('calendar').parentNode;
                calendarContainer.insertBefore(alertDiv, calendarContainer.firstChild);
                
                // Refetch events
                calendar.refetchEvents();
                
                // Auto-dismiss alert after 5 seconds
                setTimeout(() => {
                    alertDiv.classList.remove('show');
                    setTimeout(() => alertDiv.remove(), 150);
                }, 5000);
            }
        })
        .catch(error => {
            console.error('Error deleting booking:', error);
            
            // Show error message
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-danger alert-dismissible fade show';
            alertDiv.innerHTML = `
                <i class="fas fa-exclamation-circle me-2"></i>Erro ao excluir a reserva.
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;
            
            // Insert alert before the calendar
            const calendarContainer = document.getElementById('calendar').parentNode;
            calendarContainer.insertBefore(alertDiv, calendarContainer.firstChild);
        });
    });
});

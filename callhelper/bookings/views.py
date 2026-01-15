from django.utils import timezone
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import TimeSlot, BookingSession

@login_required
def my_slots(request):
    """
    Displays a list of slots for the current user.
    """
    slots = TimeSlot.objects.filter(
        owner=request.user).order_by('-start_time')
    context = {
        'slots':slots
    }
    return render(request, 'bookings/my_slots.html', context)

@login_required
def create_slot(request):
    if request.method=='POST':

        session_id = request.POST.get('session_id')
        if session_id:
            try:
                session = BookingSession.objects.get(id=session_id, owner_session=request.user)
            except BookingSession.DoesNotExist:
                messages.error(request, 'Session not found')
                return redirect('bookings:create_slot')
        else:
            session = BookingSession.objects.filter(
                owner_session=request.user
                ).order_by('-created_at').first()
            if not session:
                session = BookingSession(
                    owner_session=request.user,
                    title=f'Session from {timezone.now().strftime("%d.%m.%Y %H:%M")}',
                )
                session.save()
                
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        slot = TimeSlot(
            owner=request.user,
            session=session,    
            start_time=start_time,
            end_time=end_time)

        try:
            slot.save()
            messages.success(request, 'Slot successfully created!')
            return redirect('bookings:my_slots')
        except Exception as e :
            messages.error(request, f'Error creating slot :{str(e)}')
    
    sessions = BookingSession.objects.filter(
        owner_session=request.user).order_by('-created_at')
    context = {
        'sessions':sessions,
        'active_session': sessions.first() if sessions.exists() else None
    }
    return render(request, 'bookings/create_slot.html', context)

@login_required
def dashboard(request):
    owner = request.user

    session_count = BookingSession.objects.filter(
        owner_session=owner).count()
    slots_count = TimeSlot.objects.filter(
        owner=owner).count()
    booking_count = TimeSlot.objects.filter(
        owner=owner, is_booked=True).count()
    
    context = {
        'session_count':session_count,
        'booking_count':booking_count,
        'slots_count':slots_count,
    }
    return render(request, 'bookings/dashboard.html', context)


def public_view(request, public_link):  
    try:
        session = BookingSession.objects.get(public_link=public_link)
        
        free_slots = session.session_slots.filter(
            is_booked=False,
            start_time__gt=timezone.now()
        ).order_by('start_time')
        
        context = {
            'session': session,
            'slots': free_slots,
        }
        
        return render(request, 'bookings/public_view.html', context)
        
    except BookingSession.DoesNotExist:
        messages.error(request, 'Session not found')
        return render(request, 'bookings/error.html', {'error': 'Session not found'})

def book_slot(request, public_link, slot_id):
    try:
        slot = TimeSlot.objects.get(id=slot_id, session__public_link=public_link)

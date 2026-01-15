from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from .models import TimeSlot, BookingSession
from .forms import UserRegistrationForm

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
            slot.full_clean()  
            slot.save()
            messages.success(request, 'Slot successfully created!')
            return redirect('bookings:my_slots')
        except ValidationError as e:
           
            messages.error(request, str(e.message_dict.get('__all__', [e.message])[0]))
        except Exception as e:
            messages.error(request, f'Error creating slot: {str(e)}')
    
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
    
    # Последние бронирования
    recent_bookings = TimeSlot.objects.filter(
        owner=owner,
        is_booked=True
    ).order_by('-booked_at')[:5]
    
    # Активные сессии (с хотя бы одним слотом)
    active_sessions = BookingSession.objects.filter(
        owner_session=owner
    ).annotate(
        slots_count=Count('session_slots')
    ).filter(slots_count__gt=0).order_by('-created_at')[:5]
    
    context = {
        'session_count': session_count,
        'booking_count': booking_count,
        'slots_count': slots_count,
        'recent_bookings': recent_bookings,
        'active_sessions': active_sessions,
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
        
        if request.method == 'POST':
            if slot.is_booked:
                messages.error(request, 'Slot already booked')
                return redirect('bookings:public_view', public_link=public_link)
            
            if request.user.is_authenticated:
                slot.booked_by = request.user
            else:
                # Для гостей - сохранить имя
                guest_name = request.POST.get('guest_name', '').strip()
                if not guest_name:
                    messages.error(request, 'Please provide your name')
                    context = {
                        'slot': slot,
                        'public_link': public_link,
                    }
                    return render(request, 'bookings/book_slot.html', context)
                slot.guest_name = guest_name
            
            slot.save()
            messages.success(request, 'Slot booked successfully!')
            return redirect('bookings:public_view', public_link=public_link)
        
        context = {
            'slot': slot,
            'public_link': public_link,
        }
        return render(request, 'bookings/book_slot.html', context)
        
    except TimeSlot.DoesNotExist:
        messages.error(request, 'Slot not found')
        return redirect('bookings:public_view', public_link=public_link)


def register(request):
    """
    User registration view
    """
    if request.user.is_authenticated:
        return redirect('bookings:dashboard')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created successfully.')
            return redirect('bookings:dashboard')
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'registration/register.html', context)



@login_required
def sessions_list(request):
    """
    List of all session
    """
    sessions = BookingSession.objects.filter(
        owner_session=request.user
    ).order_by('-created_at')
    
    context = {
        'sessions': sessions,
    }
    return render(request, 'bookings/sessions_list.html', context)


@login_required
def create_session(request):
    """
    Создание новой сессии
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not title:
            messages.error(request, 'Title is required')
            return redirect('bookings:create_session')
        
        session = BookingSession(
            owner_session=request.user,
            title=title,
            description=description if description else None,
        )
        session.save()
        
        messages.success(request, f'Session "{title}" created successfully!')
        return redirect('bookings:sessions_list')
    
    return render(request, 'bookings/create_session.html')


@login_required
def edit_session(request, session_id):
    """
    Редактирование сессии
    """
    session = get_object_or_404(BookingSession, id=session_id, owner_session=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not title:
            messages.error(request, 'Title is required')
            return redirect('bookings:edit_session', session_id=session_id)
        
        session.title = title
        session.description = description if description else None
        session.save()
        
        messages.success(request, 'Session updated successfully!')
        return redirect('bookings:sessions_list')
    
    context = {
        'session': session,
    }
    return render(request, 'bookings/edit_session.html', context)


@login_required
def delete_session(request, session_id):
    """
    Удаление сессии
    """
    session = get_object_or_404(BookingSession, id=session_id, owner_session=request.user)
    
    if request.method == 'POST':
        session_title = session.title
        session.delete()
        messages.success(request, f'Session "{session_title}" deleted successfully!')
        return redirect('bookings:sessions_list')
    
    context = {
        'session': session,
    }
    return render(request, 'bookings/delete_session.html', context)


# ==================== УПРАВЛЕНИЕ СЛОТАМИ ====================

@login_required
def delete_slot(request, slot_id):
    """
    Удаление слота
    """
    slot = get_object_or_404(TimeSlot, id=slot_id, owner=request.user)
    
    if request.method == 'POST':
        slot.delete()
        messages.success(request, 'Slot deleted successfully!')
        return redirect('bookings:my_slots')
    
    context = {
        'slot': slot,
    }
    return render(request, 'bookings/delete_slot.html', context)


@login_required
def cancel_booking(request, slot_id):
    """
    Отмена бронирования (только владелец слота может отменить)
    """
    slot = get_object_or_404(TimeSlot, id=slot_id, owner=request.user)
    
    if request.method == 'POST':
        if not slot.is_booked:
            messages.warning(request, 'This slot is not booked')
            return redirect('bookings:my_slots')
        
        slot.booked_by = None
        slot.guest_name = None
        slot.booked_at = None
        slot.save()  # Автоматически обновит is_booked через save()
        
        messages.success(request, 'Booking cancelled successfully!')
        return redirect('bookings:my_slots')
    
    context = {
        'slot': slot,
    }
    return render(request, 'bookings/cancel_booking.html', context)




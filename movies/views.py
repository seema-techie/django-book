from io import BytesIO
import qrcode

from django.http import HttpResponse
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

from .models import Movie, Theater, Seat, Booking


# 1. Display all movies and search movies
def movie_list(request):
    search_query = request.GET.get('search')

    if search_query:
        movies = Movie.objects.filter(name__icontains=search_query)
    else:
        movies = Movie.objects.all()

    return render(request, 'movies/movie_list.html', {
        'movies': movies
    })


# 2. Display theaters for a selected movie
def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)

    return render(request, 'movies/theater_list.html', {
        'movie': movie,
        'theaters': theaters
    })


# 3. Select and book seats
@login_required(login_url='/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        selected_seats = list(dict.fromkeys(
            request.POST.getlist('seats')
        ))

        if not selected_seats:
            return render(request, 'movies/seat_selection.html', {
                'theater': theater,
                'seats': seats,
                'error': 'Please select at least one seat.'
            })

        selected_objects = list(
            Seat.objects.filter(
                id__in=selected_seats,
                theater=theater
            )
        )

        if len(selected_objects) != len(selected_seats):
            return render(request, 'movies/seat_selection.html', {
                'theater': theater,
                'seats': seats,
                'error': 'Invalid seat selection.'
            })

        try:
            with transaction.atomic():
                locked_seats = list(
                    Seat.objects.select_for_update().filter(
                        id__in=selected_seats,
                        theater=theater
                    ).order_by('id')
                )

                booked_seats = [
                    seat.seat_number
                    for seat in locked_seats
                    if seat.is_booked
                ]

                if booked_seats:
                    return render(request, 'movies/seat_selection.html', {
                        'theater': theater,
                        'seats': Seat.objects.filter(theater=theater),
                        'error': 'Already booked: ' + ', '.join(booked_seats)
                    })

                created_bookings = []

                for seat in locked_seats:
                    booking = Booking.objects.create(
                        user=request.user,
                        seat=seat,
                        movie=theater.movie,
                        theater=theater
                    )
                    created_bookings.append(booking.id)

                Seat.objects.filter(
                    id__in=selected_seats,
                    theater=theater
                ).update(is_booked=True)

        except IntegrityError:
            return render(request, 'movies/seat_selection.html', {
                'theater': theater,
                'seats': Seat.objects.filter(theater=theater),
                'error': 'One or more seats have already been booked. Please select again.'
            })

        booking_ids = ','.join(map(str, created_bookings))

        return redirect(
            f"{reverse('booking_confirmation')}?ids={booking_ids}"
        )

    return render(request, 'movies/seat_selection.html', {
        'theater': theater,
        'seats': seats
    })


# 4. Display booking confirmation
@login_required(login_url='/login/')
def booking_confirmation(request):
    booking_ids = request.GET.get('ids', '')

    if not booking_ids:
        return redirect('profile')

    ids = booking_ids.split(',')

    if not all(value.isdigit() for value in ids):
        return HttpResponse('Invalid booking reference.', status=400)

    bookings = Booking.objects.filter(
        id__in=ids,
        user=request.user
    ).select_related(
        'movie', 'theater', 'seat'
    ).order_by('id')

    if not bookings.exists():
        return redirect('profile')

    first_booking = bookings.first()

    return render(request, 'movies/booking_confirmation.html', {
        'bookings': bookings,
        'movie': first_booking.movie,
        'theater': first_booking.theater,
        'booking_ids': ','.join(str(b.id) for b in bookings)
    })


# 5. Generate and download PDF ticket with QR code
@login_required(login_url='/login/')
def download_ticket(request):
    booking_ids = request.GET.get('ids', '')

    if not booking_ids:
        return redirect('profile')

    ids = booking_ids.split(',')

    if not all(value.isdigit() for value in ids):
        return HttpResponse('Invalid booking reference.', status=400)

    if len(ids) != len(set(ids)):
        return HttpResponse('Invalid booking reference.', status=400)

    bookings = list(
        Booking.objects.filter(
            id__in=ids,
            user=request.user
        ).select_related(
            'movie', 'theater', 'seat'
        ).order_by('id')
    )

    if not bookings or len(bookings) != len(ids):
        return HttpResponse('Ticket not found.', status=404)

    # Get movie and theater details
    movie = bookings[0].movie
    theater = bookings[0].theater

    # Ensure all bookings belong to the same movie and theater
    if any(
        booking.movie_id != movie.id or booking.theater_id != theater.id
        for booking in bookings
    ):
        return HttpResponse('Invalid ticket selection.', status=400)

    # Prepare ticket details
    seat_numbers = ', '.join(
        booking.seat.seat_number for booking in bookings
    )

    booking_reference = ', '.join(
        str(booking.id) for booking in bookings
    )

    # Generate QR code
    qr_data = (
        f"BOOKING REFERENCE: {booking_reference}\n"
        f"MOVIE: {movie.name}\n"
        f"THEATER: {theater.name}\n"
        f"SHOW TIME: {theater.time}\n"
        f"SEATS: {seat_numbers}"
    )

    qr_image = qrcode.make(qr_data)

    qr_buffer = BytesIO()
    qr_image.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    # Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    pdf.setTitle('Movie Booking Ticket')

    # Ticket heading
    pdf.setFont('Helvetica-Bold', 22)
    pdf.drawCentredString(
        width / 2,
        height - 65,
        'MOVIE TICKET'
    )

    # Movie name
    pdf.setFont('Helvetica-Bold', 15)
    pdf.drawString(
        55,
        height - 125,
        movie.name[:65]
    )

    # Booking information
    pdf.setFont('Helvetica', 12)

    details = [
        f"Booking Reference: {booking_reference}",
        f"Customer: {request.user.username}",
        f"Theater: {theater.name}",
        f"Show Date and Time: {theater.time.strftime('%d %B %Y, %I:%M %p')}",
        f"Seats: {seat_numbers}",
        f"Booking Date: {bookings[0].booked_at.strftime('%d %B %Y, %I:%M %p')}",
    ]

    y = height - 175

    for detail in details:
        pdf.drawString(55, y, detail[:90])
        y -= 30

    # QR code
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(
        55,
        y - 10,
        'Scan your QR code for ticket details'
    )

    pdf.drawImage(
        ImageReader(qr_buffer),
        width - 180,
        height - 390,
        width=120,
        height=120
    )

    # Footer
    pdf.setFont('Helvetica', 10)
    pdf.drawCentredString(
        width / 2,
        70,
        'Thank you for booking with BookMySeat!'
    )

    pdf.save()
    buffer.seek(0)

    # Return downloadable PDF
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        'attachment; filename="movie_ticket.pdf"'
    )

    return response

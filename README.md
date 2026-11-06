# BookMySeat – Movie Ticket Booking System

A web-based movie ticket booking application built using **Python and Django**. BookMySeat allows users to explore movies, view available theatres and showtimes, select seats, and complete their ticket booking online.

**Live Demo:** https://django-book-snowy.vercel.app/

**GitHub Repository:** https://github.com/seema-techie/django-book

## Features

- **User Authentication:** User registration, login and logout.
- **Movie Listing:** Browse available movies with details.
- **Theatre Selection:** View theatres and available showtimes.
- **Seat Selection:** Select seats for a particular show.
- **Booking Management:** Book tickets and maintain booking records.
- **Booking Confirmation:** View confirmation after successfully booking tickets.
- **Responsive Interface:** HTML and CSS-based user interface.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web framework |
| HTML5 | Page structure |
| CSS3 | Styling and layout |
| JavaScript | Frontend interactions |
| SQLite | Database |
| Git & GitHub | Version control |

## Application Workflow

1. Open the application.
2. Register or log in to your account.
3. Browse the available movies.
4. Select a movie and theatre.
5. Choose a show and select seats.
6. Confirm your booking.

## Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the repository

```bash
git clone https://github.com/seema-techie/django-book.git
```

### 2. Navigate to the project folder

```bash
cd django-book
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows:**

```powershell
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

Open your browser and visit:

```text
http://127.0.0.1:8000/
```

## Project Structure

```text
django-book/
│
├── bookmyseat/       # Main Django project configuration
├── movies/           # Movie, theatre, seat and booking functionality
├── users/            # User authentication and account functionality
├── templates/        # HTML templates
├── manage.py         # Django management utility
├── requirements.txt  # Project dependencies
├── vercel.json       # Deployment configuration
└── README.md         # Project documentation
```

## Project Objective

The objective of BookMySeat is to develop a movie ticket booking platform that demonstrates practical implementation of Django, database management, user authentication, and frontend-backend integration.

## Developer

**Seema Saud**

B.Tech – Computer Science and Engineering  
Specialization: Artificial Intelligence and Analytics  
MIT ADT University, Pune

- **GitHub:** https://github.com/seema-techie
- **LinkedIn:** https://linkedin.com/in/seema-saud-77527a25b

---

⭐ If you find this project interesting, consider giving the repository a star!
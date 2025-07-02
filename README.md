# FinFinance

FinFinance is a robust Django-based web application designed to streamline personal and business financial management. It empowers users to create budgets, track expenses, book financial experts, and gain insights through an intuitive admin dashboard. With role-based access (Normal Users, Finance Experts, Company Staff), FinFinance offers a secure and scalable platform for financial planning and collaboration.

## Features

- **Budget Management**: Create, view, and export budgets as PDFs.
- **Expense Tracking**: Add and monitor expenses linked to budgets.
- **Expert Booking**: Normal users can book Finance Experts for consultations.
- **Admin Dashboard**: Company Staff access a dynamic dashboard with:
  - User & Budget analytics (bar chart).
  - User role distribution (donut chart).
  - Budget trends (area chart).
  - Recent bookings and top budget managers.
- **User Management**: Admins can activate/deactivate users.
- **Expert Booking History**: Admins view all expert bookings with details.
- **Notifications & Feedback**: Real-time booking notifications and post-session feedback.
- **EMI Calculator**: Tool for calculating loan EMIs.
- **Role-Based Access**:
  - Normal Users: Budgets, expenses, expert booking.
  - Finance Experts: Manage appointments and bookings.
  - Company Staff: Full admin controls.

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS (Bootstrap), JavaScript (jQuery)
- **Charts**: ApexCharts for data visualization
- **Database**: SQLite (default, configurable for PostgreSQL/MySQL)
- **Static Files**: Django static file management
- **Dependencies**: See `requirements.txt`

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/denmarkdeni/FinFinance.git
   cd FinFinance
   ```

2. **Set Up Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:

   - Copy `.env.example` to `.env` and update settings (e.g., `SECRET_KEY`, `DATABASE_URL`).
   - Example `.env`:

     ```env
     SECRET_KEY=your-secret-key
     DEBUG=True
     DATABASE_URL=sqlite:///db.sqlite3
     ```

5. **Apply Migrations**:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create Superuser**:

   ```bash
   python manage.py createsuperuser
   ```

7. **Collect Static Files**:

   ```bash
   python manage.py collectstatic
   ```

8. **Run Development Server**:

   ```bash
   python manage.py runserver
   ```

   Access at `http://127.0.0.1:8000`.

## Project Structure

```
finfinance/
├── finfinance/
│   ├── settings.py       # Django settings
│   ├── urls.py           # Main URL configurations
│   ├── views.py          # Core views
│   └── models.py         # Database models (User, Profile, Budget, Booking, etc.)
├── static/
│   └── dashFiles/
│       ├── css/          # Custom styles
│       ├── js/           # JavaScript (dashboard.js, ApexCharts)
│       └── images/       # Profile images, assets
├── templates/
│   └── dashboard/
│       ├── admin.html    # Admin dashboard
│       ├── user_management.html  # User management page
│       ├── experts_history.html # Expert booking history
│       └── ...           # Other templates
├── requirements.txt      # Python dependencies
├── manage.py             # Django management script
└── README.md             # Project documentation
```

## Key URLs

- **Admin Dashboard**: `/dashboard/admin/` (Company Staff only)
- **User Management**: `/dashboard/users/` (Company Staff only)
- **Expert Booking History**: `/dashboard/experts/history/` (Company Staff only)
- **Budgets**: `/budgets/` (Normal Users)
- **Expert Booking**: `/experts/` (Normal Users)
- **Booking History**: `/bookings/history/` (Normal Users, Finance Experts)
- **EMI Calculator**: `/emi-calculator/` (All users)

## Models

- **User**: Extends Django’s `AbstractUser` with `Profile` for roles (`NormalUser`, `FinanceExpert`, `CompanyStaff`).
- **Profile**: Stores user details (role, occupation, profile picture).
- **Budget**: Tracks user budgets (`month`, `total_budgeted`).
- **Booking**: Manages expert bookings (`user`, `expert`, `date_time`, `status`).
- **Notification**: Sends booking-related alerts.
- **Feedback**: Stores post-booking ratings and comments.
- **Expense**: Links expenses to budgets.

## Usage

1. **As Normal User**:

   - Log in, create budgets, add expenses, book experts.
   - View booking history and submit feedback.

2. **As Finance Expert**:

   - Manage appointments, update booking statuses.
   - Receive notifications for new bookings.

3. **As Company Staff**:

   - Access dashboard for analytics (users, budgets, bookings).
   - Manage users (activate/deactivate).
   - View all expert booking history.

4. **Setup Test Data**:

   ```bash
   python manage.py shell
   ```

   ```python
   from django.contrib.auth.models import User
   from finfinance.models import Profile, Budget, Booking
   from datetime import date
   user = User.objects.create_user('testuser', 'test@example.com', 'password')
   Profile.objects.create(user=user, role='NormalUser')
   Budget.objects.create(user=user, month=date(2025, 1, 1), total_budgeted=50000)
   ```

## Dependencies

- Django
- Bootstrap (CDN)
- jQuery (CDN: `https://code.jquery.com/jquery-3.6.0.min.js`)
- ApexCharts (CDN: `https://cdn.jsdelivr.net/npm/apexcharts`)

Install Python dependencies:

```bash
pip install django
```

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit changes: `git commit -m "Add feature"`.
4. Push to branch: `git push origin feature-name`.
5. Submit a pull request.

## License

MIT License. See `LICENSE` file.

## Contact

For issues or feature requests, open a GitHub issue or contact `mariadeniston111@example.com`.

---

**FinFinance**: Empowering financial freedom with simplicity and insight! 🚀
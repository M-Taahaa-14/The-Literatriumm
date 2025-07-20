import random
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator



class BookCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

def generate_unique_isbn():
    from .models import Book  
    while True:
        isbn = str(random.randint(1000000000000, 9999999999999))
        if not Book.objects.filter(isbn=isbn).exists():
            return isbn


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE)
    total_copies = models.PositiveIntegerField()
    available_copies = models.PositiveIntegerField()
    isbn = models.CharField(
        max_length=13,
        unique=True,
        default=generate_unique_isbn,
        validators=[
            RegexValidator(
                regex=r'^\d{13}$',
                message="ISBN must be exactly 13 digits."
            )
        ],
    )
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    def borrow(self):
        if self.available_copies < 1:
            raise ValueError("No copies available.")
        self.available_copies -= 1
        self.save()

    def return_copy(self):
        if self.available_copies >= self.total_copies:
            raise ValueError("All copies are already returned.")
        self.available_copies += 1
        self.save()

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)
    


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    address = models.TextField()
    phone = models.CharField(max_length=13)
    # is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    @property
    def is_admin(self):
        return self.user.username == 'admin'

    @property
    def initials(self):
        parts = self.full_name.strip().split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        elif parts:
            return parts[0][0].upper()
        return ""



from datetime import timedelta
class BorrowRecord(models.Model):
    DEFAULT_FINE_PER_DAY = Decimal('10.00')  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    borrow_date = models.DateTimeField(default=timezone.now)
    return_date = models.DateTimeField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    due_date = models.DateTimeField(null=True, blank=True)
    fine = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, validators=[MinValueValidator(Decimal('0.00'))])
    
    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=12)
        super().save(*args, **kwargs)

    def return_book(self):
        if self.is_returned:
            raise ValueError("Already returned.")

        self.book.return_copy()
        self.is_returned = True
        self.return_date = timezone.now()

        if self.due_date and self.return_date > self.due_date:
            days_overdue = (self.return_date - self.due_date).days
            if days_overdue > 0:
                self.fine = self.DEFAULT_FINE_PER_DAY * Decimal(days_overdue)
                Notification.objects.create(
                    user=self.user,
                    message=f"You were {days_overdue} days late returning '{self.book.title}'. A fine of Rs.{self.fine} has been added."
                )
            else:
                self.fine = Decimal('0.00')
        else:
            self.fine = Decimal('0.00')

        self.save()


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    content = models.TextField(blank=True)  
    rating = models.IntegerField() 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')  

    def __str__(self):
        return f"{self.user.username} rated {self.book.title} ⭐{self.rating}"



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}"
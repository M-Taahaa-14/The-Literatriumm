"""
Django management command to sync existing data to PostgreSQL analytics database.
This should be run once to populate the analytics database with existing data.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from library_app.models import BookCategory, Book, BorrowRecord, Review
from library_app.signals import sync_handler


class Command(BaseCommand):
    help = 'Sync existing Django data to PostgreSQL analytics database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Sync specific model: users, categories, books, borrowings, reviews, or all',
            default='all'
        )

    def handle(self, *args, **options):
        model = options['model'].lower()
        
        if model in ['all', 'users']:
            self.sync_users()
        
        if model in ['all', 'categories']:
            self.sync_categories()
            
        if model in ['all', 'books']:
            self.sync_books()
            
        if model in ['all', 'borrowings']:
            self.sync_borrowings()
            
        if model in ['all', 'reviews']:
            self.sync_reviews()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully synced data to analytics database!')
        )

    def sync_users(self):
        """Sync all users to PostgreSQL."""
        self.stdout.write('Syncing users...')
        users = User.objects.all()
        for user in users:
            sync_handler.sync_user(user)
        self.stdout.write(f'Synced {users.count()} users')

    def sync_categories(self):
        """Sync all categories to PostgreSQL."""
        self.stdout.write('Syncing categories...')
        categories = BookCategory.objects.all()
        for category in categories:
            sync_handler.sync_category(category)
        self.stdout.write(f'Synced {categories.count()} categories')

    def sync_books(self):
        """Sync all books to PostgreSQL."""
        self.stdout.write('Syncing books...')
        books = Book.objects.all()
        for book in books:
            sync_handler.sync_book(book)
        self.stdout.write(f'Synced {books.count()} books')

    def sync_borrowings(self):
        """Sync all borrowings to PostgreSQL."""
        self.stdout.write('Syncing borrowings...')
        borrowings = BorrowRecord.objects.all()
        for borrowing in borrowings:
            sync_handler.sync_borrowing(borrowing)
        self.stdout.write(f'Synced {borrowings.count()} borrowings')

    def sync_reviews(self):
        """Sync all reviews to PostgreSQL."""
        self.stdout.write('Syncing reviews...')
        reviews = Review.objects.all()
        for review in reviews:
            sync_handler.sync_review(review)
        self.stdout.write(f'Synced {reviews.count()} reviews')

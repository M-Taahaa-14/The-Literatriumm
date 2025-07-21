from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
import psycopg2
import logging
from datetime import datetime

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


logger = logging.getLogger(__name__)

class PostgreSQLSyncHandler:
    """Handles PostgreSQL synchronization for Django models."""
    
    def __init__(self):
        self.postgres_config = {
            'host': getattr(settings, 'ANALYTICS_DB_HOST', 'localhost'),
            'port': getattr(settings, 'ANALYTICS_DB_PORT', '5432'),
            'database': getattr(settings, 'ANALYTICS_DB_NAME', 'library_analytics'),
            'user': getattr(settings, 'ANALYTICS_DB_USER', 'postgres'),
            'password': getattr(settings, 'ANALYTICS_DB_PASSWORD', 'password')
        }
        self.enabled = getattr(settings, 'ENABLE_ANALYTICS_SYNC', False)
    
    def get_connection(self):
        """Get PostgreSQL connection."""
        if not self.enabled:
            return None
            
        try:
            return psycopg2.connect(**self.postgres_config)
        except Exception as e:
            logger.error(f"Failed to connect to analytics database: {e}")
            return None
    
    def sync_user(self, user_instance):
        """Sync user to PostgreSQL."""
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO auth_user (id, username, email, first_name, last_name, 
                                     is_staff, is_active, date_joined, full_name, address, phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    email = EXCLUDED.email,
                    first_name = EXCLUDED.first_name,
                    last_name = EXCLUDED.last_name,
                    is_staff = EXCLUDED.is_staff,
                    is_active = EXCLUDED.is_active
            """, (
                user_instance.id,
                user_instance.username,
                user_instance.email,
                user_instance.first_name,
                user_instance.last_name,
                user_instance.is_staff,
                user_instance.is_active,
                user_instance.date_joined,
                getattr(user_instance.userprofile, 'full_name', '') if hasattr(user_instance, 'userprofile') else '',
                getattr(user_instance.userprofile, 'address', '') if hasattr(user_instance, 'userprofile') else '',
                getattr(user_instance.userprofile, 'phone', '') if hasattr(user_instance, 'userprofile') else ''
            ))
            
            conn.commit()
            logger.info(f"Synced user {user_instance.id} to analytics database")
            
        except Exception as e:
            logger.error(f"Failed to sync user {user_instance.id}: {e}")
        finally:
            conn.close()
    
    def sync_category(self, category_instance):
        """Sync category to PostgreSQL."""
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO library_app_bookcategory (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name
            """, (
                category_instance.id,
                category_instance.name
            ))
            
            conn.commit()
            logger.info(f"Synced category {category_instance.id} to analytics database")
            
        except Exception as e:
            logger.error(f"Failed to sync category {category_instance.id}: {e}")
        finally:
            conn.close()
    
    def sync_book(self, book_instance):
        """Sync book to PostgreSQL."""
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO library_app_book (id, title, author, isbn, total_copies,
                                            available_copies, category_id, cover_image)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    author = EXCLUDED.author,
                    isbn = EXCLUDED.isbn,
                    total_copies = EXCLUDED.total_copies,
                    available_copies = EXCLUDED.available_copies,
                    category_id = EXCLUDED.category_id,
                    cover_image = EXCLUDED.cover_image
            """, (
                book_instance.id,
                book_instance.title,
                book_instance.author,
                book_instance.isbn,
                book_instance.total_copies,
                book_instance.available_copies,
                book_instance.category_id,
                str(book_instance.cover_image) if book_instance.cover_image else None
            ))
            
            conn.commit()
            logger.info(f"Synced book {book_instance.id} to analytics database")
            
        except Exception as e:
            logger.error(f"Failed to sync book {book_instance.id}: {e}")
        finally:
            conn.close()
    
    def sync_borrowing(self, borrowing_instance):
        """Sync borrowing to PostgreSQL - CRITICAL for analytics."""
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO library_app_borrowrecord (id, user_id, book_id, borrow_date, due_date,
                                                    return_date, is_returned, fine)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    return_date = EXCLUDED.return_date,
                    is_returned = EXCLUDED.is_returned,
                    fine = EXCLUDED.fine
            """, (
                borrowing_instance.id,
                borrowing_instance.user_id,
                borrowing_instance.book_id,
                borrowing_instance.borrow_date,
                borrowing_instance.due_date,
                borrowing_instance.return_date,
                borrowing_instance.is_returned,
                float(borrowing_instance.fine) if borrowing_instance.fine else 0.0
            ))
            
            conn.commit()
            logger.info(f"Synced borrowing {borrowing_instance.id} to analytics database")
            
        except Exception as e:
            logger.error(f"Failed to sync borrowing {borrowing_instance.id}: {e}")
        finally:
            conn.close()


# Initialize sync handler
sync_handler = PostgreSQLSyncHandler()


# Django Signal Receivers
from .models import BookCategory, Book, BorrowRecord

@receiver(post_save, sender='auth.User')
def sync_user_to_analytics(sender, instance, created, **kwargs):
    """Sync user changes to analytics database."""
    sync_handler.sync_user(instance)


@receiver(post_save, sender=BookCategory)
def sync_category_to_analytics(sender, instance, created, **kwargs):
    """Sync category changes to analytics database."""
    sync_handler.sync_category(instance)


@receiver(post_save, sender=Book)
def sync_book_to_analytics(sender, instance, created, **kwargs):
    """Sync book changes to analytics database."""
    sync_handler.sync_book(instance)


@receiver(post_save, sender=BorrowRecord)
def sync_borrowing_to_analytics(sender, instance, created, **kwargs):
    """Sync borrowing changes to analytics database - MOST IMPORTANT."""
    sync_handler.sync_borrowing(instance)

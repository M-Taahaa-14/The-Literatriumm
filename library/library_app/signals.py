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
from .models import BookCategory, Book, BorrowRecord, Review, UserProfile


logger = logging.getLogger(__name__)

class PostgreSQLSyncHandler:
    """Handles PostgreSQL synchronization for Django models."""
    
    def __init__(self):
        self.postgres_config = {
            'host': getattr(settings, 'ANALYTICS_DB_HOST'),
            'port': getattr(settings, 'ANALYTICS_DB_PORT'),
            'database': getattr(settings, 'ANALYTICS_DB_NAME'),
            'user': getattr(settings, 'ANALYTICS_DB_USER'),
            'password': getattr(settings, 'ANALYTICS_DB_PASSWORD')
        }
        self.enabled = getattr(settings, 'ENABLE_ANALYTICS_SYNC', False)
    
    def get_connection(self):
        if not self.enabled:
            return None
            
        try:
            return psycopg2.connect(**self.postgres_config)
        except Exception as e:
            logger.error(f"Failed to connect to analytics database: {e}")
            return None
    
    def ensure_tables_exist(self):
        """Ensure all required tables exist in PostgreSQL."""
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Create auth_user table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auth_user (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(150) UNIQUE NOT NULL,
                    email VARCHAR(254),
                    first_name VARCHAR(30),
                    last_name VARCHAR(150),
                    is_staff BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    date_joined TIMESTAMP,
                    full_name VARCHAR(150),
                    address TEXT,
                    phone VARCHAR(13)
                )
            """)
            
            # Create category table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS library_app_bookcategory (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100) UNIQUE NOT NULL
                )
            """)
            
            # Create book table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS library_app_book (
                    id INTEGER PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    author VARCHAR(200) NOT NULL,
                    isbn VARCHAR(13) UNIQUE,
                    total_copies INTEGER DEFAULT 1,
                    available_copies INTEGER DEFAULT 1,
                    cover_image VARCHAR(255),
                    category_id INTEGER REFERENCES library_app_bookcategory(id)
                )
            """)
            
            # Create borrowing table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS library_app_borrowrecord (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    book_id INTEGER REFERENCES library_app_book(id),
                    borrow_date TIMESTAMP NOT NULL,
                    return_date TIMESTAMP,
                    due_date TIMESTAMP,
                    is_returned BOOLEAN DEFAULT FALSE,
                    fine NUMERIC(6,2) DEFAULT 0.00
                )
            """)
            
            # Create review table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS library_app_review (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    book_id INTEGER REFERENCES library_app_book(id),
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Ensured all analytics tables exist")
            
        except Exception as e:
            logger.error(f"Failed to ensure tables exist: {e}")
        finally:
            conn.close()
    
    def sync_user(self, user_instance):
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Get user profile data safely
            full_name = ''
            address = ''
            phone = ''
            
            try:
                if hasattr(user_instance, 'userprofile'):
                    profile = user_instance.userprofile
                    full_name = getattr(profile, 'full_name', '')
                    address = getattr(profile, 'address', '')
                    phone = getattr(profile, 'phone', '')
            except Exception:
                # If userprofile doesn't exist, use empty strings
                pass
            
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
                    is_active = EXCLUDED.is_active,
                    full_name = EXCLUDED.full_name,
                    address = EXCLUDED.address,
                    phone = EXCLUDED.phone
            """, (
                user_instance.id,
                user_instance.username,
                user_instance.email or '',
                user_instance.first_name or '',
                user_instance.last_name or '',
                user_instance.is_staff,
                user_instance.is_active,
                user_instance.date_joined,
                full_name,
                address,
                phone
            ))
            
            conn.commit()
            logger.info(f"Synced user {user_instance.id} to analytics database")
            
        except Exception as e:
            logger.error(f"Failed to sync user {user_instance.id}: {e}")
            conn.rollback()
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
            conn.rollback()
        finally:
            conn.close()
    


    def sync_book(self, book_instance):
        """Sync book to PostgreSQL."""
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Ensure category exists first
            cursor.execute("""
                INSERT INTO library_app_bookcategory (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (
                book_instance.category.id,
                book_instance.category.name
            ))
            
            # Now sync the book
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
            conn.rollback()
        finally:
            conn.close()
    


    def sync_borrowing(self, borrowing_instance):
        """Sync borrowing to PostgreSQL - CRITICAL for analytics."""
        conn = self.get_connection()
        if not conn:
            return
            
        try:
            cursor = conn.cursor()
            
            # Ensure user exists first (but we can't create it here without profile info)
            # So we'll skip this and rely on user sync from auth signals
            
            # Ensure book exists first
            try:
                cursor.execute("""
                    INSERT INTO library_app_bookcategory (id, name)
                    VALUES (%s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    borrowing_instance.book.category.id,
                    borrowing_instance.book.category.name
                ))
                
                cursor.execute("""
                    INSERT INTO library_app_book (id, title, author, isbn, total_copies,
                                                available_copies, category_id, cover_image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    borrowing_instance.book.id,
                    borrowing_instance.book.title,
                    borrowing_instance.book.author,
                    borrowing_instance.book.isbn,
                    borrowing_instance.book.total_copies,
                    borrowing_instance.book.available_copies,
                    borrowing_instance.book.category_id,
                    str(borrowing_instance.book.cover_image) if borrowing_instance.book.cover_image else None
                ))
            except Exception:
                # If book sync fails, continue with borrowing sync
                pass
            
            # Now sync the borrowing record
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
            print(f"✅ SUCCESS: Synced borrowing {borrowing_instance.id} to analytics database")
            
        except Exception as e:
            logger.error(f"Failed to sync borrowing {borrowing_instance.id}: {e}")
            logger.error(f"Error details: {str(e)}")
            print(f"❌ ERROR: Failed to sync borrowing {borrowing_instance.id}: {e}")
            conn.rollback()
        finally:
            conn.close()


    def sync_review(self, review_instance):
            """Sync review to PostgreSQL - for ratings analytics."""
            conn = self.get_connection()
            if not conn:
                return
                
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO library_app_review (id, user_id, book_id, rating, comment, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        rating = EXCLUDED.rating,
                        comment = EXCLUDED.comment
                """, (
                    review_instance.id,
                    review_instance.user_id,
                    review_instance.book_id,
                    review_instance.rating,
                    review_instance.content,
                    review_instance.created_at
                ))
                
                conn.commit()
                logger.info(f"Synced review {review_instance.id} to analytics database")
                
            except Exception as e:
                logger.error(f"Failed to sync review {review_instance.id}: {e}")
            finally:
                conn.close()


# Initialize sync handler
sync_handler = PostgreSQLSyncHandler()

# Ensure tables exist on startup
try:
    sync_handler.ensure_tables_exist()
except Exception as e:
    logger.error(f"Failed to ensure tables exist on startup: {e}")

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


@receiver(post_save, sender=Review)
def sync_review_to_analytics(sender, instance, created, **kwargs):
    """Sync review changes to analytics database - for ratings analytics."""
    sync_handler.sync_review(instance)    


@receiver(post_save, sender=UserProfile)
def sync_user_profile_to_analytics(sender, instance, created, **kwargs):
    """Sync user profile changes - this will update the user in analytics database."""
    sync_handler.sync_user(instance.user)    


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)    
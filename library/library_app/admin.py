from django.contrib import admin
from .models import Book, BookCategory, BorrowRecord, UserProfile

admin.site.register(Book)
admin.site.register(BookCategory)
admin.site.register(BorrowRecord)
admin.site.register(UserProfile)


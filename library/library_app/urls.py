# from django.urls import path
# from django.views.generic import TemplateView

# app_name = 'library_app'
# urlpatterns = [
#     path('', TemplateView.as_view(template_name='library_app/home.html'), name='home'),
# ]

from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='home'),
    path('books/', views.list_books, name='list_books'),
    path('books/<int:book_id>/', views.book_detail, name='book_details'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('my-borrowings/', views.my_borrowings, name='my_borrowings'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_books, name='search_books'),
    path('category/<int:category_id>/', views.books_by_category, name='books_by_category'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/books/', views.admin_manage_books, name='admin_manage_books'),
    path('admin-panel/books/update/<int:book_id>/', views.admin_update_book, name='admin_update_book'),
    path('admin-panel/books/delete/<int:book_id>/', views.admin_delete_book, name='admin_delete_book'),
    path('admin-panel/books/add/', views.admin_add_book, name='admin_add_book'),
    path('admin-panel/borrowings/', views.admin_manage_borrowings, name='admin_manage_borrowings'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('admin-panel/categories/', views.manage_categories, name='admin_manage_categories'),
    path('admin-panel/categories/add/', views.add_category, name='add_category'),
    path('admin-panel/categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('admin-panel/categories/update/<int:category_id>/', views.update_category, name='update_category'),
    path('admin-panel/reviews/', views.manage_reviews, name='manage_reviews'),
    path('admin-panel/reviews/delete/<int:review_id>/', views.delete_review, name='delete_review'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
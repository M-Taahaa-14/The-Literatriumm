from django.urls import path
from .views import (
    BookListAPIView, BookDetailAPIView, CategoryListAPIView,
    BorrowRecordListAPIView, BorrowBookAPIView, ReturnBookAPIView,
    ReviewListCreateAPIView, ReviewDeleteAPIView, ReviewUpdateAPIView, UserProfileAPIView, LoginAPIView,
    NotificationListAPIView, MarkAllNotificationsReadAPIView,
    BookAdminViewSet, BookCategoryAdminViewSet, SignupAPIView, AdminDashboardAPIView,
    SearchBooksAPIView, BooksByCategoryAPIView, MyBorrowingsAPIView,
    ReviewListAdminAPIView, ReviewDeleteAdminAPIView,
    AdminBorrowingListAPIView, AdminBorrowingActionAPIView,
    TopRatedBooksAPIView, MostBorrowedBooksAPIView, CategoriesWithBooksAPIView, HomePageStatsAPIView
)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'admin/books', BookAdminViewSet, basename='admin-books')
router.register(r'admin/categories', BookCategoryAdminViewSet, basename='admin-categories')

urlpatterns = [
    path('login/', LoginAPIView.as_view(), name='login_api'),
    path('signup/', SignupAPIView.as_view(), name='signup_api'),
    path('books/', BookListAPIView.as_view(), name='api_books'),
    path('books/<int:id>/', BookDetailAPIView.as_view(), name='api_book_detail'),
    path('search/', SearchBooksAPIView.as_view(), name='api_search_books'),
    path('books/category/<int:category_id>/', BooksByCategoryAPIView.as_view(), name='api_books_by_category'),
    path('user_borrowings/', MyBorrowingsAPIView.as_view(), name='api_my_borrowings'),
    path('categories/', CategoryListAPIView.as_view(), name='api_categories'),
    path('borrowings/', BorrowRecordListAPIView.as_view(), name='api_borrowings'),
    path('borrow/<int:book_id>/', BorrowBookAPIView.as_view(), name='api_borrow_book'),
    path('return/<int:record_id>/', ReturnBookAPIView.as_view(), name='api_return_book'),
    path('reviews/', ReviewListCreateAPIView.as_view(), name='api_reviews'),
    path('reviews/<int:id>/', ReviewUpdateAPIView.as_view(), name='api_update_review'),
    path('reviews/<int:id>/delete/', ReviewDeleteAPIView.as_view(), name='api_delete_review'),
    path('profile/', UserProfileAPIView.as_view(), name='api_my_profile'),
    path('notifications/', NotificationListAPIView.as_view(), name='api_notifications'),
    path('notifications/mark_all_read/', MarkAllNotificationsReadAPIView.as_view(), name='api_mark_all_notifications_read'),
    path('admin/dashboard/', AdminDashboardAPIView.as_view(), name='api_admin_dashboard'),
    path('admin/reviews/', ReviewListAdminAPIView.as_view(), name='api_admin_reviews'),
    path('admin/reviews/<int:review_id>/delete/', ReviewDeleteAdminAPIView.as_view(), name='api_admin_review_delete'),
    path('admin/borrowings/', AdminBorrowingListAPIView.as_view(), name='api_admin_borrowings'),
    path('admin/borrowings/action/', AdminBorrowingActionAPIView.as_view(), name='api_admin_borrowing_action'),
    
    # Home page endpoints
    path('home/top-rated/', TopRatedBooksAPIView.as_view(), name='api_top_rated_books'),
    path('home/most-borrowed/', MostBorrowedBooksAPIView.as_view(), name='api_most_borrowed_books'),
    path('home/categories-with-books/', CategoriesWithBooksAPIView.as_view(), name='api_categories_with_books'),
    path('home/stats/', HomePageStatsAPIView.as_view(), name='api_home_stats'),
]

urlpatterns += router.urls

from rest_framework import generics, permissions, viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from library_app.models import Book, BorrowRecord, BookCategory, Review, UserProfile, Notification
from .serializers import BookSerializer, BorrowRecordSerializer, BookCategorySerializer, ReviewSerializer, UserProfileSerializer, NotificationSerializer, BookAdminSerializer, BookCategoryAdminSerializer, UserSignupSerializer
from .serializers import BorrowRecordAdminSerializer, ReviewAdminSerializer, BorrowRecordUserSerializer

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.shortcuts import get_object_or_404

from .permissions import IsAdminUserProfile

class AdminBookCreateAPIView(generics.CreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminUserProfile]


class LoginAPIView(APIView):
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            profile = user.userprofile
            return Response({
                'token': token.key,
                'is_admin': profile.is_admin,
                'full_name': profile.full_name
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class SignupAPIView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            from rest_framework.authtoken.models import Token
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username})
        return Response(serializer.errors, status=400)
    

# User Views
class BookListAPIView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookDetailAPIView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = 'id'


class SearchBooksAPIView(generics.ListAPIView):
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author']
    queryset = Book.objects.all()

class BooksByCategoryAPIView(generics.ListAPIView):
    serializer_class = BookSerializer
    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Book.objects.filter(category_id=category_id)
    
class CategoryListAPIView(generics.ListAPIView):
    queryset = BookCategory.objects.all()
    serializer_class = BookCategorySerializer


class BorrowRecordListAPIView(generics.ListAPIView):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]
    
class BorrowBookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, book_id):
        book = Book.objects.get(id=book_id)
        user = request.user

        if BorrowRecord.objects.filter(user=user, book=book, is_returned=False).exists():
            return Response({'error': 'You have already borrowed this book and not returned it yet.'}, status=400)

        if book.available_copies <= 0:
            return Response({'error': 'No copies available'}, status=400)

        BorrowRecord.objects.create(user=user, book=book)
        book.borrow()
        return Response({'message': f'Borrowed {book.title}'})


class ReturnBookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, record_id):
        record = BorrowRecord.objects.get(id=record_id, user=request.user)
        record.return_book()
        return Response({'message': f'Returned {record.book.title}'})

class MyBorrowingsAPIView(generics.ListAPIView):
    serializer_class = BorrowRecordUserSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        return BorrowRecord.objects.filter(user=self.request.user).order_by('-borrow_date')

class ReviewListCreateAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'book').order_by('-created_at')
        book_id = self.request.query_params.get('book')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ReviewDeleteAPIView(generics.DestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        # Users can only delete their own reviews
        return Review.objects.filter(user=self.request.user)

class UserProfileAPIView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

class NotificationListAPIView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

class MarkAllNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'success'})



# Admin Views
class AdminDashboardAPIView(APIView):
    permission_classes = [IsAdminUserProfile]
    def get(self, request):
        from django.contrib.auth.models import User
        from library_app.models import Book, BorrowRecord, Review, BookCategory
        return Response({
            'user_count': User.objects.count(),
            'book_count': Book.objects.count(),
            'borrow_count': BorrowRecord.objects.count(),
            'review_count': Review.objects.count(),
            'category_count': BookCategory.objects.count(),
        })

class BookAdminViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookAdminSerializer
    permission_classes = [IsAdminUserProfile]

class AdminBorrowingListAPIView(generics.ListAPIView):
    serializer_class = BorrowRecordAdminSerializer
    permission_classes = [IsAdminUserProfile]
    def get_queryset(self):
        queryset = BorrowRecord.objects.select_related('user', 'book').all()
        status_param = self.request.query_params.get('status')
        from django.utils.timezone import now
        if status_param == 'returned':
            queryset = queryset.filter(is_returned=True)
        elif status_param == 'unreturned':
            queryset = queryset.filter(is_returned=False)
        elif status_param == 'overdue':
            queryset = queryset.filter(is_returned=False, due_date__lt=now())
        return queryset

class AdminBorrowingActionAPIView(APIView):
    permission_classes = [IsAdminUserProfile]
    def post(self, request):
        action = request.data.get('action')
        borrow_id = request.data.get('borrow_id')
        record = get_object_or_404(BorrowRecord, id=borrow_id)
        if action == 'reminder':
            Notification.objects.create(
                user=record.user,
                message=f"Reminder: Please return '{record.book.title}' by {record.due_date.strftime('%b %d, %Y') if record.due_date else 'ASAP'}."
            )
            return Response({'status': 'reminder sent'})
        elif action == 'fine':
            try:
                fine_amount = float(request.data.get('fine_amount'))
                if fine_amount < 0:
                    return Response({'error': 'Fine cannot be negative.'}, status=400)
                record.fine = fine_amount
                record.save()
                return Response({'status': 'fine updated'})
            except Exception as e:
                return Response({'error': str(e)}, status=400)
        elif action == 'return':
            try:
                record.return_book()
                return Response({'status': 'book returned'})
            except Exception as e:
                return Response({'error': str(e)}, status=400)
        return Response({'error': 'Invalid action'}, status=400)

class BookCategoryAdminViewSet(viewsets.ModelViewSet):
    queryset = BookCategory.objects.all()
    serializer_class = BookCategoryAdminSerializer
    permission_classes = [IsAdminUserProfile]
    
    def destroy(self, request, *args, **kwargs):
        category = self.get_object()
        if Book.objects.filter(category=category).exists():
            return Response({'error': 'Cannot delete category with associated books.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)


class ReviewListAdminAPIView(generics.ListAPIView):
    serializer_class = ReviewAdminSerializer
    permission_classes = [IsAdminUserProfile]
    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'book').order_by('-created_at')
        book_query = self.request.query_params.get('book')
        rating_query = self.request.query_params.get('rating')
        if book_query:
            queryset = queryset.filter(book__title__icontains=book_query)
        if rating_query:
            queryset = queryset.filter(rating=rating_query)
        return queryset


class ReviewDeleteAdminAPIView(APIView):
    permission_classes = [IsAdminUserProfile]
    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        review.delete()
        return Response({'status': 'deleted'})

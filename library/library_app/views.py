from django.db.models import Q
from django.urls import reverse
from django.http import JsonResponse
from .forms import UserSignupForm
from django.contrib import messages
from django.utils.timezone import now
from django.contrib.auth import login, logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, BorrowRecord, BookCategory, Review, UserProfile, Notification


def login_view(request):
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        return redirect('admin_dashboard' if profile.is_admin else 'home')

    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)

        profile = UserProfile.objects.get(user=user)
        if profile.is_admin:
            return redirect('admin_dashboard')  
        return redirect('home')  

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')  

def signup_view(request):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user) 
            return redirect('/login')
    else:
        form = UserSignupForm()
    return render(request, 'signup.html', {'form': form})


def homepage(request):
    featured_books = Book.objects.order_by('?')[:8]  
    categories = BookCategory.objects.all()
    return render(request, 'homepage.html', {
        'featured_books': featured_books,
        'categories': categories,
    })


def list_books(request):
    books = Book.objects.all()
    return render(request, 'booklist.html', {'books': books})

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    already_borrowed = BorrowRecord.objects.filter(user=request.user, book=book, is_returned=False).exists()

    if already_borrowed:
        messages.warning(request, "You have already borrowed this book.")
    elif book.available_copies > 0:
        book.borrow()
        BorrowRecord.objects.create(user=request.user, book=book)
        messages.success(request, f"You've successfully borrowed: {book.title}")
    else:
        messages.error(request, "No copies available to borrow at the moment.")

    return redirect(request.META.get('HTTP_REFERER') or reverse('list_books'))

@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user)
    if not record.is_returned:
        record.return_book()
    return redirect('my_borrowings')


@login_required
def my_borrowings(request):
    records = BorrowRecord.objects.filter(user=request.user).order_by('-borrow_date')
    return render(request, 'my_borrowings.html', {'records': records})

def search_books(request):
    query = request.GET.get('query', '').strip()
    results = []
    if query:
        results = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    return render(request, 'search.html', {'query': query, 'results': results})

def books_by_category(request, category_id):
    category = get_object_or_404(BookCategory, id=category_id)
    books = Book.objects.filter(category=category)
    return render(request, 'books_by_category.html', {
        'books': books,
        'category': category
    })


@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = Review.objects.filter(book=book).order_by('-created_at')

    if request.method == 'POST':
        comment = request.POST.get('comment')
        rating = request.POST.get('rating')

        if comment and rating:
            Review.objects.create(
                user=request.user,
                book=book,
                content=comment,
                rating=int(rating)
            )
            return redirect('book_details', book_id=book_id)

    return render(request, 'book_details.html', {
        'book': book,
        'reviews': reviews,
    })

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.username != 'admin':
            return redirect('home')  
        return view_func(request, *args, **kwargs)
    return login_required(wrapper)

@admin_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


@admin_required
def admin_manage_books(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    
    categories = BookCategory.objects.all()  

    return render(request, 'admin_manage_books.html', {
        'books': books,
        'categories': categories,
        'query': query
    })


def admin_add_book(request):
    if request.method == 'POST':
        title = request.POST['title']
        author = request.POST['author']
        category = get_object_or_404(BookCategory, id=request.POST['category'])
        total = int(request.POST['total_copies'])
        available = int(request.POST['available_copies'])
        image = request.FILES.get('cover_image')

        Book.objects.create(
            title=title,
            author=author,
            category=category,
            total_copies=total,
            available_copies=available,
            cover_image=image
        )
        messages.success(request, "Book added successfully.")
        return redirect('admin_manage_books')

    categories = BookCategory.objects.all()
    return render(request, 'admin_add_book.html', {'categories': categories})


@login_required
def admin_delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if BorrowRecord.objects.filter(book=book, is_returned=False).exists():
        messages.error(request, f'The book "{book.title}" cannot be deleted because it has active borrowings.')
        return redirect('admin_manage_books')
    book.delete()
    messages.success(request, f'"{book.title}" deleted successfully.')
    return redirect('admin_manage_books')


@login_required
def admin_update_book(request, book_id):
    if request.method == 'POST' and request.user.username == 'admin':
        book = get_object_or_404(Book, id=book_id)

        try:
            category_id = request.POST.get('category')
            if not category_id or not category_id.isdigit():
                raise ValueError("Invalid category ID")
            category = get_object_or_404(BookCategory, id=int(category_id))

            total = int(request.POST.get('total_copies'))
            available = int(request.POST.get('available_copies'))
            borrowed_count = BorrowRecord.objects.filter(book=book, is_returned=False).count()

            if available > total:
                raise ValueError("Available copies cannot exceed total copies.")
            elif available < 0:
                raise ValueError("Available copies cannot be negative.")
            elif total < borrowed_count + available:
                raise ValueError("Total copies cannot be less than available + borrowed copies")
            
            book.category = category
            book.total_copies = total
            book.available_copies = available
            book.save()
            messages.success(request, f"Book '{book.title}' updated successfully.")
        except Exception as e:
            messages.error(request, f"Update failed: {e}")
            print(f"Update error: {e}")

    return redirect('admin_manage_books')


@login_required
def admin_manage_borrowings(request):
    if request.user.username != 'admin':
        return redirect('home')

    borrowings = BorrowRecord.objects.select_related('user', 'book').all()

    status = request.GET.get('status')

    if status == 'returned':
        borrowings = borrowings.filter(is_returned=True)
    elif status == 'unreturned':
        borrowings = borrowings.filter(is_returned=False)
    elif status == 'overdue':
        borrowings = borrowings.filter(is_returned=False, due_date__lt=now())

    if request.method == 'POST':
        action = request.POST.get('action')
        borrow_id = request.POST.get('borrow_id')
        record = get_object_or_404(BorrowRecord, id=borrow_id)

        if action == 'reminder':
            Notification.objects.create(
                user=record.user,
                message=f"Reminder: Please return '{record.book.title}' by {record.due_date.strftime('%b %d, %Y') if record.due_date else 'ASAP'}."
            )
            messages.success(request, f"Reminder sent to {record.user.username}")
        # elif action == 'return':
        #     try:
        #         record.return_book()
        #         messages.success(request, f"{record.book.title} marked as returned.")
        #     except Exception as e:
        #         messages.error(request, str(e))
        elif action == 'fine':
            try:
                fine_amount = float(request.POST.get('fine_amount'))
                if fine_amount < 0:
                    raise ValueError("Fine cannot be negative.")
                record.fine = fine_amount
                record.save()
                messages.success(request, f"Fine updated for {record.book.title}")
            except Exception as e:
                messages.error(request, f"Failed to update fine: {e}")

    return render(request, 'admin_manage_borrowings.html', {'borrowings': borrowings, 'now': now()})


@login_required
@csrf_exempt
def mark_all_notifications_read(request):
    if request.method == "POST":
        updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'invalid method'}, status=400)

@login_required
def manage_categories(request):
    categories = BookCategory.objects.all()
    return render(request, 'admin_manage_categories.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            BookCategory.objects.create(name=name)
            messages.success(request, 'Category added successfully.')
    return redirect('admin_manage_categories')

# from django.views.decorators.http import require_POST
# @require_POST
@login_required
def delete_category(request, category_id):
    category = get_object_or_404(BookCategory, id=category_id)
    if Book.objects.filter(category=category).exists():
        messages.error(request, f'Cannot delete category "{category.name}" because it has associated books.')
        return redirect('admin_manage_categories')
    category.delete()
    messages.success(request, f'Category "{category.name}" deleted successfully.')
    return redirect('admin_manage_categories')


@login_required
def update_category(request, category_id):
    category = get_object_or_404(BookCategory, id=category_id)
    if request.method == 'POST':
        new_name = request.POST.get('name')
        if new_name:
            category.name = new_name
            category.save()
            messages.success(request, 'Category updated successfully.')
    return redirect('admin_manage_categories')

@login_required
def manage_reviews(request):
    reviews = Review.objects.select_related('user', 'book').order_by('-created_at')

    book_query = request.GET.get('book')
    rating_query = request.GET.get('rating')

    if book_query:
        reviews = reviews.filter(book__title__icontains=book_query)

    if rating_query:
        reviews = reviews.filter(rating=rating_query)

    context = {
        'reviews': reviews,
        'book_query': book_query or '',
        'rating_query': rating_query or '',
    }
    return render(request, 'manage_reviews.html', context)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    messages.success(request, "Review deleted successfully.")
    return redirect('manage_reviews')

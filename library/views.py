from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ReviewForm, ContactForm
from .models import Book, Category, Author, Borrow, Review

MAX_BORROW_LIMIT = 5


def books_list(request):
    qs = Book.objects.select_related('author', 'category').all()

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(author__name__icontains=q))

    cat = request.GET.get('category', '').strip()
    if cat:
        qs = qs.filter(category_id=cat)

    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        qs = qs.order_by('created_at')
    elif sort == 'rated':
        qs = qs.annotate(avg_stars=Avg('reviews__stars')).order_by('-avg_stars', '-created_at')
    else:
        qs = qs.order_by('-created_at')

    paginator = Paginator(qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    return render(request, 'library/books.html', {
        'page_obj': page_obj,
        'categories': categories,
        'q': q,
        'cat': cat,
        'sort': sort,
    })


def book_detail(request, id):
    book = get_object_or_404(Book.objects.select_related('author', 'category'), id=id)
    reviews = book.reviews.select_related('user', 'user__profile').order_by('-created_at')

    user = request.user
    can_borrow = False
    currently_borrowed_by_user = False
    borrowed_before = False

    if user.is_authenticated and not user.is_staff:
        currently_borrowed_by_user = Borrow.objects.filter(
            user=user, book=book, returned_at__isnull=True
        ).exists()
        borrowed_before = Borrow.objects.filter(
            user=user, book=book, returned_at__isnull=False
        ).exists()
        can_borrow = book.is_available and (not currently_borrowed_by_user)

    return render(request, 'library/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'can_borrow': can_borrow,
        'currently_borrowed_by_user': currently_borrowed_by_user,
        'borrowed_before': borrowed_before,
    })


@login_required
def borrow_book(request, book_id):
    if request.user.is_staff:
        messages.error(request, "The admin does not borrow from the student interface.")
        return redirect('book_detail', id=book_id)

    book = get_object_or_404(Book, id=book_id)

    if not book.is_available:
        messages.error(request, "The book is currently not available.")
        return redirect('book_detail', id=book.id)

    if Borrow.objects.filter(user=request.user, book=book, returned_at__isnull=True).exists():
        messages.warning(request, "You are already a borrower of this book currently.")
        return redirect('book_detail', id=book.id)

    active_count = Borrow.objects.filter(user=request.user, returned_at__isnull=True).count()
    if active_count >= MAX_BORROW_LIMIT:
        messages.error(request, f"You have reached your borrowing limit ({MAX_BORROW_LIMIT}).")
        return redirect('my_books')

    expected = timezone.now() + timedelta(days=14)
    Borrow.objects.create(user=request.user, book=book, expected_return_at=expected)

    book.available_copies -= 1
    book.save()

    messages.success(request, "Borrowing completed successfully.")
    return redirect('my_books')


@login_required
def my_books(request):
    if request.user.is_staff:
        return redirect('home')

    borrows = Borrow.objects.filter(user=request.user).select_related('book').order_by('-borrowed_at')
    active = borrows.filter(returned_at__isnull=True)
    now = timezone.now()

    return render(request, 'library/my_books.html', {
        'active': active,
        'history': borrows.filter(returned_at__isnull=False),
        'now': now
    })


@login_required
def return_book(request, borrow_id):
    borrow = get_object_or_404(Borrow, id=borrow_id, user=request.user, returned_at__isnull=True)
    borrow.returned_at = timezone.now()
    borrow.save()

    book = borrow.book
    book.available_copies += 1
    book.save()

    messages.success(request, "The book has been returned.")
    return redirect('my_books')


@login_required
def add_review(request, id):
    if request.user.is_staff:
        return redirect('home')

    book = get_object_or_404(Book, id=id)

    borrowed_before = Borrow.objects.filter(user=request.user, book=book, returned_at__isnull=False).exists()
    if not borrowed_before:
        messages.error(request, "You cannot evaluate a book that you have not previously borrowed.")
        return redirect('book_detail', id=book.id)

    if Review.objects.filter(user=request.user, book=book).exists():
        messages.warning(request, "You already rated this book.")
        return redirect('book_detail', id=book.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            Review.objects.create(
                user=request.user,
                book=book,
                stars=int(form.cleaned_data['stars']),
                comment=form.cleaned_data.get('comment', '')
            )
            messages.success(request, "Rating added.")
            return redirect('book_detail', id=book.id)
    else:
        form = ReviewForm()

    return render(request, 'library/review_form.html', {'book': book, 'form': form})


def categories_page(request):
    cats = Category.objects.annotate(book_count=Count('books')).order_by('name')
    return render(request, 'library/categories.html', {'categories': cats})


def category_books(request, id):
    category = get_object_or_404(Category, id=id)
    books = Book.objects.filter(category=category).select_related('author', 'category').order_by('-created_at')
    return render(request, 'library/category_books.html', {'category': category, 'books': books})


def authors_page(request):
    authors = Author.objects.annotate(book_count=Count('books')).order_by('name')
    return render(request, 'library/authors.html', {'authors': authors})


def author_detail(request, id):
    author = get_object_or_404(Author, id=id)
    books = Book.objects.filter(author=author).select_related('category').order_by('-created_at')
    return render(request, 'library/author_detail.html', {'author': author, 'books': books})


def contact_page(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, "Your message has been sent. Thank you.")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'library/contact.html', {'form': form})
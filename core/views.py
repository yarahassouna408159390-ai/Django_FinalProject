from django.db.models import Count
from django.shortcuts import render
from django.contrib.auth.models import User
from library.models import Book, Author

def home(request):
    latest_books = Book.objects.select_related('author','category').order_by('-created_at')[:6]

    # top rated: ترتيب بسيط حسب عدد المراجعات كحد أدنى (حل عملي وسريع)
    top_rated = Book.objects.annotate(rc=Count('reviews')).order_by('-rc', '-created_at')[:3]

    stats = {
        'books': Book.objects.count(),
        'authors': Author.objects.count(),
        'students': User.objects.filter(is_staff=False).count(),
    }

    return render(request, 'core/home.html', {
        'latest_books': latest_books,
        'top_rated': top_rated,
        'stats': stats
    })
from django.shortcuts import render

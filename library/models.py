from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    icon = models.CharField(max_length=80, blank=True, null=True)  # مثال: "bi bi-book"

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=150)
    photo = models.ImageField(upload_to='authors/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=220)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='books')

    publication_year = models.PositiveIntegerField()
    pages = models.PositiveIntegerField()
    language = models.CharField(max_length=60)
    description = models.TextField()

    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.available_copies > 0

    def avg_rating(self):
        qs = self.reviews.all()
        if not qs.exists():
            return 0
        return round(sum(r.stars for r in qs) / qs.count(), 1)

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrows')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows')
    borrowed_at = models.DateTimeField(auto_now_add=True)
    expected_return_at = models.DateTimeField()
    returned_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'book', 'returned_at']),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.book.title}"

    @property
    def is_returned(self):
        return self.returned_at is not None

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    stars = models.PositiveSmallIntegerField()  # 1..5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.book.title} - {self.stars}"
from django.db import models

# Create your models here.

from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.books_list, name='books'),
    path('book/<int:id>/', views.book_detail, name='book_detail'),

    path('borrow/<int:book_id>/', views.borrow_book, name='borrow_book'),
    path('my-books/', views.my_books, name='my_books'),
    path('return/<int:borrow_id>/', views.return_book, name='return_book'),

    path('book/<int:id>/review/', views.add_review, name='add_review'),

    path('categories/', views.categories_page, name='categories'),
    path('category/<int:id>/', views.category_books, name='category_books'),

    path('authors/', views.authors_page, name='authors'),
    path('author/<int:id>/', views.author_detail, name='author_detail'),

    path('contact/', views.contact_page, name='contact'),
]

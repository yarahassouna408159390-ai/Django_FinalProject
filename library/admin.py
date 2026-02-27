from django.contrib import admin
from .models import Category, Author, Book, Borrow, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ('name',)
    list_per_page = 25

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ('name',)
    list_per_page = 25

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id','title','author','category','total_copies','available_copies','created_at')
    list_filter = ('category','language')
    search_fields = ('title','author__name')
    list_per_page = 25

@admin.register(Borrow)
class BorrowAdmin(admin.ModelAdmin):
    list_display = ('id','user','book','borrowed_at','expected_return_at','returned_at')
    list_filter = ('returned_at',)
    search_fields = ('user__username','book__title')
    list_per_page = 25

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id','user','book','stars','created_at')
    list_filter = ('stars',)
    search_fields = ('user__username','book__title')
    list_per_page = 25
from django.contrib import admin


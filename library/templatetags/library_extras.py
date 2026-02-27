from django import template

register = template.Library()

@register.filter
def book_status(book):
    # returns tuple-like string key, template will style it
    return "available" if book.is_available else "borrowed"

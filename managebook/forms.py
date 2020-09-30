from django.forms import ModelForm, Textarea, TextInput, SelectMultiple
from managebook.models import Book


class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ("title", "text", "genre")
        widgets = {
            'title': TextInput(attrs={"class": "form-control"}),
            'text': Textarea(attrs={"class": "form-control", "rows": 5}),
            'genre': SelectMultiple(attrs={"class": "form-control"})
        }
        labels = {
            "title": "hello title"
        }
        help_texts = {
            "text": "вводи текст руками"
        }

from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import Count, Q, CharField, Value
from django.db.models.functions import Cast
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from pytils.translit import slugify
from managebook.forms import BookForm, CommentForm, CustomUserCreateForm
from managebook.models import BookLike, Book, CommentLike, Comment
from django.views import View
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from datetime import datetime
from django.utils.decorators import method_decorator


class BookView(View):
    # @method_decorator(cache_page(5))
    def get(self, request):
        if request.user.username in cache:
            result = cache.get(request.user.username)
            response = {"content": result, "form": CommentForm()}
            return render(request, "index.html", response)
        response = {"form": CommentForm()}
        if request.user.is_authenticated:
            quary = Q(book_like__user_id=request.user.id)
            sub_quary = Book.objects.filter(quary). \
                annotate(user_rate=Cast('book_like__rate', CharField())). \
                prefetch_related("author", "genre", "comment", "comment__user")
            result = Book.objects.filter(~quary).annotate(user_rate=Value(-1, CharField())). \
                prefetch_related("author", "genre", "comment", "comment__user"). \
                union(sub_quary)
        else:
            result = Book.objects. \
                prefetch_related("author", "genre", "comment", "comment__user").all()
        response['content'] = result
        cache.set(request.user.username, result, 10)
        return render(request, "index.html", response)


class AddRateBook(View):
    def get(self, request, rate, book_id):
        if request.user.is_authenticated:
            cache.delete(request.user.username)
            BookLike.objects. \
                create(book_id=book_id, rate=rate, user_id=request.user.id)
        return redirect("hello")


class AddLike(View):
    def get(self, request, comment_id):
        if request.user.is_authenticated:
            CommentLike.objects. \
                create(comment_id=comment_id, user_id=request.user.id)
        return redirect("hello")


class RegisterView(View):
    def get(self, request):
        form = CustomUserCreateForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = CustomUserCreateForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("hello")
        messages.error(request, "This Username already exist")
        return redirect("register")


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("hello")
        messages.error(request, message="User does not exist")
        return redirect("login")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("hello")


class AddNewBook(View):
    def get(self, request):
        form = BookForm()
        return render(request, "create_book.html", {"form": form})

    def post(self, request):
        book = BookForm(data=request.POST)
        if book.is_valid():
            nb = book.save(commit=False)
            nb.slug = slugify(nb.title)
            try:
                nb.save()
            except IntegrityError:
                nb.slug += datetime.now().strftime("%Y:%m:%d:%H:%M:%S:%f")
                nb.save()
            nb.author.add(request.user)
            book.save_m2m()
            return redirect("hello")
        return redirect("add_book")


class DeleteBook(View):
    def get(self, request, book_id):
        if request.user.is_authenticated:
            book = Book.objects.get(id=book_id)
            if request.user in book.author.all():
                book.delete()
        return redirect("hello")


class UpdateBook(View):
    def get(self, request, book_slug):
        if request.user.is_authenticated:
            book = Book.objects.get(slug=book_slug)
            if request.user in book.author.all():
                bf = BookForm(instance=book)
                return render(request, "update_book.html", {"form": bf, "slug": book.slug})
        return redirect("hello")

    def post(self, request, book_slug):
        book = Book.objects.get(slug=book_slug)
        bf = BookForm(instance=book, data=request.POST)
        if bf.is_valid():
            bf.save()
        return redirect("hello")


class AddComment(View):
    def post(self, request, book_id):
        if request.user.is_authenticated:
            cf = CommentForm(data=request.POST)
            comment = cf.save(commit=False)
            comment.user = request.user
            comment.book_id = book_id
            comment.save()
        return redirect("hello")

# CRUD      create +,  read +,  update+,  delete+
# CRUD      Comment HW
# Rewrite   AuthenticationForm  to CustomAuthenticationForm
# Oath2     Google

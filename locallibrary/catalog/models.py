from tokenize import Triple

from django.db import models
from django.db.models import SET_NULL
from django.urls import reverse
import uuid
from django.contrib.auth.models import User
from datetime import date


class Genre(models.Model):
    """
    Model representing a book genre (e.g. Science Fiction, Non Fiction).
    """
    name = models.CharField(max_length=200, help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)")

    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author',on_delete=models.SET_NULL, null=True )
    summary = models.CharField(max_length=1000, help_text='Введите краткое описание книги')
    isbn = models.CharField('ISBN',max_length=13, help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Выберите жанр этой книги")

    def __str__(self):
        """
        Строка для представления объекта модели
        """
        return self.title

    def get_absolute_url(self): # я говорю django, что для каждого объекта книги в админке или на веб-странице будет отображаться название книги
        """
        Возвращает URL-адрес для доступа к определенному экземпляру книги
        """
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):

        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

class BookInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Уникальный идентификатор конкретной книги во всей библиотеке')
    book = models.ForeignKey('Book', on_delete=SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False


    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Забронировать наличие')
    class Meta:
        ordering = ["due_back"]

    def __str__(self):
        """
        Строка для представления объекта модели
        """
        return '%s (%s)' % (self.id, self.book.title)

class Author(models.Model):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])


    def __str__(self):
        return '%s, %s' % (self.last_name, self.first_name)
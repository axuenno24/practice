from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre, Language, Publisher
from django.views import generic
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author
from django.views.generic import DetailView



def index(request):
    """Отображение главной страницы"""
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(request, 'index.html',
                  context={'num_books':num_books,
                           'num_instances':num_instances,
                           'num_instances_available':num_instances_available,
                           'num_authors':num_authors,
                            'num_visits':num_visits})

class BookListView(generic.ListView):
    model = Book

class BookDetailView(generic.DetailView):
    model = Book
    def book_detail_view(request, pk):
        try:
            book_id = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            raise Http404("Book does not exist")

        return render(
            request,
            'catalog/book_detail.html',
            context={'book': book_id, })

class BookListView(generic.ListView):
    model = Book
    paginate_by = 10

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """
    Общий список книг на основе классов, предоставленных текущему пользователю
    """
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    Функция просмотра для обновления определенного BookInstance библиотекарем
    """
    book_inst = get_object_or_404(BookInstance, pk=pk)

    # Если это запрос POST, обработайте данные формы
    if request.method == 'POST':

        # Создайте экземпляр формы и заполните его данными из запроса (привязка):
        form = RenewBookForm(request.POST)

        # Проверяем, действительна ли форма:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()

            # перенаправление на новый URL:
            return HttpResponseRedirect(reverse('all-borrowed') )


    # Если это GET (или любой другой метод), создайте форму по умолчанию.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date,})

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'bookinst':book_inst})

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial={'date_of_death':'12/10/2016',}

    def get_success_url(self):
        # После успешного создания переходим на страницу детального просмотра автора
        return reverse_lazy('author-detail', kwargs={'pk': self.object.pk})

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')

class AuthorDetailView(DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'

class AuthorListView(generic.ListView):
    model = Author
    template_name = 'catalog/author_list.html'  # Убедитесь, что шаблон существует
    context_object_name = 'author_list'

from django.shortcuts import render, get_object_or_404
from .models import Book, Author, BookInstance, Genre
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# 通过函数的权限装饰器，因为我们不需要用通用列表视图
from django.contrib.auth.decorators import permission_required
import datetime
from django.core.mail import send_mail
# 处理表单需要的
from .forms import NameForm, ContractForm, RenewBookForm
from django.http import HttpResponseRedirect
from django.urls import reverse

# 用于创建作者更新作业编辑作者的通用编辑视图
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy


# Create your views here.


def index(request):
    """ 主页网站的视图函数 """
    # 生成一些主要对象的计数
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available book (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()  # all() 默认是 隐式调用的
    num_genres = Genre.objects.all().count()
    title = 'fuk the world'  # 这个是改 网页标题的，只是做尝试
    # print(num_genres)
    s = ''
    for genre in Genre.objects.all():
        if genre.name == Genre.objects.all()[len(Genre.objects.all())-1].name:
            genre.name += '。'
        else:
            genre.name += ', '
        s += genre.name

    # 告诉用户，他们访问主页的次数，需要的知识是 session,
    # 访问此视图的次数，如在会话变量中计算的那样
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    return render(
        request,
        # django 默认会在这儿找 /locallibrary/catalog/templates/index.html
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available,
                 'num_authors': num_authors, 'title': title,
                 'num_genres': num_genres, 's': s,
                 'num_visits': num_visits, }
    )


class BookListView(generic.ListView):
    """
    基于类的列表通用视图，实现了很多功能，并且代码更少，维护更少
    并且默认可以使用 object_list,或者 book_list 的模板变量来访问书本列表
    """
    model = Book
    # 就是这么简单，默认会寻找这个 catalog/book_list.html
    # 所以我们要创建一个 book_list.html
    # 每页显示 2本书，因为数据库中只有6本吧，好像是
    paginate_by = 2
    # 现在数据已经分页，我们需要添加对模板的支持，以滚动结果集合。
    # 因为我们可能希望在所有列表视图中，都执行此操作，所以我们将以可添加到基本模板的
    # 方式，执行此操作。
    # ListView 分页后会给模板传递一个 is_paginated 和一个 page_obj 变量 以及 paginator 变量
    # is_paginated 是一个布尔值变量，page_obj是一个Page对象的一个实例，paginator是Paginator对象的实例


class BookDetailView(generic.DetailView):
    model = Book
    """
    这个会默认寻找 catalog/book_detail.html
    并且默认的你可以使用 object 或者 book 的模板变量以访问书本列表
    """


class AuthorListView(generic.ListView):
    model = Author
    # 请注意这个的分页值，如果你在test_views.py 中测试，那么填写 10， 否则请改为 2，
    # 因为目前作者只有少数几个，分页设置为10 显然太多了，无法更好的在前端显示效果。
    paginate_by = 10


class AuthorDetailView(generic.DetailView):
    model = Book
    template_name = 'catalog/author_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_books = Book.objects.all()
        context['all_books'] = all_books
        return context


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """
    基于类的通用视图，列出借给当前用户的图书，并且和以前不同的是，只有登录后的用户才有资格调用次视图
    """
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        #
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')


class BorrowedBooksByStaffListView(PermissionRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_staff.html'
    paginate_by = 10
    permission_required = 'catalog.can_mark_returned'

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

'''
只是为了测试，练习，这是官网中 form 的内容
def get_name(request):
    if request.method == "POST":
        # 检查如果请求是 POST 那么用 request.POST 作为参数填充到该name表单
        form = NameForm(request.POST)
        if form.is_valid():
            # 然后我们判断表单的内容是否是有效的
            # cleaned_data 是验证后清理后的数据字典， 字段名的值都作为键存在里面了
            name = form.cleaned_data['your_name']
            print(name)
            # 这里上面在终端输出name的值，然后返回到 index 的 url.
            return HttpResponseRedirect(reverse('index'))
    else:
        form = NameForm()
    return render(request, 'catalog/name.html', {'form': form})

def send_mail(request):

    if request.method == 'POST':

        form = ContractForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']
            password = form.cleaned_data['password']
            recipients = ['info@example.com']
            if cc_myself:
                recipients.append(sender)
            print(subject, message, password, sender, recipients, cc_myself)
            #send_mail(request, subject, message, sender, recipients)

        return HttpResponseRedirect(reverse('index'))
    else:
        form = ContractForm()
    return render(request, 'catalog/send_mail.html', {'form': form})
'''


@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """
    原本你需要再去定义一个 can_renew 权限，就是重新写一个，不过，为了简单，直接用can_mark_returned
    """
    book_instance = get_object_or_404(BookInstance, pk=pk)
    print('book_instance id:', book_instance.id)
    # 检查传入的方法
    if request.method == 'POST':
        # 把传进来的数据填充给创建的form实例
        form = RenewBookForm(request.POST)

        # 检查数据是否有效
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # 这一步非常重要，把你带到某个页面，否则，用户点击提交后，一直没有动静
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        # 如果是 get 或者其他方法，则创建默认表单
        proposed_renew_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renew_date, })

    return render(request, 'catalog/book_renew_librarian.html', {'form': form, 'book_instance': book_instance, })


class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    # initial 只是为了测试，你在页面中会看到的已经填写好的默认值
    initial = {'date_of_death': '06/01/2018', }
    # 也就是添加作者成功后，应该跳转到哪里
    success_url = reverse_lazy('authors')


class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']


class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    #  reverse_lazy()是一个延迟执行的reverse()版本，在这里使用，是因为我们提供了一个基于类的 URL 查看属性
    # “创建” 和 “更新” 视图默认使用相同的模板，它将以您的模型命名：model_name_form.html（您可以
    # 使用视图中的template_name_suffix 字段，将后缀更改为_form 以外的其他内容，
    # 例如，template_name_suffix = '_other_suffix'）
    # “删除”视图需要查找以 model_name_confirm_delete.html 格式命名的模板
    # （同样，您可以在视图中，使用template_name_suffix 更改后缀）


class BookCreate(CreateView):
    model = Book
    fields = '__all__'
    success_url = reverse_lazy('books')


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'
    template_name_suffix = '_update_form'
    success_url = reverse_lazy('books')


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')

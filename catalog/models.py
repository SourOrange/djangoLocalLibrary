from django.db import models
from django.urls import reverse
# 通过反转URL模式来生成URL

from django.contrib.auth.models import User
from datetime import date

import uuid
# Create your models here.


class Genre(models.Model):
    """
    该模型代表一本书籍的类别(eg. 小说或非小说，军事历史人文地理等等)
    name 字段用于描述类型
    """
    name = models.CharField(max_length=200, help_text="Enter a book genre(e.g. Science "
                                                      "Fiction, French Poetry etc.)")

    def __str__(self):
        """
        返回该模型对象的名字，不然会显示为 object
        """
        return self.name


class Book(models.Model):
    """
    该模型代表一本普遍的书，但并不是一个特定的物理“实例”或可用于借阅的“复制“
    """
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    # 通常书只有一个作者，但作者可以写很多书，(也可能有几个作者，但是不再这个项目中实现)
    # 关联的类在引用之前还没在文件中定义，则必须使用该模型的名称作为字符串
    # Author 作为字符串而不是 Object对象，是因为在该文件中还没定义
    # null=True 如果没有作者被选择，这允许数据库存储一个 Null 值
    # 如果相关的作者记录被删除，SET_NULL 将作者的值设置为 Null
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, help_text='13 Character <a target="_blank" href="'
                                                             'https://www.isbn-international.org/content/what-isbn">'
                                                             'ISBN number</a>')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    # 一本书可以有很多类型，一个类型也可以包含很多本书

    def __str__(self):
        """
        返回该模型对象的名字，不然会显示为 object
        使用书的文本字段来表示Book记录
        """
        return self.title

    def get_absolute_url(self):
        """
        返回访问 特定图书实例 的 url
        也就是返回一个可用于访问这些模型的详细记录的URL

        在后台管理站点中点击  在站点上查看 按钮
        返回这个链接 http://127.0.0.1:8000/admin/r/10/1/ （1 是id）
        并且因为我们还没有定义 book-detail 所以会报错如下信息
        NoReverseMatch at /admin/r/10/1/
        Reverse for 'book-detail' not found. 'book-detail' is not a valid
        view function or pattern name.
        通常来说，定义这个方法是为了在模板中使用 url模板标记

        """
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        """
        为 Genre 创建字符串，这是在 Admin 中显示类型所必须的
        """
        # 以下的 self.genre 相当于
        # for objInstance in Book.objects.all():
        #     for genre in objInstance.genre.all():
        #         genre.name 实际上它返回了前三个，如果你有3个或以上的类别的话
        #                    如果没有则返回1个或者2个
        return ', '.join([genre.name for genre in self.genre.all()[:3]])
    # 如果你不给一个简洁的字段名称，后台管理将显示为 DISPLAY GENRE
    display_genre.short_description = 'Genre'


class BookInstance(models.Model):
    """
    该模型代表一本书，有人可能借用的一个特定副本，包括有关副本是否可用在上面日期归还，
    “印记”或版本的详细信息，并为这本书在图书馆给与一个唯一的ID信息。
    该模型使用
    ForeignKey 识别相关联的书(每本书可以有多个副本，但副本只能有一个Book)
    CharField 表示这本书的印记 (具体 版本)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across whole library")
    # UUIDField 用于设置该 id 字段作为其模型的 primary_key
    # 这类型字段为每个实例分配一个全局唯一的值（一个用于在库中可以找到的每本书）
    book = models.ForeignKey('Book', on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    # DateField 用于due_back日期（书籍预期在借用或维护后可用）
    # 该值可以是（blank或者null当该书可用时需要）

    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reversed'),
    )
    # 在 shell 中调试的时候，b = BookInstance(....), b.status 会返回其中一个字母
    # 而 b.get_status_display() 则 返回对应的值(可读性提高了)

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True,
                              default='m', help_text='Book availability')
    # status 是 CharField 定义选择／选择列表。你可以看到我们定义一个包含键值对元组的元组，
    # 并将其传递给choices 参数，而键是当选择该选项时实际保存的值。我们还设置了一个默认的
    # 值 “m” （维护），因为书籍最初将在库存之前创建不可用。

    class Meta:
        # 元数据（Class Meta）使用此字段在查询中返回时记录。
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """
        使用id 和 book.title 返回该对象
        表示  BookInstance 对象 使用唯一ID和关联的标题的组合
        """
        return f'{self.id} ({self.book.title})'

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False


class Author(models.Model):
    """
    该模型代表了作者的一些信息
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    def get_absolute_url(self):
        """
        返回访问特定作者实例的URL
        """
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name} {self.first_name}'

    def full_name(self):
        return f'{self.last_name + self.first_name}'

    class Meta:
        ordering = ['last_name']





















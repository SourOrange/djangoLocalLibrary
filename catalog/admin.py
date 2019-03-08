from django.contrib import admin
from .models import Author, Genre, Book, BookInstance

# Register your models here.
# 因为我们可以更好的在后台显示我们想要的结果
# 所以 我们需要引入更加强大的功能

# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(Book)
# admin.site.register(BookInstance)

class BooksInline(admin.TabularInline):
    model = Book
# 第一步，定义admin Class
class AuthorAdmin(admin.ModelAdmin):
    # 我们设置了 Author 模型返回的是作者的名，我们可以添加其他字段
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death', 'full_name')
    # list_display 是元组，而 fields 是列表
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    # search_fields = ['full_name'] 这一步暂时不搞，还没搞懂，只能接受字段名，而非函数

    # 在作者详细视图中添加一个Book内联列表，就像在Book中添加BookInstance那样
    inlines = [BooksInline]
# 第二步，使用关联的模型注册 admin 类
admin.site.register(Author, AuthorAdmin)


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    # 在添加书的那个页面中，会有三个占位符，也就是三个等待填写的相关字段
    # 并且在 book 管理后台中点击title字段后，页面底部会出现对应的BookInstance状态
    # 你可以通过 extra 0 设置一个占位都不要
    # 默认的是 三个占位符 也就是说不设置的话，默认的是 extra = 3
    # extra = 0，如果你不想要就设置为 0

# 除了第一和第二步的方法之外，还可以用装饰器一步到位
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # 当我们把 字段名 genre 写进去时，你会发现终端报错
    # Errors:
    # <class 'catalog.admin.BookAdmin'>: (admin.E109) The value of
    #  'list_display[2]' must not be a ManyToManyField.
    # 也就是说 ManyToManyField 的关系不能这么加进去，我们需要创建一个函数
    list_display = ('title', 'author', 'display_genre')
    inlines = [BooksInstanceInline]

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_filter = ('status', 'due_back')
    fieldsets = [
        # None 的意思是你不需要一个标题
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    ]
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')


# 默认情况下，Django 显示每个对象的 str() 返回的值。
# 但有时如果我们能够显示单个字段，它会更有帮助
# 使用 list_display 后台选项，它是一个包含要显示的字段名的元组
# 在更改列表页中以列的形式展示这个对象


# fields 可以控制哪些字段被显示和布局
# 在fields 属性列表只是要显示在表格上那些领域，如此才能。
# 字段默认情况下垂直显示，但如果您进一步将它们分组在元组中
# （如上述“日期”字段中所示），则会水平显示。

# fieldsets 属性添加“部分”以在详细信息表单中对相关的模型信息进行分组
# 添加内联列表的目的在于 更高效的填写有关联的模型的内容

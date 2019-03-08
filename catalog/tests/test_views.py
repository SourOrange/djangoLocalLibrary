from django.test import TestCase

# Create your tests here.
from ..models import Author
from django.urls import reverse

import datetime
from django.utils import timezone
from ..models import BookInstance, Book, Genre
from django.contrib.auth.models import User

# 测试，需要获得许可的权限
from django.contrib.auth.models import Permission


class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # 为了分页测试，创建13个作者，前提是 views 中的那个分页你设置的值是 10
        number_of_authors = 13
        all_authors = []
        for author_number in range(number_of_authors):
            author = Author.objects.create(first_name=f"Jim {author_number}", last_name=f"Green {author_number}")
            all_authors.append(author)
        print(len(all_authors))

    def test_view_url_exists_at_desired_location(self):
        # print(Author.objects.get(id=1))
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 10)
        # print("Author list is :")
        # print(len(response.context['author_list']))
        # print(response.context['author_list'])

    def test_lists_all_authors(self):
        # 获取第二页并且确认它还有 3个 作者
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertTrue(len(response.context['author_list']) == 3)


class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        # 创建两个用户，
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        # 创建 一本书
        test_author = Author.objects.create(first_name="Jim", last_name="Green")
        test_genre = Genre.objects.create(name="Fantasy")
        # test_language = Language.objects.create(name="English") 如果你做了 Language 的挑战，就加入
        # 加入到 test_book ，即一下括号内最后一项
        test_book = Book.objects.create(
            title="Book Title", summary="My book summary", isbn="ABCDEFG", author=test_author,)
        # 创建类型作为一个后步骤
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # 不允许直接分配多对多类型
        test_book.save()

        # 创建30个书的副本，BookInstance
        number_of_copies = 30
        for book_copy in range(number_of_copies):
            return_date = timezone.now() + timezone.timedelta(days=book_copy % 5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,imprint='Unlikely Imprint, 2019',due_back=return_date,borrower=the_borrower,status=status)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('my-borrowed'))

        # 验证我们的用户是登录
        self.assertEqual(str(response.context['user']), 'testuser1')
        # 验证我们得到的是200
        self.assertEqual(response.status_code, 200)

        # 检车我们用的是正确的模板
        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('my-borrowed'))

        # 验证我们的用户是否登录
        self.assertEqual(str(response.context['user']), 'testuser1')
        # 验证我们得到的是 200
        self.assertEqual(response.status_code, 200)

        # 检查一开始我们的书单上没有书 (没有借出的)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # 现在修改所有书有可以借出的状态
        get_ten_books = BookInstance.objects.all()[:10]
        for copy in get_ten_books:
            copy.status = 'o'
            copy.save()

        # 现在我们检查书单里有已经借出的书
        response = self.client.get(reverse('my-borrowed'))
        # 检查我们的用户已经登录
        self.assertEqual(str(response.context['user']), 'testuser1')
        # 检查我们得到的是200
        self.assertEqual(response.status_code, 200)
        # 判断
        self.assertTrue('bookinstance_list' in response.context)
        # 确认所有书都是user1 的并且都是显示 借出
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_back(self):
        # 检查所有的书都是已经借出的
        for copy in BookInstance.objects.all():
            copy.status = 'o'
            copy.save()

        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('my-borrowed'))

        # 检查我们的用户已经登录
        self.assertEqual(str(response.context['user']), 'testuser1')
        # 检查我们得到的是200
        self.assertEqual(response.status_code, 200)

        # 确认其中只有10个是 分页显示的
        self.assertEqual(len(response.context['bookinstance_list']), 10)

        last_date = 0
        for copy in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = copy.due_back
            else:
                self.assertTrue(last_date <= copy.due_back)


# 使用表单测试视图
class RenewBookInstanceViewTest(TestCase):

    def setUp(self):
        # 创建一个用户
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()

        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()

        # 授予权限
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        # 创建一本书
        test_author = Author.objects.create(first_name='John', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        # test_language = Language.objects.create(name='English') 因为我没接受 Language 的挑战
        test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABCDEFG',
                                        author=test_author, )
        # 创建类型作为后一个步骤
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)  # 无法直接指定多对多类型
        test_book.save()

        # 为 test_user1 创建 BookInstance 对象
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2019',
                                                              due_back=return_date, borrower=test_user1, status='o')

        # 为 test_user2 创建 BookInstance 对象
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Unlikely Imprint, 2019',
                                                              due_back=return_date, borrower=test_user2, status='o')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        # 手动检查重定向(不能使用assertRedirect，因为重定向URL不可预测)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance2.pk, }))

        # Check that it lets us login - this is our book and we have the right permissions.
        # 检查它是否允许我们登录-这是我们的书，我们有正确的权限。
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))

        # Check that it lets us login. We're a librarian, so we can view any users book
        # 检查它是否允许我们登录，我们是图书管理员，所以我们可以查看任何用户的书
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4()  # unlikely UID to match our bookinstance!
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid, }))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(response.status_code, 200)

        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    # 检查表单的初始日期，是将来三周
    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }))
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        # 注意以下是如何访问表单字段的初始值的
        self.assertEqual(response.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        """
        检查如果续借成功，视图会重定向到所有借书的列表。这里的不同之处在于，我们首次展示了，
        如何使用客户端发布（POST）数据。 post数据是post函数的第二个参数，并被指定为键/值的字典。

        """
        login = self.client.login(username='testuser2', password='12345')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        """
        再次测试POST请求，但在这种情况下具有无效的续借日期。
        我们使用assertFormError() ，来验证错误消息是否符合预期。
        """
        login = self.client.login(username='testuser2', password='12345')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='12345')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_bookinstance1.pk, }),
                                {'renewal_date': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks ahead')

    """
    全部借用的视图作为额外挑战，您的代码可能会改为重定向到主页'/'。如果是这样，
    请将测试代码的最后两行，修改为与下面的代码类似。请求中的follow=True，确保请求返回最终
    目标URL（因此检查/catalog/而不是/）。
    
    resp = self.client.post(reverse('renew-book-librarian', 
    kwargs={'pk':self.test_bookinstance1.pk,}), 
    {'renewal_date':valid_date_in_future},follow=True )
    
    self.assertRedirects(resp, '/catalog/')
    """
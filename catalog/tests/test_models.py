from django.test import TestCase
from ..models import Author
import datetime
# Create your tests here.
# 注意：测试类别还有一个我们还没有使用的tearDown()方法。
# 此方法对数据库测试不是特别有用，因为TestCase基类会为您处理数据库拆卸
"""
class YourTestClass(TestCase):

    @classmethod
    def setUpTestData(cls):
        print("setUpTestData: Run once to set up non-modified data for all class methods.")
        pass

    def setUp(self):
        print("setUp: Run once for every test method to setup clean data.")
        pass

    def test_false_is_false(self):
        print("Method: test_false_is_false.")
        self.assertFalse(False)

    def test_false_is_true(self):
        print("Method: test_false_is_true.")
        self.assertTrue(False)

    def test_one_plus_one_equals_two(self):
        print("Method: test_one_plus_one_equals_two.")
        self.assertEqual(1 + 1, 2)

    # 加上python 官网中的最简单的例子
    def test_upper(self):
        print("Method: test_upper.")
        self.assertEqual('foo'.upper(), 'FOO')

    def test_is_upper(self):
        print("Method: test_is_upper.")
        self.assertTrue('FOO'.isupper())
        self.assertFalse('foo'.isupper())

    def test_split(self):
        print("Method: test_split.")
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # 检查当分隔符不是字符串时 分割失败
        with self.assertRaises(TypeError):
            s.split(2)
"""
class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # 创建一个我们将使用，但不在任何测试中修改的作者对象。
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_first_name_label(self):
        author = Author.objects.get(id=1)
        # print(author, type(author)) 测试了一次，会输出 Bob Big, <class 'catalog.models.Author'>
        field_label = author._meta.get_field('first_name').verbose_name
        self.assertEqual(field_label, 'first name')

    def test_last_name_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('last_name').verbose_name
        self.assertEqual(field_label, 'last name')

    def test_date_of_death_label(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_death').verbose_name
        # 这里第一次我们用 self.assertEqual(field_label, 'died') 是为了确定会 出错
        # 并且我们在 models 中也定义了 该字段的 verbose_name = 'Died', 所以只能是 "Died"
        self.assertEqual(field_label, 'Died')

    def test_date_of_birth(self):
        author = Author.objects.get(id=1)
        field_label = author._meta.get_field('date_of_birth').verbose_name
        self.assertEqual(field_label, 'date of birth')

    def test_first_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('first_name').max_length
        self.assertEqual(max_length, 100)

    def test_last_name_max_length(self):
        author = Author.objects.get(id=1)
        max_length = author._meta.get_field('last_name').max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        author = Author.objects.get(id=1)
        expected_object_name = f'{author.last_name} {author.first_name}'
        self.assertEqual(expected_object_name, str(author))

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        # This will also fail if the urlconf is not defined.
        self.assertEqual(author.get_absolute_url(), '/catalog/author/1')




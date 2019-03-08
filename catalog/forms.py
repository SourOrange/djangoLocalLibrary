from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime

from django.forms import ModelForm
from .models import BookInstance


# NameForm 只是作为测试，你可以删除它或者不理会她
class NameForm(forms.Form):
    '''
    forms.Form 是一个原生的表单，也就是你需要自己定义所有的东西
    '''
    your_name = forms.CharField(label="Your Name", max_length=100)


# ContractForm 也只是为了之前的测试，做的练习，不用理会
class ContractForm(forms.Form):
    '''
    这个的字段名，我们没有指定 label ,所以默认在 html 中是 大写的字段名为 label
    '''
    subject = forms.CharField(label="主题", max_length=100, initial="You'll die too.")
    password = forms.CharField(widget=forms.PasswordInput)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks(default 3).")

    # 验证单个字段最简单的方法，就是覆盖重新写 clean_field_name 方法
    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # 检查日期是不是以前的
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # 检查是不是图书馆员允许的四个星期
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        # 最后记住要始终返回清理验证后的数据
        return data


# 除了用上面我们自定义的原生的forms.Form 之外，我们还可以用 ModelForm, 这个挺方便的，看看吧
class RenewBookModelForm(ModelForm):
    # 该模型与 RenewBookForm 做了相同的东西，个人觉得这个比较好，除非你要写原生的form
    # 验证，也和普通表单相同的写法 clean_field_name()
    def clean_due_back(self):
        data = self.cleaned_data['due_back']
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead.'))

        return data

    class Meta:
        # 还可以设置其他默认的，详细去官网看看
        model = BookInstance
        # 如果你要所有的字段就是 fields = '__all__', 如果要排除某个就是 exclude = ['field_name', ...]
        fields = ['due_back', ]
        labels = {'due_back': _('Renewal Date'), }
        help_texts = {'due_back': _('Enter a date between now and 4 weeks(default 3).'), }


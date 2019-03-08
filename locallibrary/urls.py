"""locallibrary URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static


app_name = 'catalog'  # 加了这个变量是因为一开始的 templates/catalog/index.html
                      # 或者其他页面的 url，指定一个命名空间 'url 'catalog:index' '
                      # 但是这混蛋居然显示 模板错误信息，找不到其中的 html

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')),

    # 重定向的作用是 runserver 的时候 直接定向到 http://127.0.0.1:8000/catalog/
    # 也就是说 默认的 127.0.0.1:8000 被我们取代了
    path('', RedirectView.as_view(url='/catalog/')),

    # 以下的 网址会直接报错说找不到页面，并且给你一些有用的信息，
    # 你可以访问 accounts/login 然后看到 registration/login.html 的信息，所以需要你创建这个目录和html文件
    # 做这个是为了模拟 身份登陆的模板，有些更漂亮的外观需要我们自定义，
    # 也别忘记了 你还需要去 settings.py 中 的 templates 做些修改 DIRS
    path('accounts/', include('django.contrib.auth.urls')),
]

# 暂且不加，看看往后会发生什么，

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 超级用户密码
# infos = {'code':'starrybye',
# 'user':timesgone','email':
# 'timesgone@email.com'}

# 后期中在 admin管理后台中，授权 user 添加的用户，名: orangesky code: nihao438
# 名字：橙子 姓氏：黄 email: omg@good.com
# 另一个uesr名：nimeide code: tiantian123
# 名字：霓妹 姓氏：艾 email nimei@ai.com


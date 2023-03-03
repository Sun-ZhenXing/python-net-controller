# Django 云控制器

## 设计目标

使用 Django 实现一套 RESTful 风格的 API，能够支持 Port 的 CURD，并能够分配可用 IP 给 Port。同时尽可能多地实现其他网络相关结构。

设计文档：<https://blog.alexsun.top/vuepress-python-notes/awesome/cloud-controller/>

## 开始使用

安装依赖：

```bash
pip install -r requirements.txt
```

执行数据迁移：

```bash
python manage.py makemigrations netcontroller
```

开始运行：

```bash
python manage.py runserver
```

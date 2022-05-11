from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from taggit.models import Tag
from django.db.models import Count

from .forms import *
from .models import *


def post_list(request, tag_slug=None):
    """ Обработка вывода списка статей с помощью функции обработчика """

    form = GlobalSearchForm()   # Форма для поискового запроса

    # Если был запрос в поисковом поле
    if 'global_query' in request.GET:
        form = GlobalSearchForm(request.GET)
        if form.is_valid():
            global_query = form.cleaned_data['global_query']
            results = Post.objects.annotate(search=SearchVector('title', 'body')).filter(search=global_query)

            return render(request, 'blog/post/search.html', {'form': form,
                                                             'query': global_query,
                                                             'results': results})

    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 3)

    page = request.GET.get('page')  # Извлекаем требуемую страницу

    try:
        posts = paginator.page(page)    # Список объектов на нужной странице
    except PageNotAnInteger:
        posts = paginator.page(1)   # Первая страница
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)     # Последняя страница

    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag, 'global_form': form})


# class PostListView(ListView):
#     """ Обработка вывода списка статей с помощью класса-представления """
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                             publish__month=month, publish__day=day)
    # Список активных комментариев для этой статьи
    comments = post.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        # Пользователь отправил комментарий
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаём комментарий, но пока не сохраняем в базе данных
            new_comment = comment_form.save(commit=False)
            # Привязываем комментарий к текущей статье
            new_comment.post = post
            # Сохраняем комментарий в базе данных
            new_comment.save()
    else:
        comment_form = CommentForm()

    # Формирование списка похожих статей
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts})


def post_share(request, post_id):
    """ Обработка формы отправки email. Получение статьи по идентификатору"""
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Форма было отправлена на сохранение
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Все поля формы прошли валидацию
            cd = form.cleaned_data

            # Отправка электронной почты
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{} ({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {} \n\n{}\'s comments: {}'.format(post.title, post_url, cd['name'], cd['comments'])
            send_mail(subject, message, 'konstnikon88@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # results = Post.objects.annotate(search=SearchVector('title', 'body')).filter(search=query)
            search_vector = SearchVector('title', 'body')
            search_query = SearchQuery(query)
            results = Post.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)
                                            ).filter(search=search_query).order_by('-rank')

    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results})


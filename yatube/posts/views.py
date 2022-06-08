from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .paginator import paginator


def index(request):
    """Главная страница"""
    template = 'posts/index.html'
    post_list = Post.objects.all()
    context = {
        'title': 'Последние обновления на сайте',
        'page_obj': paginator(post_list, request),
    }
    return render(request, template, context)


def group_posts(request, slug):
    """Страница группы постов"""
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = (
        Post
        .objects
        .filter(group=group)
    )
    context = {
        'group': group,
        'page_obj': paginator(post_list, request)
    }
    return render(request, template, context)


def profile(request, username):
    """Профаил пользователя"""
    template = 'posts/profile.html'
    author = User.objects.get(username=username)
    post_list = Post.objects.select_related('author').filter(author_id=author)
    context = {
        'page_obj': paginator(post_list, request),
        'author': author
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница подробной информации о посте"""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post
    }
    return render(request, template, context)


@login_required
def post_create(request):
    """Страница создания поста"""
    form = PostForm(request.POST or None)
    template = 'posts/create_post.html'
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("posts:profile", post.author)
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    """Страница редактирования поста"""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("posts:post_detail", post_id)
        return render(request, template, {'form': form})
    context = {
        'form': form,
        'is_edit': True,
        'post': post
    }
    return render(request, template, context)

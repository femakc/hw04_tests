from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Follow
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm
from .paginator import paginator
from django.views.decorators.cache import cache_page


@cache_page(20, key_prefix='index_page')
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
    following = False
    author = User.objects.get(username=username)
    follow_list = []
    if request.user.is_authenticated:
        followings = list(
            Follow.objects.select_related(
                'user'
            ).
            filter(
                user_id=request.user
            )
        )
        for i in followings:
            follow_list.append(i.author_id)
        following = author.id in follow_list
    user_not_author = request.user != author
    post_list = Post.objects.select_related('author').filter(author_id=author)

    context = {
        'page_obj': paginator(post_list, request),
        'author': author,
        'following': following,
        'user_not_author': user_not_author
    }
    return render(request, template, context)


def post_detail(request, post_id):
    """Страница подробной информации о посте"""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': comments
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
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
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
        'post': post,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Страница подписки"""
    current_user = request.user
    template = 'posts/follow.html'
    follow_list = []
    followings = list(
        Follow.objects.select_related(
            'user'
        ).
        filter(
            user_id=current_user
        )
    )
    for i in followings:
        follow_list.append(i.author_id)
    post_list = Post.objects.select_related('author').filter(
        author__in=follow_list
    )
    context = {
        'title': 'Страница подписки',
        'page_obj': paginator(post_list, request),
        'follow_list': follow_list
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""
    user = User.objects.get(username=request.user)
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.create(user=user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Одписаться на автора"""
    user = User.objects.get(username=request.user)
    author = User.objects.get(username=username)
    if user != author:
        Follow.objects.filter(user=user, author=author).delete()
    return redirect('posts:follow_index')

from django.conf import settings as s
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, User, Comment, Follow


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, s.NUMBER_MESSAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, s.NUMBER_MESSAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    count = post_list.count()
    paginator = Paginator(post_list, s.NUMBER_MESSAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/profile.html'
    following = Follow.objects.filter(
        user=request.user.pk, author=author)
    context = {
        'author': author,
        'count': count,
        'following': following,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/post_detail.html'
    count = post.author.posts.count()
    title = post.text[:30]
    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related('post')
    context = {
        'post': post,
        'count': count,
        'title': title,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect(
            'posts:profile', post.author
        )

    context = {
        'form': form
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect(
            'posts:post_detail',
            post_id
        )

    context = {
        'post': post,
        'form': form,
        'is_edit': True,
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
    """Cтраница с подписками"""
    template = 'posts/follow.html'
    page_number = request.GET.get('page')
    posts = Post.objects.select_related('author', 'group').filter(
        author__following__user=request.user)
    context = {
        'page_obj': Paginator(posts, s.NUMBER_MESSAGES).get_page(page_number),
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    """Подписка на автора"""
    author = get_object_or_404(User, username=username)
    follower = request.user
    follower_list = Follow.objects.filter(author=author, user=follower)
    if follower_list.exists() or follower == author:
        return redirect('posts:index')
    Follow.objects.create(
        author=author,
        user=follower
    )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора"""
    author = get_object_or_404(User, username=username)
    follower = request.user
    follower_list = Follow.objects.filter(author=author, user=follower)
    if not follower_list.exists():
        return redirect('posts:index')
    follower_list.delete()
    return redirect('posts:profile', username)

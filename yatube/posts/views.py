from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

NUMBER_OF_POSTS = 10


@cache_page(20)
def index(request):
    template = 'posts/index.html'
    posts = (
        Post.objects.all()
    )
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    author = get_object_or_404(User, username=username)
    posts = user.posts.all()
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if (request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author).exists()):
        following = True
    context = {
        'author': author,
        'user': user,
        'posts': posts,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post_count = Post.objects.filter(author=post.author).count()
    comments = Comment.objects.filter(post=post)
    form_comments = CommentForm(request.POST or None)
    context = {
        'post': post,
        'post_count': post_count,
        'comments': comments,
        'form_comments': form_comments,

    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        new_form = form.save(commit=False)
        new_form.author = request.user
        new_form.save()
        return redirect(f'/profile/{request.user}/')
    form = PostForm()
    context = {
        'is_edit': False,
        'form': form,
    }

    return render(request, 'posts/create.html', context)


@login_required
def post_edit(request, pk):
    is_edit = True,
    post = get_object_or_404(Post, pk=pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
        )
    if post.author != request.user:
        return redirect(f'/posts/{pk}/')

    if form.is_valid():
        form.save()
        return redirect(f'/posts/{pk}/')

    context = {
        'pk': pk,
        'is_edit': is_edit,
        'form': form,

    }

    return render(request, 'posts/create.html', context)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', pk=pk)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    posts = Post.objects.filter(author__following__user=request.user) # здесь фильтр
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:follow_index')

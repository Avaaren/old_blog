from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import SearchVector
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.core.serializers import serialize

from .models import Post
from .forms import EmailPostForm, CommentForm, SearchForm, LoginForm, UserForm

from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count


def post_list(request, tag_slug=None):
    object_list = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag,})

# Create your views here.


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month, publish__day=day
                             )
    comments = post.comments.filter(active=True)
    new_comment = None
    if request.method == "POST":
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()
    post_tags_id = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_id).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:5] 
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts,
                                                     }
                  )


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{}({}) is recomends you reading {}'.format(
                cd['name'], cd['email'], post.title)
            message = 'Read {} at {}\n {}`s comments : \n {}'.format(
                post.title, post_url, cd['name'], cd['comment']
            )
            send_mail(subject, message, cd['email'], [cd['to']])
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
        results = Post.objects.annotate(search=SearchVector('title','body').filter(search=query))
        return render(
            request, 'blog/post/search.html', {
                'form': form,
                'query': query,
                'results': results
            }
        )


def user_login(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password'],
            )
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse('Vse zaebok!')
            else:
                return HttpResponse('User is inactive')
        else:
            return HttpResponse('Pizda')
    else:
        form = LoginForm()
    return render(request, 'blog/registration/login.html', {'form': form})
            

def register(request):
    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            return render(request, 'registration/register_done.html', {'user_form': user_form})
    else:
        user_form = UserForm()
    return render(request, 'registration/register.html', {'user_form': user_form})

def ajax_search(request):
    data = {}
    search_value = request.GET.get('value')
    print(search_value)
    s = Post.objects.filter(title__icontains=search_value.lower()).only('title')
    s = [str(x) for x in s]
    print(s)
    data['search_result'] = s
    return JsonResponse(data)
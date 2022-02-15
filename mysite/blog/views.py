from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, PostForm, TagForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


def post_list(request, tag_slug=None):
    object_list = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])

    paginator = Paginator(object_list, 4)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/list.html',
                  {'page': page,
                   'posts': posts,
                   'tag': tag})


# page of detail of post
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published', publish__year=year,
                             publish__month=month, publish__day=day)

    # list of active comments for current post
    comments = post.comments.filter(active=True)

    new_comment = None

    # user sent comment
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        comment_form = CommentForm()

    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts})


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    # if user enter data to forms
    # user sent comment
    if request.method == 'POST':
        form = EmailPostForm(request.POST)  # create form of data of user
        if form.is_valid():
            cd = form.cleaned_data  # read data of input
            post_url = request.build_absolute_uri(post.get_absolute_url())

            subject = post.title
            message = f'Link "{post_url}"\n{cd["comment"]}'
            send_mail(subject, message, 'kshatan03@gmail.com', [cd['to']])  # send mail
            sent = True  # true, when mail sent
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


def add_post(request):
    add = False
    new_post = None

    if request.method == 'POST':
        add_form = PostForm(data=request.POST)
        if add_form.is_valid():
            new_post = add_form.save(commit=False)
            new_post.save()

            add = True

    else:
        add_form = PostForm()
    return render(request, 'blog/post/add.html', {
        'add': add,
        'add_form': add_form,
        'post': new_post
    })


def add_tags(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    add = False

    if request.method == 'POST':
        tag = TagForm(request.POST)
        if tag.is_valid():
            cd = tag.cleaned_data
            post.tags.add(cd['tag'])
            add = True
    else:
        tag = TagForm()
    return render(request, 'blog/post/add_tags.html', {
        'add': add,
        'tag': tag,
        'post': post
    })


def post_search(request):
    form = SearchForm()
    query = None
    results = list()
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['query']
        search_vector = SearchVector('title', weight='A') + SearchVector('body', weight='B')
        search_query = SearchQuery(query)
        results = Post.objects.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)).filter(
            rank__gte=0.3).order_by('-rank')
    return render(request, 'blog/post/search.html', {'form': form,
                                                     'query': query,
                                                     'results': results})

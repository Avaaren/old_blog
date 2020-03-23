from django import template
from ..models import Post

from django.db.models import Count

register = template.Library()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    latest_posts = Post.published.all().order_by('-publish')[:5]
    return {'latest_posts': latest_posts}

@register.simple_tag()
def posts_count():
    return Post.published.count()

@register.simple_tag()
def most_commented_posts(count=5):
    return Post.published.annotate(most_commented=Count('comments')).order_by('-most_commented')[:count]
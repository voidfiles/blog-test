import logging
import functools
import itertools
import os

from jinja2 import Environment, FileSystemLoader
from pelican.utils import mkdir_p, clean_output_dir, copy
from werkzeug.contrib.atom import AtomFeed

from .content import Content

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
SITE_ROOT_DIR = os.path.join(BASE_DIR, 'root')
POST_DIR = os.path.join(BASE_DIR, 'posts')
SITE_DIR = os.path.join(BASE_DIR, 'site')
loader = FileSystemLoader(TEMPLATE_DIR)
env = Environment(loader=loader)


SITE_DATA = {
    'title': 'testing'
}


def walk_posts():
    for root, dirs, files in os.walk(POST_DIR):
        for name in files:
            yield root, name

required_fields = ['title', 'date']


def get_posts():
    for directory, file_name in walk_posts():
        post = Content.from_markdown_file(directory, file_name)

        if not set(required_fields) <= set(post.keys()):
            logger.warning('Droping %s because it is missing one of these required keys %s', file_name, required_fields)
            continue

        yield post


def render_post(ctx, post):
    template_name = post.template
    template = env.get_template(template_name)
    ctx['post'] = post
    ctx['site'] = SITE_DATA

    return template.render(**ctx)


def write_post(output_post_dir, ctx, post):
    post_dir = os.path.join(output_post_dir, post.slug)
    mkdir_p(post_dir)
    output_path = os.path.join(post_dir, 'index.html')
    output = render_post(ctx, post)
    logger.info("Writing post to path %s", output_path)
    with open(output_path, 'w') as fd:
        fd.write(output)

    return post


def render_index(ctx, posts):
    template = env.get_template('index.html')
    ctx['posts'] = posts
    ctx['site'] = SITE_DATA
    ctx['is_index'] = True
    return template.render(**ctx)


def write_index(output_post_dir, ctx, posts):
    output_path = os.path.join(output_post_dir, 'index.html')
    output = render_index(ctx, posts)
    logger.info("Writing index to path %s", output_path)
    with open(output_path, 'w') as fd:
        fd.write(output)


def render_feed(ctx, posts):
    base_url = ctx.get('rootpath') + 'feed.xml'
    feed = AtomFeed("My Blog", feed_url=base_url,
                    url=ctx.get('rootpath'),
                    subtitle="My example blog for a feed test.")

    for post in posts[0:10]:
        feed.add(post.get('title'), post.html, content_type='html',
                 author=post.get('author', 'None'), url=base_url + post.url_path, id=base_url + post.url_path,
                 updated=post.get('date'), published=post.get('date'))

    return feed.to_string()


def write_feed(output_post_dir, ctx, posts):
    output_path = os.path.join(output_post_dir, 'index.xml')
    output = render_feed(ctx, posts)
    logger.info("Writing feed to path %s", output_path)
    with open(output_path, 'w') as fd:
        fd.write(output)


def write_site(ctx):
    output_post_dir = os.path.join(SITE_DIR, 'posts')

    clean_output_dir(SITE_DIR, [])
    copy(SITE_ROOT_DIR, SITE_DIR)
    mkdir_p(output_post_dir)
    write_post_to_dir = functools.partial(write_post, output_post_dir, ctx)
    posts = itertools.imap(write_post_to_dir, get_posts())
    posts = itertools.ifilter(lambda x: x.get('published'), posts)
    posts = sorted(list(posts), key=lambda x: x.get('published'), reverse=True)
    write_index(SITE_DIR, ctx, posts)
    write_feed(SITE_DIR, ctx, posts)

import logging
import functools
import itertools
import os

from jinja2 import Environment, FileSystemLoader
from pelican.utils import mkdir_p, clean_output_dir, copy

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


def get_posts():
    return (Content.from_markdown_file(directory, file_name) for directory, file_name in walk_posts())


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
    logger.info("Writing post to path %s", output_path)
    with open(output_path, 'w') as fd:
        fd.write(output)


def write_site(ctx):
    output_post_dir = os.path.join(SITE_DIR, 'posts')

    clean_output_dir(SITE_DIR, [])
    copy(SITE_ROOT_DIR, SITE_DIR)
    mkdir_p(output_post_dir)
    write_post_to_dir = functools.partial(write_post, output_post_dir, ctx)
    posts = list(itertools.imap(write_post_to_dir, get_posts()))
    posts = sorted(posts, key=lambda x: x.get('published'), reverse=True)
    write_index(SITE_DIR, ctx, posts)

import os
import six
from IPython import embed

import frontmatter
from pelican.utils import slugify
from markdown2 import Markdown

from .exceptions import NalContentException
from .utils import get_date


class NalMarkdown(Markdown):
    def _extract_metadata(self, text):
        # fast test
        if not text.startswith("---"):
            return text

        content = frontmatter.loads(text)
        self.metadata = content.metadata
        return content.content


def markdown(text, html4tags=False, tab_width=4,
             safe_mode=None, extras=None, link_patterns=None,
             use_file_vars=False):

    return NalMarkdown(html4tags=html4tags, tab_width=tab_width,
                       safe_mode=safe_mode, extras=extras,
                       link_patterns=link_patterns,
                       use_file_vars=use_file_vars).convert(text)


class Content(dict):

    @classmethod
    def from_markdown_file(cls, directory, file_name):
        if not file_name.endswith('.md'):
            return None

        path = os.path.join(directory, file_name)
        text = None
        text = ''
        with open(path, 'r') as fd:
            text = fd.read()

        if not text:
            raise NalContentException('file: %s has no content' % (path))

        html = markdown(text, extras=["metadata"])
        metadata = html.metadata

        date = metadata.get('date')
        if date:
            metadata['date'] = get_date(date)

        content = cls(**metadata)

        content.html = html
        content.text = text

        return content

    @property
    def slug(self):
        slug_override = self.get('slug')
        if slug_override:
            return slug_override

        return slugify(self.get('title', 'missing-title'))

    @property
    def url_path(self):
        return 'posts/%s' % (self.slug)

    @property
    def template(self):
        return u'%s.html' % self.get('template', 'post')

import os

from pelican.utils import slugify
import markdown2

from .exceptions import NalContentException
from .utils import get_date


class Content(dict):

    @classmethod
    def from_markdown_file(cls, directory, file_name):
        path = os.path.join(directory, file_name)
        text = None
        with open(path) as fd:
            text = fd.read()

        if not text:
            raise NalContentException('file: %s has no content' % (path))

        html = markdown2.markdown(text, extras=["metadata"])
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
        return '/posts/%s' % (self.slug)

    @property
    def template(self):
        return u'%s.html' % self.get('template', 'post')

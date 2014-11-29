import logging
import click

logger = logging.getLogger('nal_blog_cli')


@click.group()
def cli():
    import sys

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


@cli.command()
@click.option('--rootpath', default='/', help='Root path of the site')
def build(rootpath):
    from .build import write_site
    click.echo('Writing out site')
    write_site({'rootpath': rootpath})
    click.echo('Writing out site done')


@cli.command()
def watch():
    import time
    import sys
    from pelican.utils import folder_watcher
    from .build import write_site, TEMPLATE_DIR, SITE_ROOT_DIR, POST_DIR, SITE_DIR
    from .server import get_server

    watchers = {
        'posts': folder_watcher(POST_DIR, ['.md']),
        'root': folder_watcher(SITE_ROOT_DIR, ['']),
        'templates': folder_watcher(TEMPLATE_DIR, ['.html']),
    }

    server_thread = get_server(path=SITE_DIR)
    server_thread.daemon = True
    server_thread.start()

    try:
        logger.info('AutoReload setup')

        def _ignore_cache(pelican_obj):
            if pelican_obj.settings['AUTORELOAD_IGNORE_CACHE']:
                pelican_obj.settings['LOAD_CONTENT_CACHE'] = False

        while True:
            try:
                # Check source dir for changed files ending with the given
                # extension in the settings. In the theme dir is no such
                # restriction; all files are recursively checked if they
                # have changed, no matter what extension the filenames
                # have.
                modified = {k: next(v) for k, v in watchers.items()}

                if any(modified.values()):
                    print('\n-> Modified: {}. re-generating...'.format(
                        ', '.join(k for k, v in modified.items() if v)))

                    write_site()
            except KeyboardInterrupt:
                logger.warning("Keyboard interrupt, quitting.")
                break

            except Exception:
                logger.exception('yo')

            finally:
                time.sleep(.5)  # sleep to avoid cpu load

    except Exception as e:
        logger.exception('yo')
        sys.exit(getattr(e, 'exitcode', 1))

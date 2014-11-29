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
    logger.info('Writing out site...')
    write_site({'rootpath': rootpath})
    logger.info('...done')


@cli.command()
@click.option('--rootpath', default='/', help='Root path of the site')
def watch(rootpath):
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

    logger.info('AutoReload setup')

    try:
        while True:
            try:
                # Check source dir for changed files ending with the given
                # extension in the settings. In the theme dir is no such
                # restriction; all files are recursively checked if they
                # have changed, no matter what extension the filenames
                # have.
                modified = {k: next(v) for k, v in watchers.items()}

                if any(modified.values()):
                    print('\nModified: {}. re-generating...'.format(
                        ', '.join(k for k, v in modified.items() if v)))

                    write_site({'rootpath': rootpath})
            except KeyboardInterrupt:
                logger.warning("Keyboard interrupt, quitting.")
                break

            except Exception:
                logger.exception('Failed to rgenerate website. Eating, will try again.')
            finally:
                time.sleep(.5)  # sleep to avoid cpu load

    except Exception as e:
        logger.exception('Failed to rgenerate website. Exiting.')
        sys.exit(getattr(e, 'exitcode', 1))

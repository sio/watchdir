'''
Implement multiple watch folders for torrent clients that don't offer that
functionality.

Relies on inotify mechanism provided by Linux kernel
'''


import logging
import os.path
import re
from time import sleep

from inotify.adapters import Inotify


logging.basicConfig()
log = logging.getLogger(__name__)


def main():  # TODO: commandline arguments
    destination = '/sample/destination'
    for torrent in watch_torrents('/tmp/test'):
        if download(torrent, destination):
            post_download(torrent)


def download(torrent, destination, max_retries=5, worker=None):
    '''
    Add torrent file to the client with specified destination directory.
    Returns False if downloading was not successful, otherwise True.
    '''
    RETRY_DELAY = 1

    if worker is None:
        worker = download_with_transmission

    retry = 0
    success = False
    while retry < max_retries:
        try:
            worker(torrent, destination)
            success = True
            break
        except Exception as e:
            retry += 1
            log.error('{} when trying to add {} (attempt {}/{})'.format(
                e.__class__.__name__,
                torrent,
                retry,
                max_retries,
            ))
            if retry == max_retries:
                log.error('giving up on {}'.format(torrent))
            else:
                sleep(RETRY_DELAY)
    return success


def download_with_transmission(torrent, destination):
    '''
    Transmission-specific downloading logic
    '''
    # TODO: call transmission-cli
    print('Downloading {} to {}'.format(torrent, destination))


def post_download(torrent):
    '''
    Process the torrent file after adding it to the client
    '''
    # TODO: rename/move torrent file after adding
    print('Post-processing for {}'.format(torrent))


def watch_torrents(*directories):
    '''
    Yield file paths for new torrent files in any of the provided directories.
    This generator does not quit unless interrupted by an exception.
    '''
    torrent = re.compile(r'.*\.torrent', re.IGNORECASE)

    watcher = Inotify()
    for dirname in directories:
        if os.path.isdir(dirname):
            watcher.add_watch(dirname)
        else:
            log.error('invalid watch directory: {}'.format(dirname))

    try:
        for _, events, path, filename in watcher.event_gen(yield_nones=False):
            if {'IN_CLOSE_WRITE', 'IN_MOVED_TO'}.intersection(events) \
            and torrent.match(filename):
                yield os.path.join(path, filename)
    except KeyboardInterrupt:
        return []


if __name__ == '__main__':
    main()

'''
Implement multiple watch folders for torrent clients that don't offer that
functionality.

Relies on inotify mechanism provided by Linux kernel
'''


import logging
import os.path
import re
from subprocess import Popen
from time import sleep

from inotify.adapters import Inotify


logging.basicConfig()
log = logging.getLogger(__name__)


def main(client=None, post_process=None):  # TODO: commandline arguments
    '''
    Watch a directory for new torrent files and add them to the client

    Arguments allow to customize which client is used and how to process
    torrent files after adding.

    Default behavior
        worker: uses transmission-cli
        post_process: append '.added' suffix to torrent file name
    '''
    destination = '/sample/destination'

    if post_process is None:
        post_process = rename

    for torrent in watch_torrents('/tmp/test'):
        if download(torrent, destination, worker=client):
            post_process(torrent)


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
    log.info('Downloading {} to {}'.format(torrent, destination))
    process = Popen([
        'transmission-remote',
        '--add',
        torrent,
        '--download-dir',
        destination,
    ])
    exit_code = process.wait()
    if exit_code != 0:
        raise ExitCodeError('transmission-remote exited with code {}'.format(exit_code))


class ExitCodeError(Exception):
    '''Raised when subprocess signals about error via exit code'''


def rename(torrent, suffix='.added'):
    '''Rename the torrent file after adding it to the client'''
    os.rename(torrent, torrent + suffix)


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

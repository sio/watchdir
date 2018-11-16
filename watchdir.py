'''
Implement multiple watch folders for torrent clients that don't offer that
functionality.

Relies on inotify mechanism provided by Linux kernel
'''


import logging
import os
import re
import sys
from argparse import ArgumentParser
from subprocess import Popen, PIPE
from time import sleep

from inotify.adapters import Inotify


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def main(client=None, post_process=None):
    '''
    Watch a directory for new torrent files and add them to the client

    Arguments allow to customize which client is used and how to process
    torrent files after adding.

    Default behavior
        worker: uses transmission-cli
        post_process: append '.added' suffix to torrent file name
    '''
    if post_process is None:
        post_process = rename

    args = get_arguments()
    for dirname in (args.watchdir, args.destination):
        if not os.path.exists(dirname):
            log.info('creating directory: {}'.format(dirname))
            os.makedirs(dirname)

    for torrent in watch_torrents(args.watchdir):
        if download(torrent, args.destination, worker=client, extra_args=args.extras):
            post_process(torrent)


def get_arguments():
    '''Parse command line arguments for watchdir script'''
    cmdline = ArgumentParser(
        description='Watch for new torrent files in the specified directory',
        epilog='If any of the provided directories do not exist, they will be created',
    )
    cmdline.add_argument(
        'watchdir',
        metavar='WATCHDIR',
        help='Path to watch directory with torrent files',
    )
    cmdline.add_argument(
        'destination',
        metavar='DESTINATION',
        help='Path to download destination',
    )
    cmdline.add_argument(
        'extras',
        nargs='*',
        help='Any extra arguments will be passed to the torrent client "as is"',
    )
    args = cmdline.parse_args(sys.argv[1:3])
    args.extras = sys.argv[3:]  # we do not need to parse these
    return args


def download(torrent, destination, max_retries=5, worker=None, extra_args=None):
    '''
    Add torrent file to the client with specified destination directory.

    Parameters
        torrent
            Torrent file path
        destination
            Download directory path
        max_retries
            Maximum number of retries if worker fails
        worker
            The function that does actual work (adds torrent file to client).
            Uses transmission-remote by default.
        extra_args
            Sequence of extra arguments to pass to worker on each invokation

    Returns False if downloading was not successful, otherwise True.
    '''
    RETRY_DELAY = 1

    if worker is None:
        worker = download_with_transmission

    log.info('Downloading {} to {}'.format(torrent, destination))
    retry = 0
    success = False
    while retry < max_retries:
        try:
            worker(torrent, destination, extra_args=extra_args)
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


def download_with_transmission(torrent, destination, extra_args=None):
    '''
    Transmission-specific downloading logic

    Extra args are passed to transmission-remote verbatim.

    Daemon RPC credentials can be set via TR_HOST and TR_AUTH environment
    variables.
    '''
    host = os.environ.get('TR_HOST')
    if not host:
        host = 'localhost:9091'

    command = [
        'transmission-remote',
        host,
        '--add',
        os.path.abspath(torrent),
        '--download-dir',
        os.path.abspath(destination),
    ]
    if os.environ.get('TR_AUTH'):
        command.append('--authenv')

    if extra_args:
        command += list(extra_args)

    process = Popen(command, stdout=PIPE, stderr=PIPE)
    exit_code = process.wait()
    if exit_code != 0:
        log.error(process.communicate()[1].decode())
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
    torrent = re.compile(r'.*\.torrent$', re.IGNORECASE)

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
        raise StopIteration


if __name__ == '__main__':
    main()

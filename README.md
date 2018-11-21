# Multiple watch directories for any torrent client

## Installation

Watchdir can be installed with pip:

```
$ pip install https://github.com/sio/watchdir/archive/master.zip
```


## Usage with transmission-remote (default)

After installing you can launch any number of watchdir instances via
`transmission-watch`:

```
usage: transmission-watch [-h] WATCHDIR DESTINATION [extras [extras ...]]

Watch for new torrent files in the specified directory

positional arguments:
  WATCHDIR     Path to watch directory with torrent files
  DESTINATION  Path to download destination
  extras       Any extra arguments will be passed to the torrent client "as
               is"

optional arguments:
  -h, --help   show this help message and exit

If any of the provided directories do not exist, they will be created
```

If `transmission-daemon` runs on non-default port or requires authentication,
use environment variables:

- `TR_HOST=hostname:port`
- `TR_AUTH=username:password`


## Usage with other clients

Watchdir can be easily tailored to fit any other torrent client:

```python
import watchdir
watchdir.main(
    client=YOUR_CLIENT_HANDLER,
    post_process=YOUR_POSTPROCESSING_FUNCTION
)
```

Check [watchdir.py](watchdir.py) for function signatures of `client` and
`post_process`.

The resulting script will provide the same commandline interface as
`transmission-watch`.


## Support and contributing

If you need help using watchdir from command line or including it into your
custom scripts, please create **[an issue](https://github.com/sio/watchdir/issues)**.
Issues are also the primary venue for reporting bugs and posting feature
requests. General discussion related to this project is also acceptable and
very welcome!

In case you wish to contribute code or documentation, feel free to open **[a
pull request](https://github.com/sio/watchdir/pulls)**. That would certainly make
my day!

I'm open to dialog and I promise to behave responsibly and treat all
contributors with respect. Please try to do the same, and treat others the way
you want to be treated.

If for some reason you'd rather not use the issue tracker, contacting me via
email is OK too. Please use a descriptive subject line to enhance visibility
of your message. Also please keep in mind that public discussion channels are
preferable because that way many other people may benefit from reading past
conversations.  My email is visible under the GitHub profile and in the commit
log.


## License and copyright

Copyright 2018 Vitaly Potyarkin

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

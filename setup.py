from setuptools import setup, find_packages

setup(
    name='watchdir',
    version='0.1.0-git',
    description='Use multiple watch directories with any torrent client',
    url='https://github.com/sio/watchdir',
    author='Vitaly Potyarkin',
    author_email='sio.wtf@gmail.com',
    license='Apache',
    platforms='any',
    entry_points={
        'console_scripts': ['transmission-watch=watchdir:main'],
    },
    py_modules=['watchdir'],
    install_requires=[
        'inotify',
    ],
    python_requires='>=3.3',
    zip_safe=True,
)

import os

from setuptools import setup
from setuptools import find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''
try:
    CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()
except IOError:
    CHANGES = ''

version = '0.1dev'

install_requires = [
    'Kotti>=0.10b1',
    'functools32',
    #'PySide',
    'lxml',
    #'sqlalchemy',
    'python-amazon-simple-product-api',
    'xlrd'
]


setup(
    name='busybrowse',
    version=version,
    description="Add on for Kotti",
    long_description='\n\n'.join([README, CHANGES]),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "License :: Repoze Public License",
    ],
    author='Kotti developers',
    author_email='kotti@googlegroups.com',
    url='https://github.com/cruxlog/busybrowse',
    keywords='kotti web cms wcms pylons pyramid sqlalchemy bootstrap',
    license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=[],
    dependency_links=[],
    entry_points={
        'fanstatic.libraries': [
            'busybrowse = busybrowse.fanstatic:library',
        ],
        'console_scripts': [
            'busybrowse-importer = busybrowse.importer:importer_command',
        ]
    },
    extras_require={},
)

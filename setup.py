
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'a HTML/JS/CSS bundler',
    'author': 'Jan Kowalleck',
    #'url': 'URL to get it at.',
    #'download_url': 'Where to download it.',
    'author_email': 'jan.kowalleck@googlemail.com',
    'version': '0.1',
    'install_requires': ['beautifulsoup4', 'html5lib'],
    'packages': ['Bundler'],
    'scripts': [],
    'name': 'bundle'
}

setup(**config)

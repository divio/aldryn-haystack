# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name="aldryn-haystack",
    version=__import__('aldryn_haystack').__version__,
    description='An opinionated haystack setup bundled as an Aldryn Addon. To be used together with aldryn-django.',
    author='Divio AG',
    author_email='info@divio.ch',
    url='https://github.com/aldryn/aldryn-haystack',
    packages=find_packages(),
    install_requires=(
        'aldryn-django',
        'elasticsearch',
        'requests-aws4auth',
        'django-haystack',
        'furl',
    ),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Framework :: Django',
    ]
)

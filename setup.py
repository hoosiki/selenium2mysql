#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

install_requireent = []

setup_requires = [
        'csv2sqllike',
        'selenium',
        'dict',
        'validators'
        ]

install_requires = [
        'csv2sqllike',
        'selenium',
        'dict',
        'validators'
        ]

setup(
    name='selenium2mysql',
    author='Junsang Park',
    author_email='publichey@gmail.com',
    url='https://github.com/hoosiki/selenium2mysql',
    version='1.0.3',
    long_description=readme,
    long_description_content_type="text/markdown",
    description='scraper using selenium for general purposes',
    packages=find_packages(),
    license='BSD',
    include_package_date=False,
    setup_requires=setup_requires,
    install_requires=install_requires,
    download_url='https://github.com/hoosiki/selenium2mysql/blob/master/dist/selenium2mysql-1.0.3.tar.gz'
)

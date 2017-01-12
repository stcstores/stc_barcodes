#!/usr/bin/env python

from distutils.core import setup

setup(
    name='stc_barcodes',
    version='1.0.01',
    description='Barcode order manager',
    author='Luke Shiner',
    author_email='luke@lukeshiner.com',
    install_requires=['jinja2', 'tabler'],
    packages=['stc_barcodes']
)

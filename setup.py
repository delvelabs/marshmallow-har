#!/usr/bin/env python

from setuptools import setup

setup(name='marshmallow-har',
      version='0.5',
      description='Simple set of marshmallow schemas to load/dump the HTTP Archive (HAR) format.',
      author='Delve Labs inc.',
      author_email='info@delvelabs.ca',
      url='https://github.com/delvelabs/marshmallow-har',
      packages=['marshmallow_har'],
      install_requires=[
          'marshmallow',
      ])

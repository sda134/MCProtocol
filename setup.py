# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='mcprotcol',
    version='0.1.0',
    description='三菱シーケンサと通信する為のパッケージです。',
    long_description=readme,
    author='Sada134',
    author_email='saji.sus4@gmail.com',
    url='https://github.com/Sada134/mcprotocol',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)


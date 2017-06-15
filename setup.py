#!/usr/bin/env python
# coding: utf-8
from setuptools import setup, find_packages

setup(
    name='django-unifi-portal',
    version='0.0.3',
    author='bsab',
    author_email='tino.saba@gmail.com',
    url='https://github.com/bsab/django-unifi-portal',
    description='Authenticate Unifi WiFi Guests with Django.',
    long_description=open('README.rst').read(),
    packages=find_packages(exclude=['test*']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "django>=1.10",
        "django-braces==1.9.0",
        "requests",
        "django-material",
        "requests-toolbelt",
        "django-braces",
        "django-rest-framework-social-oauth2",
        "Pillow",
    ],
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
    ],
)
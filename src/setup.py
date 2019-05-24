"""
Copyright 2016 Juergen Edelbluth

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import re

from setuptools import setup

__author__ = 'Juergen Edelbluth'


def read_requirements_from_file(file: str) -> list:
    requirements = []
    with open(file, 'r') as f:
        lines = f.readlines()
    for l in lines:
        r = l.strip()
        if len(r) > 0:
            requirements.append(r)
    return requirements


def read_helper(file: str) -> str:
    with open(file, 'r') as f:
        return f.read()


def read_version_from_file(file: str) -> str:
    version_pattern = re.compile(r'^__version__\s*=\s*\'(?P<version>\d(\.\d)+)\'\s*$')
    with open(file, 'r') as f:
        for l in f.readlines():
            matcher = version_pattern.match(l)
            if matcher:
                return matcher.group('version')
    return '0.0.0'


__version__ = read_version_from_file('blackred/blackred.py')

REQUIREMENTS = read_requirements_from_file('../requirements.txt')
TEST_REQUIREMENTS = REQUIREMENTS + read_requirements_from_file('../test-requirements.txt')


setup(
    name='BlackRed',
    packages=['blackred'],
    version=__version__,
    long_description=read_helper('README'),
    license='Apache License 2.0',
    description='Dynamic blacklisting library using redis.',
    author=__author__,
    author_email='dev@juergen.rocks',
    url='https://github.com/edelbluth/blackred',
    download_url='https://github.com/edelbluth/blackred/tarball/v' + __version__,
    keywords=['protection', 'redis', 'django', 'ban', 'filter'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Networking',
    ],
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
)

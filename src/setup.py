"""
Copyright 2015 Juergen Edelbluth

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


__author__ = 'Juergen Edelbluth'


from distutils.core import setup


def read_helper(file: str) -> str:
    with open(file, 'r') as f:
        return f.read()


setup(
    name='BlackRed',
    packages=['blackred'],
    version='0.1.5',
    # long_description=read_helper('README'),
    license='Apache Software License 2.0',
    description='Dynamic blacklisting library using redis.',
    author='Juergen Edelbluth',
    author_email='dev@juergen.rocks',
    url='https://github.com/edelbluth/blackred',
    download_url='https://github.com/edelbluth/blackred/tarball/v0.1.5',
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
    requires=['redis'],
)

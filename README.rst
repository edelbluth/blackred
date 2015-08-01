BlackRed
========

BlackRed is a dynamic blacklisting library using `Redis <http://redis.io/>`__ as a fast and reliable
storage backend.

.. image:: https://coveralls.io/repos/edelbluth/blackred/badge.svg?branch=master
   :target: https://coveralls.io/r/edelbluth/blackred?branch=master
.. image:: https://travis-ci.org/edelbluth/blackred.svg?branch=master
   :target: https://travis-ci.org/edelbluth/blackred
.. image:: https://readthedocs.org/projects/blackred/badge/?version=latest
   :target: https://blackred.readthedocs.org/index.html
.. image:: https://img.shields.io/pypi/v/BlackRed.svg
   :target: https://pypi.python.org/pypi/BlackRed
.. image:: https://img.shields.io/pypi/status/BlackRed.svg
   :target: https://pypi.python.org/pypi/BlackRed
.. image:: https://img.shields.io/pypi/dd/BlackRed.svg
   :target: https://pypi.python.org/pypi/BlackRed
.. image:: https://img.shields.io/github/license/edelbluth/blackred.svg
   :target: https://github.com/edelbluth/blackred
.. image:: https://img.shields.io/badge/juergen-rocks-000033.svg?style=flat
   :target: https://juergen.rocks/


How does it work?
-----------------

Example: A user tries to log on a system and fails because of bad credentials or an inactivated account. This failure
can be recorded with BlackRed. After three failures within a certain time the account gets locked for an extended
period of time. This limits brute force attacks. All time periods are configurable.

In a desktop application you would record the username in question with BlackRed. In a web environment, the requester's
IP address would be the perfect.

In the redis database, two lists are kept: A watchlist that records the failures, and the blacklist that contains
blocked items.


Links
-----

- Author: Juergen Edelbluth, `https://juergen.rocks/ <https://juergen.rocks/>`_,
  `@JuergenRocks <https://twitter.com/JuergenRocks>`_
- Build Status: `https://travis-ci.org/edelbluth/blackred <https://travis-ci.org/edelbluth/blackred>`_
- Project Homepage: `https://github.com/edelbluth/blackred <https://github.com/edelbluth/blackred>`_
- Documentation: `https://blackred.readthedocs.org/index.html <https://blackred.readthedocs.org/index.html>`_
- PyPi Page: `https://pypi.python.org/pypi/blackred <https://pypi.python.org/pypi/blackred>`_
- German Description: `https://juergen.rocks/art/mit-blackred-benutzer-logins-absichern.html
  <https://juergen.rocks/art/mit-blackred-benutzer-logins-absichern.html>`_


License
-------

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


See LICENSE.txt for complete License Text

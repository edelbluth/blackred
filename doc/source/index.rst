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


Requirements
------------

BlackRed runs only under Python 3.3, 3.4, 3.5 and PyPy3. There's no support for Python 2.

The only thing BlackRed needs is the `redis package <https://pypi.python.org/pypi/redis>`__ >= 2.10.


Jump Start
----------

Installation can be done with ``pip install blackred``. Usage is as easy, here an example for a simple user login:

.. code-block:: python

   import blackred

   def login(username, password, request_ip):
       br = blackred.BlackRed()
       if br.is_blocked(request_ip):
           return False
       if not authenticate(username, password):
           br.log_fail(request_ip)
           return False
       return True

More examples: :doc:`Example Usage <doc/example-usage>`.

Usage
-----

.. toctree::
   :maxdepth: 2
   :glob:

   doc/configuration
   doc/example-usage

API Documentation
-----------------

.. toctree::
   :maxdepth: 2
   :glob:

   api/blackred

Links
-----

- Author: Juergen Edelbluth, `https://juergen.rocks/ <https://juergen.rocks/>`_,
  `@JuergenRocks <https://twitter.com/JuergenRocks>`_
- Build Status: `https://travis-ci.org/edelbluth/blackred <https://travis-ci.org/edelbluth/blackred>`_
- Project Homepage: `https://github.com/edelbluth/blackred <https://github.com/edelbluth/blackred>`_
- PyPi Page: `https://pypi.python.org/pypi/blackred <https://pypi.python.org/pypi/blackred>`_
- German Description (for 0.2 version): `https://juergen.rocks/art/mit-blackred-benutzer-logins-absichern.html
  <https://juergen.rocks/art/mit-blackred-benutzer-logins-absichern.html>`_
- Documentation (this one): `https://blackred.readthedocs.org/index.html <https://blackred.readthedocs.org/index.html>`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


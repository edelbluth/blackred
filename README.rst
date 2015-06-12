BlackRed
========

BlackRed is a dynamic blacklisting library using `Redis <http://redis.io/>`_ as a fast and reliable storage backend.


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

BlackRed runs only under Python 3.2, 3.3, 3.4, 3.5 and PyPy3. There's no support for Python 2.

The only thing BlackRed needs is `redis <https://pypi.python.org/pypi/redis>`_.


Basic Usage
-----------

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


API Documentation
-----------------

BlackRed has a very simple and intuitive API.

The constructor ``blackred.BlackRed`` accepts these parameters, all optional:

- ``redis_host``: Hostname, IP Address or Socket, defaults to ``localhost``
- ``redis_port``: Port Number, defaults to ``6397``
- ``redis_db``: DB Number, defaults to ``0``
- ``redis_use_socket``: True, when a socket should be used instead the TCP/IP connection, defaults to ``False``

To record a login or action failure, use the ``log_fail`` method. It requires one parameter:

- ``item``: A username, an IP address or whatever you use to identify the failure

To check if some item is already on the blacklist, use the ``is_blocked`` method, or the ``is_not_blocked`` method to
check for the opposite. Both methods require one parameter:

- ``item``: A username, an IP address or whatever you use to identify the try

If you want to unblock something before it gets removed from the blacklist automatically, use the ``unblock`` method. It
requires one parameter:

- ``item``: A username, an IP address or whatever you use to identify the try


Redis Connection Parameters
---------------------------

The Redis connection parameters can be passed to the constructor ``blackred.BlackRed`` or configured as defaults for
every new instance (see `Settings and Defaults`_ below). Typically, you should be fine with the defaults.

If you want to use a unix socket to connect, set the ``redis_use_socket`` constructor parameter to ``True`` and provide
the absolute path to the socket with the ``redis_host`` parameter, example:

.. code-block:: python

   import blackred

   br = blackred.BlackRed(redis_host='/var/run/redis/redis.sock', redis_use_socket=True)


Settings and Defaults
---------------------

Besides the connection parameters, all settings are global for all instances of ``blackred.BlackRed``. The settings are
kept in the ``blackred.BlackRed.Settings`` class.

Global settings
...............

- ``blackred.BlackRed.Settings.WATCHLIST_KEY_TEMPLATE``: Template for creating watchlist keys in the Redis database.
  Defaults to ``'BlackRed:WatchList:{:s}'`` and should only be changed when this collides with one of your namespaces.
- ``blackred.BlackRed.Settings.BLACKLIST_KEY_TEMPLATE``: Same for blacklist keys. Defaults to
  ``'BlackRed:BlackList:{:s}'`` and should only be changed when this collides with one of your namespaces.
- ``blackred.BlackRed.Settings.WATCHLIST_TTL_SECONDS``: Time in seconds for an item to stay on the watchlist. If after
  a logged failure a new failure appears within this time frame, the fail count is increased. If not, the entry is
  deleted automatically. Defaults to 180 (3 minutes).
- ``blackred.BlackRed.Settings.BLACKLIST_TTL_SECONDS``: Time in seconds for an item to stay on the blacklist. Defaults
  to 86400 (24 hours). After that time, the entry is deleted automatically.
- ``blackred.BlackRed.Settings.WATCHLIST_TO_BLACKLIST_THRESHOLD``: Number of fails for an item to get from the watchlist
  to the blacklist. Defaults to 3.
- ``blackred.BlackRed.Settings.BLACKLIST_REFRESH_TTL_ON_HIT``: If an item is already on the blacklist and is checked
  with ``BlackRed.is_blocked`` or ``BlackRed.is_not_blocked`` while on the blacklist, the time to live for the
  blacklist entry is reset to ``blackred.BlackRed.Settings.BLACKLIST_TTL_SECONDS``. So if this is set to ``True``
  (that's the default value) and a blocked user tries to login after 12 hours after blacklisting, his blacklist time is
  increased to another 24 hours.


Defaults for new instances
..........................

These settings are the defaults for the ``blackred.BlackRed`` constructor.

- ``blackred.BlackRed.Settings.REDIS_HOST``: Hostname, IP Address or socket, defaults to ``'localhost'``
- ``blackred.BlackRed.Settings.REDIS_PORT``: TCP-Port for Redis, defaults to ``6379``
- ``blackred.BlackRed.Settings.REDIS_DB``: The Redis database number, defaults to ``0``
- ``blackred.BlackRed.Settings.REDIS_USE_SOCKET``: Tell the ``BlackRed`` class to use a unix socket instead of a TCP/IP
  connection. Defaults to ``False``


Links
-----

- Author: Juergen Edelbluth, `https://juergen.rocks/ <https://juergen.rocks/>`_,
  `@JuergenRocks <https://twitter.com/JuergenRocks>`_
- Build Status: `https://travis-ci.org/edelbluth/blackred <https://travis-ci.org/edelbluth/blackred>`_
- Project Homepage: `https://github.com/edelbluth/blackred <https://github.com/edelbluth/blackred>`_
- PyPi Page: `https://pypi.python.org/pypi/blackred <https://pypi.python.org/pypi/blackred>`_


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

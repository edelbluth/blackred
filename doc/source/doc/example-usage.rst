Example Usage
=============

BlackRed features a very simple and intuitive API. :doc:`Go to API documentation <../api/blackred>`.

Simple Use
----------

With everything in defaults (Host is ``localhost``, port is ``6379`` and so on), you can use BlackRed right out of the
box:

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

The :py:class:`BlackRed constructor <blackred.blackred.BlackRed>` offers a wide range of on-the-fly settings for
the new instance. To keep your code nice and clean when you use the same settings most of the time, you can use the
`Settings Predefinition`_.

Item Selection
--------------

For a web or network based application, a good item to check and block is the client IP address of the requestor.

In other environments, you might choose anything else that identifies a request source uniqually. Most important: The
item must be represented by a ``str``.

Settings Predefinition
----------------------

To make the using of BlackRed easier, you can change the default settings for new instances by changing the values of
the attributes of the :py:class:`BlackRed.Settings <blackred.blackred.BlackRed.Settings>` class. Changes are only valid
for new instances created after the changes. Already existing instances are not changed.

.. note::

   BlackRed versions before 0.3.0 had a different settings approach. Settings where separated into global settings and
   settings for new instances. With 0.3.0, all settings are only valid for new instances. Keep that in mind when
   upgrading from an older version.

Example: Enable `Anonymization`_ by default:

.. code-block:: python

   import blackred

   blackred.BlackRed.Settings.ANONYMIZATION = True

   def login(username, password, request_ip):
       br = blackred.BlackRed()
       if br.is_blocked(request_ip):
           return False
       if not authenticate(username, password):
           br.log_fail(request_ip)
           return False
       return True


Use Unix Socket instead of TCP/IP connection
--------------------------------------------

If you want to use a unix socket to connect, set the ``redis_use_socket`` constructor parameter to ``True`` and provide
the absolute path to the socket with the ``redis_host`` parameter, example:

.. code-block:: python

   import blackred

   br = blackred.BlackRed(redis_host='/var/run/redis/redis.sock', redis_use_socket=True)

As always, those settings can be predefined (see `Settings Predefinition`_) as defaults for all new instances:

.. code-block:: python

   import blackred

   blackred.BlackRed.Settings.REDIS_USE_SOCKET = True
   blackred.BlackRed.Settings.REDIS_HOST = '/var/run/redis/redis.sock'


Anonymization
-------------

Sometimes it's necessary to hash the item's values to ensure privacy of the requester. BlackRed can easily support you.
Just set the :py:attr:`ANONYMIZATION <blackred.blackred.BlackRed.Settings.ANONYMIZATION>` attribute to ``True``:

.. code-block:: python

   import blackred

   blackred.BlackRed.Settings.ANONYMIZATION = True


Use a Redis password (aka Redis AUTH feature)
---------------------------------------------

To activate authentication, you can use the ``redis_auth`` parameter of the constructor:

.. code-block:: python

   import blackred

   br = blackred.BlackRed(redis_auth='my_password')

As always, this settings can be predefined (see `Settings Predefinition`_) as default for all new instances:

.. code-block:: python

   import blackred

   blackred.BlackRed.Settings.REDIS_AUTH = 'my_password'

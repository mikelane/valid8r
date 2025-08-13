valid8r.core
============

.. py:module:: valid8r.core

.. autoapi-nested-parse::

   Core validation components.



Submodules
----------

.. toctree::
   :maxdepth: 1

   /autoapi/valid8r/core/combinators/index
   /autoapi/valid8r/core/maybe/index
   /autoapi/valid8r/core/parsers/index
   /autoapi/valid8r/core/validators/index


Functions
---------

.. autoapisummary::

   valid8r.core.parse_cidr
   valid8r.core.parse_ip
   valid8r.core.parse_ipv4
   valid8r.core.parse_ipv6


Package Contents
----------------

.. py:function:: parse_cidr(text, *, strict = True)

   Parse a CIDR network string (IPv4 or IPv6).

   Uses ipaddress.ip_network under the hood. By default ``strict=True``
   so host bits set will fail. With ``strict=False``, host bits are masked.

   Error messages:
   - value must be a string
   - value is empty
   - has host bits set (when strict and host bits are present)
   - not a valid network (all other parsing failures)


.. py:function:: parse_ip(text)

   Parse a string as either an IPv4 or IPv6 address.

   Trims surrounding whitespace only.

   Error messages:
   - value must be a string
   - value is empty
   - not a valid IP address


.. py:function:: parse_ipv4(text)

   Parse an IPv4 address string.

   Trims surrounding whitespace only. Returns Success with a concrete
   IPv4Address on success, or Failure with a deterministic error message.

   Error messages:
   - value must be a string
   - value is empty
   - not a valid IPv4 address


.. py:function:: parse_ipv6(text)

   Parse an IPv6 address string.

   Trims surrounding whitespace only. Returns Success with a concrete
   IPv6Address on success, or Failure with a deterministic error message.

   Error messages:
   - value must be a string
   - value is empty
   - not a valid IPv6 address



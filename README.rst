###############
pl-s3path
###############

.. image:: https://img.shields.io/github/tag/fnndsc/pl-s3path.svg?style=flat-square   :target: https://github.com/FNNDSC/pl-s3path
.. image:: https://img.shields.io/docker/build/fnndsc/pl-s3path.svg?style=flat-square   :target: https://hub.docker.com/r/fnndsc/pl-s3path/


Abstract
========

A CUBE 'ds' plugin to adapt pl-pacsquery output to pl-s3retrieve input.

Preconditions
=============

Input must contain success.txt generated by the pl-pacsquery plugin.


Run
===
Using ``docker run``
--------------------

.. code-block:: bash

  docker run -t --rm
    -v $(pwd)/../pl-pacsquery/out:/input \
    -v $(pwd)/output:/output             \
    fnndsc/pl-s3path s3path.py           \ 
    --seriesUIDS 0                       \
    /input /output

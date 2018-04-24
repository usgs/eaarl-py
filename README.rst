eaarl-py
===============================

This library provides a starting place for exploring EAARL data in Python. It
allows you to access EAARL waveform data and provides a simplified basic
processing workflow that you can adapt to experiment with the data.

The library is not intended to provide a production-ready, full-featured
processing workflow. The included algorithms are capable of generating an
approximate first return point cloud by calculating the centroid of the early
portion of a waveform. This is suitable for exploring the data and serves as a
basis from which you might develop your own waveform analysis algorithms.

Users of this library should be familiar with the contents of USGS Open-File
Report 2016-1046: `Algorithms used in the Airborne Lidar Processing System
(ALPS)`_. Production processing of EAARL data was performed using ALPS, which
primarily uses the Yorick_ programming language.

The EAARL sensors were operational between 2001 and 2014. This library is part
of a final effort to make EAARL data acquisitions more accessible to the
public. The USGS has no plans for further development or support of EAARL or of
its associated software (including this library).


Features
--------

- Access to full waveform data for EAARL missions
- Access to related mission data (trajectories, configuration) for EAARL missions
- Approximate first surface detection using centroid waveform analysis
- Projection of detected surfaces in waveforms into real-world x,y,z points
- Random Consensus Filter (RCF) to reduce presence of outlier points in a point cloud


Requirements
------------

The library is compatible with Python 2.7 and Python 3.5. The following
third-party libraries are required:

- `future <https://pypi.python.org/pypi/future>`_
- `NumPy <http://www.numpy.org>`_
- `pandas <https://pandas.pydata.org>`_
- `PyTables <http://www.pytables.org>`_
- `SciPy <https://www.scipy.org>`_
- `utm <https://pypi.python.org/pypi/utm>`_

The following third-party libraries are optional but recommended:

- `Shapely <https://github.com/Toblerity/Shapely>`_; only required if you want
  to use :meth:`eaarl.io.flight.Flight.wfs_by_region` or
  to use :meth:`eaarl.io.flight.Flight.times_by_region`.
- `tqdm <https://getihub.com/tqdm/tqdm>`_; if installed, a progress bar will be
  displayed when loading rasters; this is purely cosmetic.


Installation
------------

To install the library, navigate to the root directory of the source code where
the file `setup.py` is located. Then run the install command::

    $ python setup.py install

For more information regarding installing third-party Python modules, please
see `Installing Python Modules`_ For a description of how installation works
including where the module will be installed on your computer platform, please
see `How Installation Works`_.


Documentation
-------------

HTML documentation can be generated using Sphinx_. Navigate into the docs
subdirectory and run this command::

    $ make html

The documentation will be generated under docs/_build/html.


Tests
-----

The library comes with a test suite that can be run using this command::

    $ python setup.py test


License
-------

This software is licensed under `CC0 1.0`_ and is in the `public domain`_
because it contains materials that originally came from the `U.S. Geological
Survey (USGS)`_, an agency of the `United States Department of Interior`_. For
more information, see the `official USGS copyright policy`_.

.. image:: http://i.creativecommons.org/p/zero/1.0/88x31.png
    :target: http://creativecommons.org/publicdomain/zero/1.0/
    :alt: Creative Commons logo


Disclaimer
----------

This software is preliminary or provisional and is subject to revision. It is
being provided to meet the need for timely best science. The software has not
received final approval by the U.S. Geological Survey (USGS). No warranty,
expressed or implied, is made by the USGS or the U.S. Government as to the
functionality of the software and related material nor shall the fact of
release constitute any such warranty. The software is provided on the condition
that neither the USGS nor the U.S. Government shall be held liable for any
damages resulting from the authorized or unauthorized use of the software.

The USGS provides no warranty, expressed or implied, as to the correctness of
the furnished software or the suitability for any purpose. The software has
been tested, but as with any complex software, there could be undetected
errors. Users who find errors are requested to report them to the USGS.

References to non-USGS products, trade names, and (or) services are provided
for information purposes only and do not constitute endorsement or warranty,
express or implied, by the USGS, U.S. Department of Interior, or U.S.
Government, as to their suitability, content, usefulness, functioning,
completeness, or accuracy.

Although this program has been used by the USGS, no warranty, expressed or
implied, is made by the USGS or the United States Government as to the accuracy
and functioning of the program and related program material nor shall the fact
of distribution constitute any such warranty, and no responsibility is assumed
by the USGS in connection therewith.

This software is provided "AS IS."


.. _Python: https://www.python.org/
.. _Yorick: https://dhmunro.github.io/yorick/
.. _pytest: http://pytest.org/latest/
.. _Sphinx: http://sphinx-doc.org/
.. _public domain: https://en.wikipedia.org/wiki/Public_domain
.. _CC0 1.0: http://creativecommons.org/publicdomain/zero/1.0/
.. _U.S. Geological Survey: https://www.usgs.gov/
.. _USGS: https://www.usgs.gov/
.. _U.S. Geological Survey (USGS): https://www.usgs.gov/
.. _United States Department of Interior: https://www.doi.gov/
.. _official USGS copyright policy: http://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits
.. _Python's download page: https://www.python.org/downloads/
.. _Installing Python Modules: https://docs.python.org/3.5/install/
.. _How Installation Works: https://docs.python.org/3.5/install/#how-installation-works
.. _Algorithms used in the Airborne Lidar Processing System (ALPS): https://pubs.er.usgs.gov/publication/ofr20161046

Working with flights
====================

This page provides an introduction to working with flights. A flight object
correlates the various raw data sources, which allows you to retrieve waveform
data that has associated spatial information from the trajectories.

Creating a flight
-----------------

The first step to working with an EAARL dataset is to create a flight object
that defines the four component data sources needed:

* An operational configuration file, or "ops" for short. This file provides
  measurements and calibration values necessary for using the other data
  sources together to derive a projected real-world point location.
* A trajectory containing inertial measurements from an inertial navigation
  system, or "ins" for short. This file actually contains both positional data
  and inertial measurements, both of which are provided at a higher frequency
  than the gps trajectory.
* A trajectory containing positional measurements from a GPS, or "gps" for
  short. The positional data in the gps trajectory is provided at a lower
  frequency than the ins trajectory, which makes it faster to work with when
  the additional precision is not needed.
* An EAARL index/database file, or "edb" for short. The index allows
  random-access retrieval of records from the associated EAARL TLD files, which
  contain the waveform data.

When loading the data sources, you must always load the ops file first because
some of the other files depend on values from it during their load processes.

During creation, the flight's date must also be provided. If a flight crosses GPS midnight, then use the date the flight started. The date is used for two purposes:

* The time offset between UTC and GPS time must be applied, and it varies based
  on date.
* The gps trajectory uses "seconds of the day" timestamps and the ins
  trajectory uses "seconds of the week" timestamps. The date is used to convert
  them into "seconds of the epoch".

The flight object is defined in eaarl.io.flight. Assuming you have a flight's
data in /data/2014-01-31, you can create a flight object for it like so::

    import eaarl.io.flight

    # Create a flight object, specifying the date during creation
    flight = eaarl.io.flight.Flight('2014-01-31')

    # Load the ops file first
    flight.load_ops('/data/2014-01-31/py/ops/20140131.ops.json')

    # Then load the ins, gps, and edb files
    flight.load_ins('/data/2014-01-31/py/ins/2014-01-31-cmb-ins.csv')
    flight.load_gps('/data/2014-01-31/py/gps/2014-01-31-cmb-pnav.csv')
    flight.load_edb('/data/2014-01-31/eaarl/2014-01-31.idx')

Once you have flight defined, you can write out a configuration file that lets
you load it back up in a later session::

    flight.save('/data/2014-01-31/flight.json')

The configuration file is a simple JSON file that lists the files that were
loaded. It does not actually save the associated data, and any changes you
might make to the data in memory after loading will not be reflected by it.

You can later load the flight from the configuration file like so::

    import eaarl.io.flight
    flight = eaarl.io.flight.load('/data/2014-01-31/flight.json')

Properties of a flight
----------------------

Once you have a flight, you can inspect the component data sources as
properties on the object.

The data from the ops file is loaded as a dict to flight.ops::

    >>> flight.ops
    {'chn1_range_bias': -13.25, 'chn4_dx': -0.117, 'dmars_invert': 0, 'chn3_range_bias': -10.564, 'type': 'EAARL-B', 'scan_bias': -40.5, 'z_offset': -0.02, '_timestamp': '2016-09-28 22:51:14', 'chn1_dx': -0.117, 'max_sfc_sat': 2, 'delta_ht': 300, 'roll_bias': 0, 'x_offset': -0.03099, 'chn1_dy': -1.6, 'use_ins_for_gps': 1, 'chn4_dy': 0, 'chn3_dy': 1.6, 'tx_clean': 8, 'chn4_range_bias': -19.875, 'chn2_dx': 0, 'minsamples': 0, 'yaw_bias': 0, 'chn3_dx': -0.117, 'pitch_bias': 0.325, 'range_biasM': 0, 'y_offset': 0.02426, 'chn2_dy': 0, 'chn2_range_bias': -12.375}

The data from the ins trajectory is loaded as a pandas dataframe to flight.ins::

    >>> flight.ins
                lon        lat        alt        sod      roll     pitch  \
    0       -94.022656  29.956418 -22.730499  56217.025  0.950894  2.281592   
    1       -94.022656  29.956418 -22.730499  56217.030  0.951364  2.281570   
    2       -94.022656  29.956418 -22.730499  56217.035  0.951429  2.281585   
    ...            ...        ...        ...        ...       ...       ...   
    2174792 -89.084658  30.416997  28.854300  67090.985  2.921807 -9.047781   
    2174793 -89.084657  30.416995  28.820299  67090.990  2.914392 -9.052345   
    2174794 -89.084655  30.416994  28.786200  67090.995  2.907984 -9.056522   

                heading  
    0        256.070349  
    1        256.070376  
    2        256.070431  
    ...             ...  
    2174792  134.038132  
    2174793  134.044320  
    2174794  134.050905  

    [2174795 rows x 7 columns]

The data from the gps trajectory is loaded as a pandas dataframe to flight.gps::

    >>> flight.gps
                lon        lat         alt      sod  pdop   xrms      veast  \
    0     -94.022667  29.956417  -21.821400  56200.0   1.5  0.007  -0.000000   
    1     -94.022667  29.956417  -21.821400  56200.5   1.5  0.007   0.000000   
    2     -94.022667  29.956417  -21.821400  56201.0   1.5  0.007   0.000000   
    ...          ...        ...         ...      ...   ...    ...        ...   
    21752 -89.084267  30.416649   22.647200  67076.0   1.9  0.101  36.087002   
    21753 -89.084076  30.416483   19.571899  67076.5   1.8  0.101  36.092999   
    21754 -89.084076  30.416483   19.571899  67076.5   1.8  0.101  36.092999   

            vnorth    vup  sv  flag  
    0      -0.000000 -0.000   9     2  
    1       0.000000  0.000   9     2  
    2       0.000000  0.000   9     2  
    ...          ...    ...  ..   ...  
    21752 -36.757000 -6.313   8     2  
    21753 -36.685001 -5.938   8     2  
    21754 -36.685001 -5.938   8     2  

    [21755 rows x 11 columns]

The data from the edb file is loaded as an
eaarl.io.waveforms.collection.EaarlCollection object::

    >>> flight.edb
    <eaarl.io.waveforms.collection.EaarlCollection object at 0x7fe11b20d710>

You can interact with flight.edb to retrieve raster records directly if you
wish. However, the flight object contains methods that will automatically add
associated trajectory data to the raster records for you. It is recommended
that you start with the methods available via the flight object, and you can
consult the documentation of EaarlCollection to learn about working with it
directly.

Methods of a flight
-------------------

The flight object contains methods for retrieving pulse data in there different
ways: by raster number, by time, and by region. In all three cases, the data is
returned as a pandas dataframe that contains a record for each channel of each
pulse of each raster of the request. Since it may take a while to load larger
amounts of data, a progress bar is displayed during the load process.

wfs_by_raster
^^^^^^^^^^^^^

The simplest approach is to retrieve data based on raster number via
wfs_by_raster. The method is flexible and supports several different sets of
arguments.

To request a single raster, simply give its raster number as an argument. This
retrieves raster 12803::

    >>> frame = flight.wfs_by_raster(12803)
    Loading rasters: 100%|████████████████| 1/1 [00:00<00:00, 17.02raster/s]

To request a set of arbitrary rasters, provide them as a list of raster
numbers. This retrieves three rasters (12803, 24295, and 54187)::

    >>> frame = flight.wfs_by_raster([12803, 24295, 54187])
    Loading rasters: 100%|████████████████| 3/3 [00:00<00:00, 13.24raster/s]

To request a sequential range of rasters, you can specify the starting raster
number with *start* and the number of rasters with *count*. This requests the
data for ten rasters starting from raster 12803::

    >>> frame = flight.wfs_by_raster(start=12803, count=10)
    Loading rasters: 100%|██████████████| 10/10 [00:00<00:00, 35.89raster/s]

You can also request multiple sequential ranges at the same time by using the
*ranges* option, which accepts a list of tuples where each tuple is a (*start*,
*count*) pair as would be provided in the previous example. This requests data
for ten rasters starting from raster 13803 and five rasters starting from
24295::

    >>> frame = flight.wfs_by_raster(ranges=[(12803, 10), (24295, 5)])
    Loading rasters: 100%|██████████████| 15/15 [00:00<00:00, 40.32raster/s]

wfs_by_time
^^^^^^^^^^^

Similarly, you can retrieve data based on seconds-of-the-epoch time using
wfs_by_time.

Use *start* and *stop* to request rasters that fall within a specified time
period. This requests rasters with a timestamp between 1391188200 and
1391188210::

    >>> frame = flight.wfs_by_time(start=1391188200, stop=1391188210)
    Loading rasters: 100%|████████████| 202/202 [00:05<00:00, 37.84raster/s]

You can also request multiple time periods using *ranges*, which accepts a list
of tuples where each tuple is (*start*, *stop*). This requests data for rasters
between times 1391188200 and 1391188201 as well as rasters between times
1391188207 and 1391188208::

    >>> frame = flight.wfs_by_time(ranges=[(1391188200, 1391188201),
    ...                                    (1391188207, 1391188208)])
    Loading rasters: 100%|██████████████| 41/41 [00:01<00:00, 32.57raster/s]

wfs_by_region
^^^^^^^^^^^^^

If you have the shapely library installed, you can also retrieve data based on
a spatial region. Your spatial region should use WGS-84 geographic coordinates.
Any bounded shapely geometry type is permitted.

Data will be retrieved for all rasters where the plane's location was inside
the region during data collection. This does not correspond perfectly to the
area of data coverage itself, since the lidar coverage extends to the left and
right of the plane. It may be helpful to expand your region by a few hundred
meters.

This requests data where the plane was located between 89.20 W and 89.19 W
longitude and between 29.47 N and 29.48 N latitude::

    >>> import shapely.geometry
    >>> region = shapely.geometry.box(-89.195, -89.194, 29.473, 29.474)
    >>> frame = flight.wfs_by_region(region)
    Loading rasters: 100%|██████████| 1460/1460 [00:53<00:00, 27.13raster/s]


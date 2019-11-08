#!/usr/bin/env python

# OK get data from some random dataset?

# aws s3 --recursive cp s3://noaa-nexrad-level2/2010/01/01/KDIX .
#
# https://carto.com/blog/mapping-nexrad-radar-data/
#
"""
apt install proj-bin libgdal20 libgeos-dev 
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
  libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
  xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
pip install ipython cartopy siphon metpy ipykernel pylzma
"""
# https://nbviewer.jupyter.org/gist/dopplershift/356f2e14832e9b676207

# Where it says
# from metpy.plots.ctables as ctables  # For NWS colortable
# ref_norm, ref_cmap = ctables.registry.get_with_steps('NWSReflectivity', 5, 5)

# Using the nextradaws pyenv

import matplotlib
import warnings
from datetime import datetime, timedelta


from siphon.radarserver import RadarServer
from siphon.cdmr import Dataset

import numpy as np

from metpy.plots import ctables  # For NWS colortable

import matplotlib.pyplot as plt
import cartopy


rs = RadarServer('http://thredds-aws.unidata.ucar.edu/thredds/radarServer/nexrad/level2/S3/')
warnings.filterwarnings("ignore", category=matplotlib.cbook.MatplotlibDeprecationWarning)
query = rs.query()
query.stations('KLVX').time(datetime.utcnow())

rs.validate_query(query)

catalog = rs.get_catalog(query)

# We can pull that dataset out of the dictionary and look at the available access URLs. We see URLs for OPeNDAP, CDMRemote, and HTTPServer (direct download).

ds = list(catalog.datasets.values())[0]
# ds.access_urls will be something like
# 
# {'CdmRemote': 'http://thredds-aws.unidata.ucar.edu/thredds/cdmremote/nexrad/level2/S3/2015/10/27/KLVX/KLVX20151027_231326_V06.gz',
#  'HTTPServer': 'http://thredds-aws.unidata.ucar.edu/thredds/fileServer/nexrad/level2/S3/2015/10/27/KLVX/KLVX20151027_231326_V06.gz',
#  'OPENDAP': 'http://thredds-aws.unidata.ucar.edu/thredds/dodsC/nexrad/level2/S3/2015/10/27/KLVX/KLVX20151027_231326_V06.gz'}

data = Dataset(ds.access_urls['CdmRemote'])

def raw_to_masked_float(var, data):
    # Values come back signed. If the _Unsigned attribute is set, we need to convert
    # from the range [-127, 128] to [0, 255].
    if var._Unsigned:
        data = data & 255

    # Mask missing points
    data = np.ma.array(data, mask=data==0)

    # Convert to float using the scale and offset
    return data * var.scale_factor + var.add_offset

def polar_to_cartesian(az, rng):
    az_rad = np.deg2rad(az)[:, None]
    x = rng * np.sin(az_rad)
    y = rng * np.cos(az_rad)
    return x, y

# The CDMRemote reader provides an interface that is almost identical
# to the usual python NetCDF interface. We pull out the variables we
# need for azimuth and range, as well as the data itself.

sweep = 0
ref_var = data.variables['Reflectivity_HI']
ref_data = ref_var[sweep]
rng = data.variables['distanceR_HI'][:]
az = data.variables['azimuthR_HI'][sweep]

# Then convert the raw data to floating point values and the polar coordinates to Cartesian.

ref = raw_to_masked_float(ref_var, ref_data)
x, y = polar_to_cartesian(az, rng)

# MetPy is a Python package for meteorology (Documentation:
# http://metpy.readthedocs.org and GitHub:
# http://github.com/MetPy/MetPy). We import MetPy and use it to get
# the colortable and value mapping information for the NWS
# Reflectivity data.

ref_norm, ref_cmap = ctables.registry.get_with_steps('NWSReflectivity', 5, 5)


# This time we'll make a query based on a longitude, latitude point and using a time range.

query = rs.query()
dt = datetime(2012, 10, 29, 15) # Our specified time
query.lonlat_point(-73.687, 41.175).time_range(dt, dt + timedelta(hours=1))

# time_start=2012-10-29T15%3A00%3A00&time_end=2012-10-29T16%3A00%3A00&latitude=41.175&longitude=-73.687

# The specified longitude, latitude are in NY and the TDS helpfully finds the closest station to that point. The time range we request is an hour of data form 29 October 2012; we're looking for data from Hurricane Sandy. We can see that this time we obtained multiple datasets.

cat = rs.get_catalog(query)
print(cat.datasets)

# {'KOKX20121029_150259_V06.gz': <siphon.catalog.Dataset at 0x106e8e588>,
#  'KOKX20121029_150854_V06.gz': <siphon.catalog.Dataset at 0x106e8e4a8>,
#  'KOKX20121029_151451_V06.gz': <siphon.catalog.Dataset at 0x106e8e5c0>,
#  'KOKX20121029_152046_V06.gz': <siphon.catalog.Dataset at 0x106e8e630>,
#  'KOKX20121029_152639_V06.gz': <siphon.catalog.Dataset at 0x106e8e668>,
#  'KOKX20121029_153234_V06.gz': <siphon.catalog.Dataset at 0x106e8e6a0>,
#  'KOKX20121029_153829_V06.gz': <siphon.catalog.Dataset at 0x106e8e6d8>,
#  'KOKX20121029_154422_V06.gz': <siphon.catalog.Dataset at 0x106e8e710>,
#  'KOKX20121029_155017_V06.gz': <siphon.catalog.Dataset at 0x106e8e748>,
#  'KOKX20121029_155612_V06.gz': <siphon.catalog.Dataset at 0x106e8e780>}

# Grab the first dataset so that we can get the longitude and latitude of the station and make a map for plotting. We'll go ahead and specify some longitude and latitude bounds for the map.

ds = list(cat.datasets.values())[0]
data = Dataset(ds.access_urls['CdmRemote'])


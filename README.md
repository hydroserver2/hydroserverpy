# hydroserverpy

The hydroserverpy Python package provides an interface for interacting with HydroServer's Data Management API. This guide will go over how to install the package and connect to a HydroServer instance to retrieve, upload, and modify data.

## Installation

You can install the package via pip:

```bash
pip install hydroserverpy
```

## Getting Started

### Connecting to HydroServer

To connect to HydroServer, you need to initialize the client with the instance of HydroServer you're using and your user credentials if you want to access and modify your own data. If you don't provide authentication credentials you can read public data, but you will not be able to create or modify any data.

#### Example: Anonymous User

```python
from hydroserverpy import HydroServer

# Initialize HydroServer connection.
hs_api = HydroServer(
    host='https://playground.hydroserver.org'
)
```

#### Example: Basic Authentication

```python
from hydroserverpy import HydroServer

# Initialize HydroServer connection with credentials.
hs_api = HydroServer(
    host='https://playground.hydroserver.org',
    username='user@example.com',
    password='******'
)
```

### Retrieving Data

The hydroserverpy connection exposes the following types of data and metadata you can retireve, either as a list or by ID using the `list` or `get` methods of the associated property:

* things
* datastreams
* dataloaders
* datasources
* sensors
* units
* processinglevels
* observedproperties
* resultqualifiers

Dataframes of Observations can be queried using the `get_observations` method of a datastream object.

#### Example: Get Things
```python
things = hs_api.things.list()
```

#### Example: Get Thing by ID
```python
thing = hs_api.things.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Get Observations of a Datastream
```python
from datetime import datetime

...

datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')
observations_df = datastream.get_observations(
    start_time=datetime(year=2023, month=1, day=1),
    end_time=datetime(year=2023, month=12, day=31)
)
```

### Creating and Modifying Data

HydroServer things, datastreams, and other metadata can be created using the `create` method of the respective property of the connection object. To modify HydroServer metadata, you can update one or more properties of a fetched metadata object and then use the `save` method to save those changes back to HydroServer. Observations can be uploaded from a DataFrame using the `upload_observations` method of `datastreams`.

#### Example: Create a Thing

```python
new_thing = hs_api.things.create(
    name='My Observation Site',
    description='This is a site that records environmental observations.'
    sampling_feature_type='Site',
    sampling_feature_code='OBSERVATION_SITE',
    site_type='Atmosphere',
    latitude='41.739',
    longitude='-111.794'
)
```

#### Example: Modify a Thing

```python
thing = hs_api.things.get(uid='00000000-0000-0000-0000-000000000000')
thing.name = 'Updated Site Name'
thing.description = 'Updated Site Description.'
thing.save()
```

#### Example: Upload Observations

```python
import pandas as pd

...

datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')
new_observations = pd.DataFrame(
    [
        ['2023-01-26 00:00:00+00:00', 40.0],
        ['2023-01-27 00:00:00+00:00', 41.0],
        ['2023-01-28 00:00:00+00:00', 42.0],
    ],
    columns=['timestamp', 'value']
)
new_observations['timestamp'] = pd.to_datetime(new_observations['timestamp'])
datastream.upload_observations(new_observations)
```


## Funding and Acknowledgements

Funding for this project was provided by the National Oceanic & Atmospheric Administration (NOAA), awarded to the Cooperative Institute for Research to Operations in Hydrology (CIROH) through the NOAA Cooperative Agreement with The University of Alabama (NA22NWS4320003).

# HydroServer Python Client - Data Loader

They hydroserverpy package supports several methods for loading data into HydroServer. This guide will provide examples on how to prepare and load data into HydroServer using each of these methods.

## Data Loader Guide with Examples

To perform data loading operations, you must connect to HydroServer.

```python
from hydroserverpy import HydroServer

# Initialize HydroServer connection with credentials.
hs_api = HydroServer(
    host='https://playground.hydroserver.org',
    username='user@example.com',
    password='******'
)
```

After setting up all necessary metadata associated with the datastreams you want to load data into, the following properties of the HydroServer connection object will be used to set up data loading:

* dataloaders
* datasources
* datastreams

### Data Loaders

HydroServer data loaders are generally used in conjunction with the Streaming Data Loader, and will be automatically registered after installing an instance of the Streaming Data Loader application. If you are not using the Streaming Data Loader, this endpoint should be used to register the name of the script or process you're using to load data. The examples below demonstrate the actions you can take to manage data loaders in HydroServer.

#### Example: Get Data Loaders
```python
# Get all owned Data Loaders
data_loaders = hs_api.dataloaders.list()

# Get Data Loader with a given ID
data_loader = hs_api.dataloaders.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Create Data Loader
```python
# Create a new Data Loader in HydroServer
new_data_loader = hs_api.dataloaders.create(
    name='My Data Loader',
)
```

#### Example: Modify a Data Loader
```python
# Get a Data Loader
data_loader = hs_api.dataloaders.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the Data Loader.
data_loader.name = 'Updated Data Loader Name'

# Save the changes back to HydroServer.
data_loader.save()
```

#### Example: Get Data Sources of a Data Loader
```python
# Get a Data Loaders
data_loader = hs_api.dataloaders.get(uid='00000000-0000-0000-0000-000000000000')

# Fetch Data Sources of the Data Loader
data_sources = data_loader.data_sources
```

#### Example: Refresh Data Loader details from HydroServer
```python
# Get a Data Loader
data_loader = hs_api.dataloaders.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh Data Loader data from HydroServer
data_loader.refresh()
```

#### Example: Delete Data Loader from HydroServer
```python
# Get a Data Loader
data_loader = hs_api.dataloaders.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the Data Loader from HydroServer
data_loader.delete()
```

### Data Sources

HydroServer data sources represent a data file where observations for one or more datastreams are stored before being loaded into HydroServer. The examples below demonstrate the actions you can take to manage data sources in HydroServer.

#### Example: Get Data Sources
```python
# Get all owned Data Sources
data_sources = hs_api.datasources.list()

# Get Data Source with a given ID
data_source = hs_api.datasources.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Create Data Source
```python
# Create a new Data Source in HydroServer
new_data_source = hs_api.datasources.create(
    name='My Data Source',
    path='/path/to/my/local/data/file.csv',
    header_row=1,
    data_start_row=2,
    delimiter=',',
    quote_char='"',
    interval='1',
    interval_units='days',
    timestamp_column='timestampColumnName',
    timestamp_format='%Y-%m-%dT%H:%M:%S%Z',
    timestamp_offset='+0000',
    paused=False,
    data_loader_id='00000000-0000-0000-0000-000000000000'
)
```

#### Example: Modify a Data Source
```python
# Get a Data Source
data_source = hs_api.datasources.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the Data Source.
data_source.name = 'Updated Data Source Name'

# Save the changes back to HydroServer.
data_source.save()
```

#### Example: Get Datastreams of a Data Source
```python
# Get a Data Source
data_source = hs_api.datasources.get(uid='00000000-0000-0000-0000-000000000000')

# Fetch Datastreams of the Data Source
datastreams = data_source.datastreams
```

#### Example: Refresh Data Source details from HydroServer
```python
# Get a Data Source
data_source = hs_api.datasources.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh Data Source data from HydroServer
data_source.refresh()
```

#### Example: Delete Data Source from HydroServer
```python
# Get a Data Source
data_source = hs_api.datasources.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the Data Source from HydroServer
data_source.delete()
```

### Datastreams

In order to load data, data sources must be linked to one or more datastreams. The examples below demonstrate how to link existing datastreams to a data source.

#### Example: Link Datastream to a Data Source
```python
# Get a Data Source
data_source = hs_api.datasources.get(uid='00000000-0000-0000-0000-000000000000')

# Get a Datastream
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')

# Update the data_source_id and data_source_column properties of the Datastream
# The data_source_column value should match the appropriate column name/index of the column in your data source file
datastream.data_source_id = data_source.uid
datastream.data_source_column = 'dataColumnName'

# Save the changes back to HydroServer.
datastream.save()
```

### Loading Data

Once you have datastreams and data sources set up in HydroServer, you can begin loading observations data into them. The examples below demonstrate several methods you can use to load data into HydroServer.

#### Example: Load Data from a DataFrame
```python
import pandas as pd

...

# Get a Datastream
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')

# Create a DataFrame of Observations
new_observations = pd.DataFrame(
    [
        ['2023-01-26 00:00:00+00:00', 40.0],
        ['2023-01-27 00:00:00+00:00', 41.0],
        ['2023-01-28 00:00:00+00:00', 42.0],
    ],
    columns=['timestamp', 'value']
)
new_observations['timestamp'] = pd.to_datetime(new_observations['timestamp'])

# Upload the Observations to HydroServer
datastream.load_observations(new_observations)
```

#### Example: Load Data from a Data Source File
```python
# Get a Data Source
data_source = hs_api.datasources.get(uid='00000000-0000-0000-0000-000000000000')

# Load new Observations from the Data Source file to HydroServer
data_source.load_observations()
```

#### Example: Load Data from Data Sources of a Data Loader
```python
# Get a Data Loader
data_loader = hs_api.dataloaders.get(uid='00000000-0000-0000-0000-000000000000')

# Load new Observations from all Data Sources associated with the Data Loader to HydroServer
data_loader.load_observations()
```

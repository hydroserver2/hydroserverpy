# Overview of the `hydroserverpy.api` Package

The `hydroserverpy.api` Python package allows HydroServer users to retrieve, create, update, and delete their HydroServer data and metadata. This guide will provide examples on how to manage various types of HydroServer data.

## Data Management Guide with Examples

To perform data management operations, you must connect to HydroServer.

```python
from hydroserverpy import HydroServer

# Initialize HydroServer connection with credentials.
hs_api = HydroServer(
    host='https://playground.hydroserver.org',
    email='user@example.com',
    password='******'
)
```

The hydroserverpy connection instance exposes the following types of core data and metadata you can retrieve or create, either as a collection or by ID using the `list`, `get`, or `create` methods of the associated property:

* workspaces
* things
* datastreams
* sensors
* units
* processinglevels
* observedproperties
* resultqualifiers

### Workspaces

Workspaces in HydroServer are used to organize and manage access to your data. All user-managed resources in HydroServer are created within the context of a workspace. Each workspace has one owner and can have any number of collaborators with varying levels of access to resources within the workspace. The examples below demonstrate how to use hydroserverpy to manage workspaces.

#### Example: Get Workspaces
```python
# Get all visible workspaces
public_workspaces = hs_api.workspaces.list()

# Get all workspaces you are associated with
your_workspaces = hs_api.workspaces.list(associated_only=True)

# Get a workspace by ID
workspace = hs_api.workspaces.get(uid="00000000-0000-0000-0000-000000000000")
```

#### Example: Get Workspace Resources
```python
workspace = hs_api.workspaces.get(uid="00000000-0000-0000-0000-000000000000")

# Get all collaborators for a workspace
workspace_collaborators = workspace.collaborators

# Get all roles that can be assigned for this workspace
workspace_roles = workspace.roles

# Get all things within a workspace
workspace_things = workspace.things

# Get all observed properties within a workspace
workspace_observed_properties = workspace.observedproperties

# Get all units within a workspace
workspace_units = workspace.units

# Get all processing levels within a workspace
workspace_processing_levels = workspace.processinglevels

# Get all sensors within a workspace
workspace_sensors = workspace.sensors
```

#### Example: Create a Workspace
```python
# Create a new workspace in HydroServer
new_workspace = hs_api.workspaces.create(
    name="New Workspace",
    is_private=False
)
```

#### Example: Modify a Workspace
```python
workspace = hs_api.workspaces.get(uid="00000000-0000-0000-0000-000000000000")

# Update the name and privacy settings of a workspace
workspace.name = "New Workspace Name"
workspace.is_private = True
workspace.save()
```

#### Example: Manage Workspace Collaborators and Ownership
```python
workspace = hs_api.workspaces.get(uid="00000000-0000-0000-0000-000000000000")

# Add a collaborator to a workspace
workspace.add_collaborator(
    email="user@example.com",                    # Must be the email of an active HydroServer user.
    role="00000000-0000-0000-0000-000000000000"  # You can use either the UUID of the role, or the role object.
)

# Modify a collaborator's role
workspace.edit_collaborator_role(
    email="user@example.com",
    role="00000000-0000-0000-0000-000000000000"
)

# Remove a collaborator
workspace.remove_collaborator(
    email="user@example.com"
)

# Initiate transfer of workspace ownership to another user
workspace.transfer_ownership(
    email="user@example.com"
)

# Accept pending ownership transfer (Must be accepted by the user receiving the workspace)
workspace.accept_ownership_transfer()

# Cancel pending ownership transfer
workspace.cancel_ownership_transfer()
```

### Things

Things (or sites) are one of the core data elements managed in HydroServer. Things represent a location or site at which one or more datastreams of observations are collected. All datastreams in HydroServer must be associated with a thing/site. The examples below demonstrate how to use hydroserverpy to manage things in HydroServer.

#### Example: Get Things
```python
# Get all visible things
public_things = hs_api.things.list()

# Get things belonging to a workspace
workspace_things = hs_api.things.list(workspace="00000000-0000-0000-0000-000000000000")

# Get thing with a given ID
thing = hs_api.things.get(uid="00000000-0000-0000-0000-000000000000")
```

#### Example: Create Thing
```python
# Create a new thing in HydroServer
new_thing = hs_api.things.create(
    name="My Site",
    description="This is a site that records environmental observations.",
    sampling_feature_type="Site",
    sampling_feature_code="OBSERVATION_SITE",
    site_type="Atmosphere",
    latitude=41.7390,
    longitude=-111.7957,
    elevation_m=1414.0,
    elevation_datum="EGM96",
    state="UT",
    county="Cache",
    country="US",
    data_disclaimer="WARNING: These data may be provisional and subject to revision.",
    workspace="00000000-0000-0000-0000-000000000000"
)
```

Each of the methods above will return one or more Thing objects. The examples below show the main properties and methods available to a Thing object.

#### Example: Modify a Thing
```python
# Get a thing
thing = hs_api.things.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the thing.
thing.name = 'Updated Site Name'
thing.description = 'This site metadata has been modified.'

# Save the changes back to HydroServer.
thing.save()
```

#### Example: Manage Thing Tags
```python
# Get a thing
thing = hs_api.things.get(uid='00000000-0000-0000-0000-000000000000')

# Get thing tags
tags = thing.tags

# Add a tag to a thing
thing.add_tag(
    key='Region',
    value='A'
)

# Modify a thing's tag
thing.update_tag(
    key='Region',
    value='B'
)

# Delete a thing's tag
thing.delete_tag(key='Region')
```

#### Example: Manage Thing Photos
```python
# Get a thing
thing = hs_api.things.get(uid='00000000-0000-0000-0000-000000000000')

# Get thing photos
photos = thing.photos

# Add a photo to a thing
with open('/path/to/my/photo.png', 'rb') as photo_file:
    thing.add_photo(file=photo_file)

# Delete a thing's photo
thing.delete_photo(name='photo.png')
```

#### Example: Get Datastreams of a Thing
```python
# Get a thing
thing = hs_api.things.get(uid='00000000-0000-0000-0000-000000000000')

# Fetch datastreams of the thing
datastreams = thing.datastreams
```

#### Example: Refresh Thing data from HydroServer
```python
# Get a Thing
thing = hs_api.things.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh thing data from HydroServer
thing.refresh()
```

#### Example: Delete Thing from HydroServer
```python
# Get a Thing
thing = hs_api.things.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the thing from HydroServer
thing.delete()
```

### Observed Properties

Observed properties are used in HydroServer to represent the physical property being observed and stored in a datastream. The examples below demonstrate the actions you can take to manage observed properties in HydroServer.

#### Example: Get Observed Properties
```python
# Get all observed properties
observed_properties = hs_api.observedproperties.list()

# Get observed properties belonging to a workspace
workspace_observed_properties = hs_api.things.list(workspace="00000000-0000-0000-0000-000000000000")

# Get observed property with a given ID
observed_property = hs_api.observedproperty.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Create Observed Property
```python
# Create a new observed property in HydroServer
new_observed_property = hs_api.observedproperties.create(
    name='Temperature',
    definition='Air Temperature',
    description='Air temperature',
    observed_property_type='Climate',
    code='AirTemp',
    workspace='00000000-0000-0000-0000-000000000000'
)
```

Each of the methods above will return one or more ObservedProperty objects. The examples below show the main properties and methods available to an ObservedProperty object.

#### Example: Modify an Observed Property
```python
# Get an observed property
observed_property = hs_api.observedproperties.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the Observed Property.
observed_property.name = 'Updated Observed Property Name'

# Save the changes back to HydroServer.
observed_property.save()
```

#### Example: Refresh Observed Property data from HydroServer
```python
# Get an observed property
observed_property = hs_api.observedproperties.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh observed property data from HydroServer
observed_property.refresh()
```

#### Example: Delete Observed Property from HydroServer
```python
# Get an observed property
observed_property = hs_api.observedproperties.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the observed property from HydroServer
observed_property.delete()
```

### Units

Units are used in HydroServer to describe the physical quantity represented by the result of an observation in a datastream. The examples below demonstrate the actions you can take to manage units in HydroServer.

#### Example: Get Units
```python
# Get all units
units = hs_api.units.list()

# Get units belonging to a workspace
workspace_units = hs_api.units.list(workspace="00000000-0000-0000-0000-000000000000")

# Get unit with a given ID
unit = hs_api.units.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Create Unit
```python
# Create a new unit in HydroServer
new_unit = hs_api.units.create(
    name='Degree Celsius',
    symbol='C',
    definition='Degree Celsius',
    unit_type='Temperature',
    workspace='00000000-0000-0000-0000-000000000000'
)
```

Each of the methods above will return one or more Unit objects. The examples below show the main properties and methods available to a Unit object.

#### Example: Modify a Unit
```python
# Get a Unit
unit = hs_api.units.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the Unit.
unit.name = 'Updated Unit Name'

# Save the changes back to HydroServer.
unit.save()
```

#### Example: Refresh Unit data from HydroServer
```python
# Get a Unit
unit = hs_api.units.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh Unit data from HydroServer
unit.refresh()
```

#### Example: Delete Unit from HydroServer
```python
# Get a Unit
unit = hs_api.units.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the Unit from HydroServer
unit.delete()
```

### Sensors

Sensors are used in HydroServer to describe the sensor/method used to make an environmental observation. The examples below demonstrate the actions you can take to manage sensors in HydroServer.

#### Example: Get Sensors
```python
# Get all sensors
sensors = hs_api.sensors.list()

# Get sensors belonging to a workspace
workspace_sensors = hs_api.sensors.list(workspace="00000000-0000-0000-0000-000000000000")

# Get sensor with a given ID
sensor = hs_api.sensors.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Create Sensor
```python
# Create a new sensor in HydroServer
new_sensor = hs_api.sensors.create(
    name='Environmental Sensor',
    description='An environmental sensor.',
    encoding_type='application/json',
    manufacturer='Campbell Scientific',
    sensor_model='A',
    sensor_model_link='https://link/to/sensor/model/info',
    method_type='Sensor',
    method_link='https://link/to/method/info',
    method_code='SENSOR_A',
    workspace='00000000-0000-0000-0000-000000000000'
)
```

Each of the methods above will return one or more sensor objects. The examples below show the main properties and methods available to a sensor object.

#### Example: Modify a Sensor
```python
# Get a sensor
sensor = hs_api.sensors.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the Sensor.
sensor.name = 'Updated Sensor Name'

# Save the changes back to HydroServer.
sensor.save()
```

#### Example: Refresh Sensor data from HydroServer
```python
# Get a sensor
sensor = hs_api.sensors.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh sensor data from HydroServer
sensor.refresh()
```

#### Example: Delete Sensor from HydroServer
```python
# Get a sensor
sensor = hs_api.sensors.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the sensor from HydroServer
sensor.delete()
```

### Processing Levels

Processing levels are used in HydroServer to describe the level of processing observations of a datastream have been subject to. The examples below demonstrate the actions you can take to manage processing levels in HydroServer.

#### Example: Get Processing Levels
```python
# Get all processing levels
processing_levels = hs_api.processinglevels.list()

# Get processing levels belonging to a workspace
workspace_processing_levels = hs_api.processinglevels.list(workspace="00000000-0000-0000-0000-000000000000")

# Get processing level with a given ID
processing_level = hs_api.processinglevels.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Create Processing Level
```python
# Create a new processing level in HydroServer
new_processing_level = hs_api.processinglevels.create(
    code='0',
    definition='Raw',
    explanation='Data have not been processed or quality controlled.',
    workspace='00000000-0000-0000-0000-000000000000'
)
```

Each of the methods above will return one or more processing level objects. The examples below show the main properties and methods available to a processing level object.

#### Example: Modify a Processing Level
```python
# Get a processing level
processing_level = hs_api.processinglevels.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the processing level.
processing_level.code = 'Updated Processing Level Code'

# Save the changes back to HydroServer.
processing_level.save()
```

#### Example: Refresh Processing Level data from HydroServer
```python
# Get a processing level
processing_level = hs_api.processinglevels.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh processing level data from HydroServer
processing_level.refresh()
```

#### Example: Delete Processing Level from HydroServer
```python
# Get a processing level
processing_level = hs_api.processinglevels.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the processing level from HydroServer
processing_level.delete()
```

### Result Qualifiers

Result qualifiers are used in HydroServer to annotate observations during quality control or other processing steps. The examples below demonstrate the actions you can take to manage result qualifiers in HydroServer.

#### Example: Get Result Qualifiers
```python
# Get all result qualifiers
result_qualifiers = hs_api.resultqualifiers.list()

# Get result qualifiers belonging to a workspace
workspace_result_qualifiers = hs_api.resultqualifiers.list(workspace="00000000-0000-0000-0000-000000000000")

# Get result qualifier with a given ID
result_qualifier = hs_api.resultqualifiers.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Create Result Qualifier
```python
# Create a new result qualifier on HydroServer
new_result_qualifier = hs_api.resultqualifiers.create(
    code='PF',
    description='Power Failure',
    workspace='00000000-0000-0000-0000-000000000000'
)
```

Each of the methods above will return one or more ResultQualifier objects. The examples below show the main properties and methods available to a ResultQualifier object.

#### Example: Modify a Result Qualifier
```python
# Get a result qualifier
result_qualifier = hs_api.resultqualifiers.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the result qualifier.
result_qualifier.code = 'Updated Result Qualifier Code'

# Save the changes back to HydroServer.
result_qualifier.save()
```

#### Example: Refresh Result Qualifier data from HydroServer
```python
# Get a result qualifier
result_qualifier = hs_api.resultqualifiers.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh result qualifier data from HydroServer
result_qualifier.refresh()
```

#### Example: Delete Result Qualifier from HydroServer
```python
# Get a result qualifier
result_qualifier = hs_api.resultqualifiers.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the result qualifier from HydroServer
result_qualifier.delete()
```

### Datastreams

Datastreams are used in HydroServer to represent a group of environmental observations of an observed property made by a sensor at a location and having a specific processing level. The examples below demonstrate the actions you can take to manage datastreams in HydroServer.

#### Example: Get Datastreams
```python
# Get all datastreams
datastreams = hs_api.datastreams.list()

# Get processing levels belonging to a workspace
workspace_datastreams = hs_api.processinglevels.list(workspace="00000000-0000-0000-0000-000000000000")

# Get processing levels belonging to a thing
thing_datastreams = hs_api.processinglevels.list(thing="00000000-0000-0000-0000-000000000000")

# Get datastream with a given ID
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')
```

#### Example: Create Datastream
```python
from datetime import datetime

...

# Create a new datastream on HydroServer
new_datastream = hs_api.datastreams.create(
    name='Datastream A',
    description='A datastream containing environmental observations.',
    observation_type='Field Observation',
    sampled_medium='Air',
    no_data_value=-9999,
    aggregation_statistic='Continuous',
    time_aggregation_interval=1,
    status='Ongoing',
    result_type='Timeseries',
    value_count=0,
    phenomenon_begin_time=datetime(year=2024, month=1, day=1),
    phenomenon_end_time=None,
    result_begin_time=datetime(year=2024, month=1, day=1),
    result_end_time=None,
    is_visible=True,
    is_private=False,
    thing='00000000-0000-0000-0000-000000000000',
    sensor='00000000-0000-0000-0000-000000000000',
    observed_property='00000000-0000-0000-0000-000000000000',
    processing_level='00000000-0000-0000-0000-000000000000',
    unit='00000000-0000-0000-0000-000000000000',
    time_aggregation_interval_unit='hours',
    intended_time_spacing=1,
    intended_time_spacing_unit='hours'
)
```

Each of the methods above will return one or more Datastream objects. The examples below show the main properties and methods available to a Datastream object.

#### Example: Modify a Datastream
```python
# Get a datastream
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')

# Update one or more properties of the datastream.
datastream.name = 'Updated Datastream Name'

# Save the changes back to HydroServer.
datastream.save()
```

#### Example: Get related properties of a Datastream
```python
# Get a datastream
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')

# Get the datastream's Thing/Site
thing = datastream.thing

# Get the datastream's Sensor
sensor = datastream.sensor

# Get the datastream's Observed Property
observed_property = datastream.observed_property

# Get the datastream's Unit
unit = datastream.unit

# Get the datastream's Processing Level
processing_level = datastream.processing_level
```

#### Example: Get Observations of a Datastream
```python
from datetime import datetime

...

# Get a datastream
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')

# Get observations of a datastream between two timestamps
observations_df = datastream.get_observations(
    start_time=datetime(year=2023, month=1, day=1),
    end_time=datetime(year=2023, month=12, day=31)
)

# Get observations all observations of a datastream
full_observations_df = datastream.get_observations(
    fetch_all=True
)
```

#### Example: Upload Observations to a Datastream
```python
import pandas as pd

...

# Get a datastream
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')

# Create a DataFrame of observations
new_observations = pd.DataFrame(
    [
        ['2023-01-26 00:00:00+00:00', 40.0],
        ['2023-01-27 00:00:00+00:00', 41.0],
        ['2023-01-28 00:00:00+00:00', 42.0],
    ],
    columns=['timestamp', 'value']
)
new_observations['timestamp'] = pd.to_datetime(new_observations['timestamp'])

# Upload the observations to HydroServer
datastream.load_observations(new_observations)
```

#### Example: Refresh Datastream data from HydroServer
```python
# Get a datastream
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')

# Refresh datastream data from HydroServer
datastream.refresh()
```

#### Example: Delete Datastream from HydroServer
```python
# Get a datastream
datastream = hs_api.datastreams.get(uid='00000000-0000-0000-0000-000000000000')

# Delete the datastream from HydroServer
datastream.delete()
```

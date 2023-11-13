from pydantic import BaseModel, Field, root_validator
from typing import List, Optional
from uuid import UUID
from hydroserverpy.utils import allow_partial
from hydroserverpy.schemas.observed_properties import ObservedPropertyGetResponse
from hydroserverpy.schemas.processing_levels import ProcessingLevelGetResponse
from hydroserverpy.schemas.units import UnitGetResponse
from hydroserverpy.schemas.sensors import SensorGetResponse


class ThingID(BaseModel):
    id: UUID


class ThingFields(BaseModel):
    name: str
    description: str
    sampling_feature_type: str = Field(alias='samplingFeatureType')
    sampling_feature_code: str = Field(alias='samplingFeatureCode')
    site_type: str = Field(alias='siteType')
    data_disclaimer: str = Field(None, alias='dataDisclaimer')


class LocationFields(BaseModel):
    latitude: float
    longitude: float
    elevation_m: float = None
    elevation_datum: str = Field(None, alias='elevationDatum')
    state: str = None
    county: str = None


class OrganizationFields(BaseModel):
    organization_name: Optional[str] = Field(None, alias='organizationName')


class AssociationFields(BaseModel):
    is_primary_owner: bool = Field(..., alias='isPrimaryOwner')


class PersonFields(BaseModel):
    first_name: str = Field(..., alias='firstName')
    last_name: str = Field(..., alias='lastName')
    email: str

    class Config:
        allow_population_by_field_name = True


class OwnerFields(AssociationFields, OrganizationFields, PersonFields):
    pass


class ThingGetResponse(LocationFields, ThingFields, ThingID):
    is_private: bool = Field(..., alias='isPrivate')
    is_primary_owner: bool = Field(..., alias='isPrimaryOwner')
    owns_thing: bool = Field(..., alias='ownsThing')
    follows_thing: bool = Field(..., alias='followsThing')
    owners: List[OwnerFields]

    class Config:
        allow_population_by_field_name = True


class ThingPostBody(ThingFields, LocationFields):

    class Config:
        allow_population_by_field_name = True


@allow_partial
class ThingPatchBody(ThingFields, LocationFields):

    class Config:
        allow_population_by_field_name = True


class ThingOwnershipPatchBody(BaseModel):
    email: str
    make_owner: Optional[bool] = Field(False, alias='makeOwner')
    remove_owner: Optional[bool] = Field(False, alias='removeOwner')
    transfer_primary: Optional[bool] = Field(False, alias='transferPrimary')

    @root_validator()
    def validate_only_one_method_allowed(cls, field_values):

        assert [
                   field_values.get('make_owner', False),
                   field_values.get('remove_owner', False),
                   field_values.get('transfer_primary', False)
               ].count(True) == 1, \
            'You must perform one and only one action from among "makeOwner", "removeOwner", and "transferPrimary".'

        return field_values


class ThingPrivacyPatchBody(BaseModel):
    is_private: bool = Field(..., alias="isPrivate")


class ThingMetadataGetResponse(BaseModel):
    units: List[UnitGetResponse]
    sensors: List[SensorGetResponse]
    processing_levels: List[ProcessingLevelGetResponse] = Field(..., alias='processingLevels')
    observed_properties: List[ObservedPropertyGetResponse] = Field(..., alias='observedProperties')

    class Config:
        allow_population_by_field_name = True

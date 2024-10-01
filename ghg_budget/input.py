import uuid
from enum import Enum
from typing import Optional

import geojson_pydantic
import shapely
from pydantic import BaseModel, Field, field_validator


class DetailOption(Enum):
    SIMPLE = 'einfach'
    EXTENDED = 'erweitert'


class AoiProperties(BaseModel):
    name: str = Field(
        title='Name',
        description='The name of the area of interest i.e. a human readable description.',
        examples=['Heidelberg'],
    )
    id: str = Field(
        title='ID',
        description='A unique identifier of the area of interest.',
        examples=[uuid.uuid4()],
    )


class ComputeInput(BaseModel):
    aoi: geojson_pydantic.Feature[geojson_pydantic.MultiPolygon, AoiProperties] = Field(
        title='Area of Interest',
        description="The geographic area of interest for this plugin's indicator computation.",
        validate_default=True,
        examples=[
            {
                'type': 'Feature',
                'properties': {'name': 'Heidelberg', 'id': 'Q12345'},
                'geometry': {
                    'type': 'MultiPolygon',
                    'coordinates': [
                        [
                            [
                                [12.3, 48.22],
                                [12.3, 48.34],
                                [12.48, 48.34],
                                [12.48, 48.22],
                                [12.3, 48.22],
                            ]
                        ]
                    ],
                },
            }
        ],
    )
    level_of_detail: Optional[DetailOption] = Field(
        title='Detailgrad',
        description='Bitte wählen Sie, wie detailliert Sie die Ergebnisse haben möchten.',
        examples=[DetailOption.EXTENDED],
        default=DetailOption.EXTENDED,
    )

    @field_validator('aoi')
    def assert_aoi_properties_not_null(cls, aoi: geojson_pydantic.Feature) -> geojson_pydantic.Feature:
        assert aoi.properties, 'AOI properties are required.'
        assert aoi.properties.name == 'Heidelberg', 'Only works for the AOI Heidelberg at the moment.'
        return aoi

    def get_aoi_geom(self) -> shapely.MultiPolygon:
        """Convert the input geojson geometry to a shapely geometry.

        :return: A shapely.MultiPolygon representing the area of interest defined by the user.
        """
        return shapely.geometry.shape(self.aoi.geometry)

    def get_aoi_properties(self) -> AoiProperties:
        """Return the properties of the aoi.

        :return:
        """
        return self.aoi.properties

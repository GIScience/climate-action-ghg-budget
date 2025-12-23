import uuid

import pytest
import shapely
from climatoology.base.computation import ComputationScope
from climatoology.base.baseoperator import AoiProperties

from ghg_budget.core.input import ComputeInput
from ghg_budget.core.operator_worker import GHGBudget


@pytest.fixture
def default_aoi() -> shapely.MultiPolygon:
    return shapely.MultiPolygon(
        polygons=[
            [
                [
                    [8.65, 49.39],
                    [8.65, 49.43],
                    [8.74, 49.43],
                    [8.74, 49.39],
                    [8.65, 49.39],
                ]
            ]
        ]
    )


@pytest.fixture
def default_aoi_properties() -> AoiProperties:
    return AoiProperties(name='Heidelberg', id='heidelberg')


@pytest.fixture
def expected_compute_input() -> ComputeInput:
    # noinspection PyTypeChecker
    return ComputeInput(
        level_of_detail='erweitert',
    )


# The following fixtures can be ignored on plugin setup
@pytest.fixture
def compute_resources():
    with ComputationScope(uuid.uuid4()) as resources:
        yield resources


@pytest.fixture
def operator():
    return GHGBudget()

import uuid
from pathlib import Path
from typing import List

import pytest
from climatoology.base.artifact import ArtifactModality
from climatoology.base.computation import ComputationScope
from climatoology.base.operator import Concern, Info, PluginAuthor, _Artifact

from ghg_budget.input import ComputeInput
from ghg_budget.operator_worker import GHGBudget


@pytest.fixture
def expected_compute_input() -> ComputeInput:
    # noinspection PyTypeChecker
    return ComputeInput(
        bool_blueprint=True,
        aoi={
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
        },
    )


@pytest.fixture
def expected_info_output() -> Info:
    # noinspection PyTypeChecker
    return Info(
        name='GHG Budget',
        icon=Path('resources/info/hourglass.jpg'),
        authors=[
            PluginAuthor(
                name='Veit Ulrich',
                affiliation='HeiGIT gGmbH',
                website='https://heigit.org/heigit-team/',
            ),
            PluginAuthor(
                name='Niko Krasowski',
                affiliation='Klimanetz Heidelberg',
                website='https://klimanetz-heidelberg.de/',
            ),
            PluginAuthor(
                name='Moritz Schott',
                affiliation='HeiGIT gGmbH',
                website='https://heigit.org/heigit-team/',
            ),
        ],
        version='dummy',
        concerns=[Concern.CLIMATE_ACTION__GHG_EMISSION, Concern.CLIMATE_ACTION__MITIGATION],
        purpose=Path('resources/info/purpose.md').read_text(),
        methodology=Path('resources/info/methodology.md').read_text(),
        sources=Path('resources/info/sources.bib'),
    )


@pytest.fixture
def expected_compute_output(compute_resources) -> List[_Artifact]:
    markdown_artifact = _Artifact(
        name='Berechnung des CO₂-Budgets',
        modality=ArtifactModality.MARKDOWN,
        file_path=Path(compute_resources.computation_dir / 'methodology_description.md'),
        summary='Beschreibung der Methodik zur Berechnung des CO₂-Budgets',
    )
    table_artifact = _Artifact(
        name='CO₂ Budget Heidelberg [kt]',
        modality=ArtifactModality.TABLE,
        file_path=Path(compute_resources.computation_dir / 'ghg_budget_heidelberg.csv'),
        summary='Die Tabelle zeigt das verbleibende CO₂-Budget Heidelbergs in Kilotonnen (kt) für verschiedene Temperaturziele und'
        'Wahrscheinlichkeiten, dass diese erreicht werden.',
        description='Eine Tabelle mit drei Spalten',
    )
    chart_artifact = _Artifact(
        name='Vergleich der gesamten geplanten CO₂-Emissionen Heidelbergs mit den CO₂-Budgets',
        modality=ArtifactModality.CHART,
        primary=False,
        file_path=Path(compute_resources.computation_dir / 'comparison_emissions_budgets.json'),
        summary='Das Diagramm zeigt die Summe der ab 2016 gemessenen und geplanten CO₂-Emissionen Heidelbergs '
        'im Vergleich mit den verbleibenden CO₂-Budgets für das Erreichen der verschiedenen Temperaturziele '
        'mit einer Wahrscheinlichkeit von 83 %.',
    )
    return [
        markdown_artifact,
        table_artifact,
        chart_artifact,
    ]


# The following fixtures can be ignored on plugin setup
@pytest.fixture
def compute_resources():
    with ComputationScope(uuid.uuid4()) as resources:
        yield resources


@pytest.fixture
def operator():
    return GHGBudget()

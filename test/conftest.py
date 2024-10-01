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
        level_of_detail='erweitert',
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
        version='demo',
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
        name='CO₂ Budget Heidelberg',
        modality=ArtifactModality.TABLE,
        file_path=Path(compute_resources.computation_dir / 'ghg_budget_heidelberg.csv'),
        summary='Um mit einer Wahrscheinlichkeit von 67 % bzw. 83 % die Temperaturerhöhung auf den jeweiligen '
        'Maximalwert zu begrenzen, hat Heidelberg nur ein beschränktes CO₂-Budget zur Verfügung. Das heißt, '
        'dass der Stadt Heidelberg für die Einhaltung des Paris-Ziels von 1,5 °C mit einer Wahrscheinlichkeit '
        'von 83 % das geringste Budget zur Verfügung steht, um ihren Anteil zur Erreichung des Ziels '
        'beizutragen. Nehmen wir gesellschaftlich ein größeres Risiko des Scheiterns in Kauf, also eine '
        'Wahrscheinlichkeit von nur 67 %, um das Ziel zu erreichen, steht Heidelberg ein höheres Budget zur '
        'Verfügung. Gleiches gilt für höhere Zieltemperaturen (1,7 °C bzw. 2 °C): Diese bedeuten ebenfalls, '
        'dass noch mehr CO₂ emittiert werden darf.',
        description='**Erläuterung der Spalten**\n\n'
        '**Temperaturziel (°C):** Angestrebte Begrenzung auf eine maximale Erwärmung. Das internationale Abkommen von '
        'Paris gibt eine Begrenzung auf deutlich unter 2 °C Temperaturerhöhung vor.\n\n'
        '**Wahrscheinlichkeit:** Wie stark die globale Durchschnittstemperatur durch eine bestimmte Menge an '
        'ausgestoßenem CO₂ steigt, kann nicht exakt vorhergesagt werden. Daher berechnet der Weltklimarat '
        '(IPCC) die globalen CO₂-Budgets für verschiedene Wahrscheinlichkeiten, dass die Temperaturziele '
        'eingehalten werden.\n\n'
        '**BISKO CO₂-Budget 2016 (1000 Tonnen):** Jene CO₂-Budgets, die Heidelberg 2016 noch zur Verfügung standen, '
        'als die Pariser Klimaziele beschlossen wurden. '
        '[BISKO](https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Angebote/Beschreibung_der_BISKO-Methodik.pdf) '
        'ist ein vom Institut für Energie- und Umweltforschung (IFEU) entwickelter Standard, nach dem '
        'viele Städte wie beispielsweise Heidelberg ihre Emissionen schätzen.\n\n'
        '**BISKO CO₂-Budget 2024 (1000 Tonnen):** CO₂-Budgets, die Heidelberg aktuell noch zur '
        'Verfügung stehen. Ein negativer Wert bedeutet, dass das verfügbare Budget bereits überschritten '
        'ist.\n\n'
        '**CO₂-Budget aufgebraucht (Jahr):** Wann die CO₂-Budgets aufgebraucht sind, hängt davon ab, '
        'wie schnell wir unsere Emissionen reduzieren und auf Null bringen. Die Jahreszahlen in dieser '
        'Spalte beruhen auf der Annahme, dass die Stadt Heidelberg die von ihr bereits beschlossenen '
        'Maßnahmen zur Emissionsreduzierung erfolgreich umsetzt.\n\n'
        '**Anmerkung:** Die CO₂-Budgets in dieser Tabelle sind nicht so zu verstehen, dass die Temperaturziele '
        'automatisch erreicht werden, wenn Heidelberg die Budgets einhält. Damit die Klimaziele '
        'erreicht werden, muss die ganze Welt ihr CO₂-Budget einhalten. Jedoch wollen wir mit diesen Informationen auf '
        'die Verantwortung der Stadt Heidelberg sowie aller Heidelberger:innen hinweisen, und ihren Anteil an den '
        'globalen Emissionen darstellen.\n\n'
        'Mehr Informationen zu den CO₂-Budgets finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        primary=False,
    )
    comparison_chart_artifact = _Artifact(
        name='Vergleich der gesamten geplanten CO₂-Emissionen Heidelbergs mit den CO₂-Budgets',
        modality=ArtifactModality.CHART,
        primary=False,
        file_path=Path(compute_resources.computation_dir / 'comparison_emissions_budgets.json'),
        summary='Das Diagramm zeigt die Summe der ab 2016 gemessenen und geplanten CO₂-Emissionen Heidelbergs '
        '(in 1000 Tonnen) im Vergleich mit den verbleibenden CO₂-Budgets für das Erreichen der verschiedenen '
        'Temperaturziele mit einer Wahrscheinlichkeit von 83 %.',
    )
    time_chart_artifact = _Artifact(
        name='Entwicklung der CO₂-Emissionen in Heidelberg',
        modality=ArtifactModality.CHART,
        primary=True,
        file_path=Path(compute_resources.computation_dir / 'time_chart.json'),
        summary='Entwicklung der CO₂-Emissionen Heidelbergs ab 2016 (in 1000 Tonnen)',
        description='Die Emissionswerte von 2016 bis 2021 sind Messwerte basierend auf dem BISKO-Standard, die Werte '
        'ab 2022 sind Prognosen unter der Annahme, dass die zurzeit beschlossenen '
        'Maßnahmen Heidelbergs zur Emissionsreduzierung umgesetzt werden. \n\nAnmerkung: Die Emissionswerte bilden '
        'nicht die gesamten Emissionen der Stadt Heidelberg ab, sondern nur etwa 64 % der Emissionen. Dies liegt '
        'daran, dass die Emissionen nach dem BISKO-Standard ermittelt wurden. Mehr Informationen zur BISKO-Systematik '
        'finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
    )
    return [
        markdown_artifact,
        table_artifact,
        comparison_chart_artifact,
        time_chart_artifact,
    ]


@pytest.fixture
def expected_simple_compute_output(compute_resources) -> List[_Artifact]:
    markdown_simple_artifact = _Artifact(
        name='Berechnung des CO₂-Budgets',
        modality=ArtifactModality.MARKDOWN,
        file_path=Path(compute_resources.computation_dir / 'simple_methodology_description.md'),
        summary='Beschreibung der Methodik zur Berechnung des CO₂-Budgets',
    )
    table_simple_artifact = _Artifact(
        name='CO₂ Budget Heidelberg',
        modality=ArtifactModality.TABLE,
        file_path=Path(compute_resources.computation_dir / 'simple_ghg_budget_heidelberg.csv'),
        summary='Um die Temperaturerhöhung auf den jeweiligen Maximalwert zu begrenzen, hat Heidelberg nur ein '
        'beschränktes CO₂-Budget zur Verfügung. Das heißt, dass der Stadt Heidelberg für die Einhaltung des '
        'Paris-Ziels von 1,5 °C das geringste Budget zur Verfügung steht, um ihren Anteil zur Erreichung des '
        'Ziels beizutragen. Für höhere Zieltemperaturen (1,7 °C bzw. 2 °C) darf noch mehr CO₂ emittiert '
        'werden.',
        description='**Erläuterung der Spalten**\n\n'
        '**Temperaturziel (°C):** Angestrebte Begrenzung auf eine maximale Erwärmung. Das internationale '
        'Abkommen von Paris gibt eine Begrenzung auf deutlich unter 2 °C Temperaturerhöhung vor.\n\n'
        '**BISKO CO₂-Budget 2024 (1000 Tonnen):** CO₂-Budgets, die Heidelberg aktuell noch zur Verfügung stehen. Ein '
        'negativer Wert bedeutet, dass das verfügbare Budget bereits überschritten ist. '
        '[BISKO](https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Angebote/Beschreibung_der_BISKO-Methodik.pdf) '
        'ist ein vom Institut für Energie- und Umweltforschung (IFEU) entwickelter Standard, nach dem '
        'viele Städte wie beispielsweise Heidelberg ihre Emissionen schätzen.\n\n'
        '**CO₂-Budget aufgebraucht (Jahr):** Wann die CO₂-Budgets aufgebraucht sind, hängt davon ab, '
        'wie schnell wir unsere Emissionen reduzieren und auf Null bringen. Die Jahreszahlen in dieser '
        'Spalte beruhen auf der Annahme, dass die Stadt Heidelberg die von ihr bereits beschlossenen '
        'Maßnahmen zur Emissionsreduzierung erfolgreich umsetzt.\n\n'
        '**Anmerkung:** Die CO₂-Budgets in dieser Tabelle sind nicht so zu verstehen, dass die Temperaturziele '
        'automatisch erreicht werden, wenn Heidelberg die Budgets einhält. Damit die Klimaziele '
        'erreicht werden, muss die ganze Welt ihr CO₂-Budget einhalten. Jedoch wollen wir mit diesen Informationen auf '
        'die Verantwortung der Stadt Heidelberg sowie aller Heidelberger:innen hinweisen, und ihren Anteil an den '
        'globalen Emissionen darstellen.\n\n'
        'Mehr Informationen zu den CO₂-Budgets finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
        primary=False,
    )
    time_chart_artifact = _Artifact(
        name='Entwicklung der CO₂-Emissionen in Heidelberg',
        modality=ArtifactModality.CHART,
        primary=True,
        file_path=Path(compute_resources.computation_dir / 'time_chart.json'),
        summary='Entwicklung der CO₂-Emissionen Heidelbergs ab 2016 (in 1000 Tonnen)',
        description='Die Emissionswerte von 2016 bis 2021 sind Messwerte basierend auf dem BISKO-Standard, die Werte '
        'ab 2022 sind Prognosen unter der Annahme, dass die zurzeit beschlossenen '
        'Maßnahmen Heidelbergs zur Emissionsreduzierung umgesetzt werden. \n\nAnmerkung: Die Emissionswerte bilden '
        'nicht die gesamten Emissionen der Stadt Heidelberg ab, sondern nur etwa 64 % der Emissionen. Dies liegt '
        'daran, dass die Emissionen nach dem BISKO-Standard ermittelt wurden. Mehr Informationen zur BISKO-Systematik '
        'finden Sie links im Reiter "Berechnung des CO₂-Budgets".',
    )
    return [
        markdown_simple_artifact,
        table_simple_artifact,
        time_chart_artifact,
    ]


# The following fixtures can be ignored on plugin setup
@pytest.fixture
def compute_resources():
    with ComputationScope(uuid.uuid4()) as resources:
        yield resources


@pytest.fixture
def operator():
    return GHGBudget()

import pandas as pd
from climatoology.base.artifact import Artifact, ArtifactMetadata
from climatoology.base.artifact_creators import (
    create_markdown_artifact,
    create_table_artifact,
    create_plotly_chart_artifact,
)
from climatoology.base.computation import ComputationResources
from climatoology.base.i18n import tr, translate_dataframe
from plotly.graph_objects import Figure

from ghg_budget.components.data import NOW_YEAR, EMISSION_PROJECTION_CITIES


def build_methodology_description_simple_artifact(text: str, resources: ComputationResources) -> Artifact:
    methodology_description_simple_artifact_metadata = ArtifactMetadata(
        name=tr('Calculation of the CO₂-budget'),
        summary=tr(' '),
        filename='simple_methodology_description',
    )

    result = create_markdown_artifact(
        text=text,
        metadata=methodology_description_simple_artifact_metadata,
        resources=resources,
    )
    return result


def build_time_chart_artifact(
    line_chart: Figure, resources: ComputationResources, city_name: str, aoi_emission_end_year: int
) -> Artifact:
    name = tr('Development of the CO₂-emissions in {city_name}').format(city_name=city_name)
    summary = tr(
        'Development of the CO₂-emissions in {city_name} and alternative reduction paths since 2016 by maintaining '
        'temperature thresholds with 83 % probability (in 1000 tons)'
    ).format(city_name=city_name)

    description_main = tr(
        'The emission values from 2016 up to {aoi_emission_end_year} in the data set "reported" are reported values '
        'based on the BISKO-standard, the values from {year_after} onwards are predictions assuming that the measures '
        'adopted by {city_name} to reduce emissions are actually implemented. '
        'The alternative reduction paths represent fictive scenarios of how {city_name} could become (or could have '
        'become) CO₂-neutral by 2040 without exceeding the CO₂-budgets available to stay below certain temperature '
        'thresholds. '
        'Note that the Paris agreement demands a limit significantly below 2&nbsp;°C.'
    )
    description_remark = tr(
        'Note: The emission values do not represent the entire emissions of {city_name} but only about 64&nbsp;% of '
        'the emissions. '
        'This is due to how emissions are determined according to the BISKO-Standard. The BISKO-Standard reflects, in '
        'simple terms, only emissions within the city boundaries of {city_name} but not those emitted by inhabitants '
        'of {city_name} outside the city area. '
        'More information on the BISKO classification can be found on the left under "Calculation of the CO₂-budget".'
    )
    description = '\n\n'.join([description_main, description_remark])
    description = description.format(
        city_name=city_name, aoi_emission_end_year=aoi_emission_end_year, year_after=aoi_emission_end_year + 1
    )

    if city_name not in EMISSION_PROJECTION_CITIES:
        description_pre_warning = tr(
            '**Because we do not have any emission projections for {city_name}, we created our own estimation. '
            'It is not based on potentially planned measures of the city. The actually targeted reduction path of '
            '{city_name} may therefore differ from ours.**'
        ).format(city_name=city_name)
        description = f'{description_pre_warning}\n\n{description}'

    time_chart_artifact_metadata = ArtifactMetadata(
        name=name,
        summary=summary,
        description=description,
        filename='time_chart',
    )

    result = create_plotly_chart_artifact(
        figure=line_chart,
        metadata=time_chart_artifact_metadata,
        resources=resources,
    )
    return result


def build_budget_table_artifact(table: pd.DataFrame, resources: ComputationResources, city_name: str) -> Artifact:
    latest_column_name = tr('{NOW_YEAR} BISKO CO₂-budget (1000 tons)').format(NOW_YEAR=NOW_YEAR)
    table = table.rename(columns={'BISKO CO₂-budget 2016 (1000 tons)': latest_column_name})
    table = translate_dataframe(table)

    name = tr('{city_name} CO₂ budget').format(city_name=city_name)
    summary = tr('How much of the CO₂-budget of {city_name} is already consumed?').format(city_name=city_name)
    description_intro = tr(
        'To limit the temperature increase to the respective maximum value with a probability of 67&nbsp;% or '
        '83&nbsp;%, {city_name} only has a limited CO₂ budget available. '
        'This means that the city of {city_name} has the smallest budget available to contribute its share toward '
        'staying below the 1.5&nbsp;°C limit with a probability of 83&nbsp;%. '
        'If we as a society accept a greater risk of failure, that is, only a 67&nbsp;% probability of staying within '
        'the limit, {city_name} has a larger budget available. '
        'The same applies to higher temperature thresholds (1.7&nbsp;°C and 2&nbsp;°C respectively): These also mean '
        'that more CO₂ may still be emitted.'
    )
    description_explanation_title = tr('**Explanation of the columns**')
    description_temperature = tr(
        '**Temperature limit (°C):** Target limit on maximum warming. '
        'The Paris Agreement stipulates limiting the temperature increase to well below 2&nbsp;°C. '
        'Global warming of 1.5&nbsp;°C already increases the risk of extreme weather events such as heatwaves and '
        'heavy rainfall. '
        'At 2&nbsp;°C of warming, these risks will be considerably higher. '
        'The specific impacts, however, depend on the trajectory of greenhouse gas emissions — in particular on '
        'whether and by how much the 1.5&nbsp;°C threshold is temporarily exceeded. '
        'Further information on the effects of 1.5&nbsp;°C warming and 2&nbsp;°C warming respectively can be found '
        '[here](https://www.ipcc.ch/site/assets/uploads/sites/2/2018/12/SR15_FAQ_Low_Res.pdf) under FAQ 3.1.'
    )
    description_probability = tr(
        '**Probability:** The exact increase in temperature for a certain amount of emitted CO₂ cannot be predicted '
        'exactly. '
        'The International Panel on Climate Change (IPCC) therefore calculates global CO₂-budgets for various '
        'probabilities of staying below temperature thresholds.'
    )
    description_bisko_2016 = tr(
        '**BISKO CO₂-budget 2016 (1000 tons):** The CO₂-budgets still available to {city_name} in 2016, when the Paris '
        'climate targets were decided. '
        '[BISKO](https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Angebote/Beschreibung_der_BISKO-Methodik.pdf) '
        'is a standard developed by the Institute for Energy and Environmental Research (IFEU), according to which '
        'many cities such as {city_name} estimate their emissions.'
    )
    description_bisko_now = tr(
        '**{NOW_YEAR} BISKO CO₂-budget (1000 tons):** CO₂-budget still available to {city_name}. A negative value '
        'means that the available budget has already been exceeded.'
    )
    description_co2_budget = tr(
        '**CO₂-budget consumed (year):** When the CO₂-budgets will be exhausted depends on how quickly we reduce our '
        'emissions and bring them down to zero. '
        'The year dates shown in this column are based on the assumption that the city of {city_name} successfully '
        'implements the emission reduction measures it has already agreed upon. '
        'If the column reads "will not be consumed", this means that {city_name}, based on current emission '
        'projections, will not exceed this budget.'
    )
    description_remark = tr(
        '**Note:** The CO₂-budgets in this table do not mean that the temperature limits will automatically be met if '
        '{city_name} stays within its budgets. '
        'For the limits not to be exceeded, the entire world must adhere to its CO₂-budget. '
        'However, with this information we aim to highlight the responsibility of {city_name} and its inhabitants, and '
        'to illustrate their share of global emissions.'
    )
    description_further_info = tr(
        'You can find more information on CO₂-budgets on the left under "Calculation of the CO₂-budget".'
    )
    description = '\n\n'.join(
        [
            description_intro,
            description_explanation_title,
            description_temperature,
            description_probability,
            description_bisko_2016,
            description_bisko_now,
            description_co2_budget,
            description_remark,
            description_further_info,
        ]
    )
    description = description.format(city_name=city_name, NOW_YEAR=NOW_YEAR)

    budget_table_artifact_metadata = ArtifactMetadata(
        name=name,
        summary=summary,
        description=description,
        filename='ghg_budget_table',
    )

    result = create_table_artifact(
        data=table,
        metadata=budget_table_artifact_metadata,
        resources=resources,
    )
    return result


def build_budget_table_simple_artifact(
    table: pd.DataFrame, resources: ComputationResources, city_name: str
) -> Artifact:
    latest_column_name = tr('BISKO CO₂-budget {NOW_YEAR} (1000 tons)').format(NOW_YEAR=NOW_YEAR)
    table = table.rename(columns={'BISKO CO₂-budget now (1000 tons)': latest_column_name})
    table = translate_dataframe(table)

    name = tr('{city_name} CO₂ budget').format(city_name=city_name)
    summary = tr('How much of the CO₂-budget of {city_name} is already consumed?').format(city_name=city_name)

    description_intro = tr(
        'To limit warming to the respective maximum temperature value, {city_name} only has a limited CO₂-budget at '
        'its disposal. '
        'This means that, in order to meet the 1.5 °C limit, the city of {city_name} has the smallest budget available '
        'to contribute to keeping warming below that threshold. '
        'For higher temperature thresholds (1.7&nbsp;°C and 2&nbsp;°C respectively), more CO₂ may still be emitted.'
    )
    description_explanation_title = tr('**Explanation of the columns**')
    description_temperature = tr(
        '**Temperature limit (°C):** Target limit on maximum warming. '
        'The Paris Agreement stipulates limiting the temperature increase to well below 2&nbsp;°C. '
        'Global warming of 1.5&nbsp;°C already increases the risk of extreme weather events such as heatwaves and '
        'heavy rainfall. '
        'At 2&nbsp;°C of warming, these risks will be considerably higher. '
        'The specific impacts, however, depend on the trajectory of greenhouse gas emissions — in particular on '
        'whether and by how much the 1.5&nbsp;°C threshold is temporarily exceeded. '
        'Further information on the effects of 1.5&nbsp;°C warming and 2&nbsp;°C warming respectively can be found '
        '[here](https://www.ipcc.ch/site/assets/uploads/sites/2/2018/12/SR15_FAQ_Low_Res.pdf) under FAQ 3.1.'
    )
    description_bisko_now = tr(
        '**BISKO CO₂-budget {NOW_YEAR} (1000 tons):** CO₂-budgets currently still available to {city_name} to meet the '
        'temperature limit with an 83&nbsp;% probability. '
        'A negative value means that the available budget has already been exceeded. '
        '[BISKO](https://www.kea-bw.de/fileadmin/user_upload/Energiemanagement/Angebote/Beschreibung_der_BISKO-Methodik.pdf) '
        'is a standard developed by the Institute for Energy and Environmental Research (IFEU), which many cities such '
        'as {city_name} use to estimate their emissions.'
    )
    description_co2_budget = tr(
        '**CO₂-budget consumed (year):** When the CO₂-budgets will be exhausted depends on how quickly we reduce our '
        'emissions and bring them down to zero. '
        'The year dates shown in this column are based on the assumption that the city of {city_name} successfully '
        'implements the emission reduction measures it has already agreed upon. '
        'If the column reads "will not be consumed", this means that {city_name}, based on current emission '
        'projections, will not exceed this budget.'
    )
    description_remark = tr(
        '**Note:** The CO₂-budgets in this table do not mean that the temperature limits will automatically be met if '
        '{city_name} stays within its budgets. '
        'For the limits not to be exceeded, the entire world must adhere to its CO₂-budget. '
        'However, with this information we aim to highlight the responsibility of {city_name} and its inhabitants, and '
        'to illustrate their share of global emissions.'
    )
    description_g = tr(
        'You can find more information on CO₂-budgets on the left under "Calculation of the CO₂-budget".'
    )
    description = '\n\n'.join(
        [
            description_intro,
            description_explanation_title,
            description_temperature,
            description_bisko_now,
            description_co2_budget,
            description_remark,
            description_g,
        ]
    )
    description = description.format(city_name=city_name, NOW_YEAR=NOW_YEAR)

    budget_table_simple_artifact_metadata = ArtifactMetadata(
        name=name,
        summary=summary,
        description=description,
        filename='simple_ghg_budget_table',
    )
    result = create_table_artifact(
        data=table,
        metadata=budget_table_simple_artifact_metadata,
        resources=resources,
    )
    return result


def build_budget_comparison_chart_artifact(
    fig: Figure, resources: ComputationResources, city_name: str, aoi_emission_end_year: int
) -> Artifact:
    name = tr('How much CO₂-budget has already been emitted?')
    summary = tr(
        "The share of {city_name}'s emissions on the global CO₂-emission that, with an  83 % probability, would keep "
        'warming within the 1.5 °C target (or lead to warming of 1.7 °C/2.0 °C , compared with reported and projected '
        'emissions (up until {aoi_emission_end_year}).'
    ).format(city_name=city_name, aoi_emission_end_year=aoi_emission_end_year)
    description = tr(
        'The chart shows the CO₂-budgets available to {city_name} since the 2015 Paris Climate Conference to meet '
        'various temperature limits with an 83&nbsp;% probability. '
        "The grey bar to the right shows the total of the CO₂-budget already used and {city_name}'s the projected "
        'emissions. '
        'The dark grey section of the bar shows how much CO₂ {city_name} emitted from 2016 until '
        '{aoi_emission_end_year}, the most recent year for which data is available. '
        'It therefore illustrates how much of the CO₂-budget has already been used up. '
        'The light grey section shows how much CO₂ {city_name} is expected to emit before achieving climate '
        'neutrality. '
        'This projection is based on the climate protection measures currently adopted by the city of {city_name}. '
        'The chart shows that even the CO₂-budget for the 2&nbsp;°C threshold will be significantly exceeded if the '
        'city of {city_name} does not make additional efforts to reduce emissions. '
        'It should be noted that the Paris Agreement stipulates limiting the temperature increase to well below '
        '2&nbsp;°C.'
    ).format(city_name=city_name, aoi_emission_end_year=aoi_emission_end_year)

    if city_name not in EMISSION_PROJECTION_CITIES:
        description_pre_warning = tr(
            '**Because we do not have any emission projections for {city_name}, we created our own estimation. '
            'It is not based on potentially planned measures of the city. '
            'The actually targeted reduction path of {city_name} may therefore differ from ours.**'
        ).format(city_name=city_name)
        description = f'{description_pre_warning}\n\n{description}'

    budget_comparison_chart_artifact_metadata = ArtifactMetadata(
        name=name,
        summary=summary,
        description=description,
        filename='comparison_emissions_budgets',
    )
    result = create_plotly_chart_artifact(
        figure=fig,
        metadata=budget_comparison_chart_artifact_metadata,
        resources=resources,
    )
    return result


def build_cumulative_chart_artifact(
    fig: Figure, resources: ComputationResources, city_name: str, aoi_emission_end_year: int
) -> Artifact:
    name = tr('Cumulative CO₂-emissions in {city_name}').format(city_name=city_name)
    summary = tr('Total CO₂-emissions in {city_name} per year since 2016 (in 1000 tons)').format(city_name=city_name)

    description_main = tr(
        'A reduction in CO₂ emissions does not mean that the concentration of CO₂ in the atmosphere decreases, but '
        'merely that it is rising more slowly. '
        'The concentration of CO₂ in the atmosphere will continue to rise as long as more CO₂ enters the atmosphere '
        'than escapes from it. '
        'You can think of it as a bathtub into which water is being filled. '
        'If I turn the tap down a little, less water flows into the tub, but as long as the plug is in, the water '
        'level still continues to rise, albeit more slowly. '
        'This is shown in this chart. '
        'The emission figures from 2016 to {aoi_emission_end_year} are reported figures based on the BISKO standard. '
        'The figures from {year_after} onwards are projections based on the assumption that the emission reduction '
        'measures currently agreed upon by {city_name} will be implemented.'
    )
    description_remark = tr(
        'Note: The emission values do not represent the entire emissions of {city_name} but only about 64&nbsp;% of '
        'the emissions. '
        'This is due to how emissions are determined according to the BISKO-Standard. '
        'The BISKO-Standard reflects, in simple terms, only emissions within the city boundaries of {city_name} but '
        'not those emitted by inhabitants of {city_name} outside the city area. '
        'More information on the BISKO classification can be found on the left under "Calculation of the CO₂-budget".'
    )
    description = '\n\n'.join([description_main, description_remark])
    description = description.format(
        city_name=city_name, aoi_emission_end_year=aoi_emission_end_year, year_after=aoi_emission_end_year + 1
    )

    if city_name not in EMISSION_PROJECTION_CITIES:
        description_pre_warning = tr(
            '**Because we do not have any emission projections for {city_name}, we created our own estimation. '
            'It is not based on potentially planned measures of the city. '
            'The actually targeted reduction path of {city_name} may therefore differ from ours.**'
        ).format(city_name=city_name)
        description = f'{description_pre_warning}\n\n{description}'

    cumulative_chart_artifact_metadata = ArtifactMetadata(
        name=name,
        summary=summary,
        description=description,
        filename='cumulative_chart',
    )
    result = create_plotly_chart_artifact(
        figure=fig,
        metadata=cumulative_chart_artifact_metadata,
        resources=resources,
    )
    return result


def build_emission_reduction_chart_artifact(
    fig: Figure,
    resources: ComputationResources,
    city_name: str,
    aoi_bisko_budgets: pd.DataFrame,
    percentage_decrease: int,
) -> Artifact:
    bisko_budget_now_year = aoi_bisko_budgets['BISKO CO₂-budget now (1000 tons)'].iloc[-1]

    name = tr('CO₂-emission reduction paths for {city_name}').format(city_name=city_name)
    summary = tr(
        'Selection of potential CO₂-reduction paths of {city_name} that stay below the temperature threshold of 2°C '
        'with 83 % probability'
    ).format(city_name=city_name)

    description_intro = tr(
        'Many cities have already used up their CO₂-budget for meeting the 1.5&nbsp;°C temperature limit and will soon '
        'have used up the budget for 1.7&nbsp;°C as well. '
        'This chart therefore illustrates a selection of possible CO₂ reduction pathways that comply with the '
        '2&nbsp;°C temperature limit. '
        'It should be noted that the Paris Agreement stipulates limiting the temperature increase to well below '
        '2&nbsp;°C.'
    )
    description_main = tr(
        'In {NOW_YEAR}, the city of {city_name} still has a CO₂-budget of approximately {bisko_budget_now_year} '
        'kilotons available to stay within the 2&nbsp;°C temperature limit with a 83&nbsp;% probability. '
        'The values for the annual emission decrease in the reduction pathways are chosen such that the budget is '
        'exhausted precisely in the year in which emissions drop to zero. '
        'Thus, the sum of the values in each curve corresponds approximately to the CO₂-budget of '
        '{bisko_budget_now_year} kilotons. '
        'The chart shows that we have more time to become CO₂-neutral if we reduce emissions by '
        '{percentage_decrease}&nbsp;% each year than if we reduce them linearly. '
        'The budget is used up particularly quickly if we do not reduce emissions at all.'
    )
    description_outro = tr(
        'This diagram only shows fictive scenarios. '
        'You can find a projection of the real emissions of {city_name} on the left under "Development of '
        'CO₂-emissions in {city_name}".'
    )
    description = '\n\n'.join([description_intro, description_main, description_outro])
    description = description.format(
        city_name=city_name,
        NOW_YEAR=NOW_YEAR,
        bisko_budget_now_year=bisko_budget_now_year,
        percentage_decrease=percentage_decrease,
    )

    emission_reduction_chart_artifact_metadata = ArtifactMetadata(
        name=name,
        summary=summary,
        description=description,
        filename='emission_reduction_chart',
    )
    result = create_plotly_chart_artifact(
        figure=fig,
        metadata=emission_reduction_chart_artifact_metadata,
        resources=resources,
    )
    return result


def build_emissions_growth_rates_chart_artifact(
    fig: Figure,
    resources: ComputationResources,
) -> Artifact:
    name = tr('Comparison of CO₂-emission reduction')
    summary = tr('Average yearly reduction rate of CO₂-emissions from 2016 to {NOW_YEAR}').format(NOW_YEAR=NOW_YEAR)

    description_main = tr(
        'This figure shows the annual CO₂ emission reduction rates for cities for which emission data is currently '
        'available. '
        'The reduction rates were calculated using the Compound Annual Growth Rate (CAGR). '
        'The analysis is based on reported CO₂ emissions in accordance with the BISKO standard and covers the period '
        'from 2016 to {NOW_YEAR}.'
    )
    description_remark = tr(
        'Note that the last year of reported data differs between cities: Heidelberg (2022), Bonn (2022), '
        'Berlin (2023), Karlsruhe (2019) and Hamburg (2019). '
        'Emission data beyond these years are based on estimates and not on reported data.'
    )
    description = '\n\n'.join([description_main, description_remark])
    description = description.format(NOW_YEAR=NOW_YEAR)

    emissions_growth_rates_artifact_metadata = ArtifactMetadata(
        name=name,
        summary=summary,
        description=description,
        filename='emissions_growth_rates',
    )
    result = create_plotly_chart_artifact(
        figure=fig,
        metadata=emissions_growth_rates_artifact_metadata,
        resources=resources,
    )
    return result

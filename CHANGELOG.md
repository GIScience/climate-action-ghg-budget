# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project mostly adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/compare/1.0.0...main)

## [1.0.0](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/releases/1.0.0)

### Changed
- account for new explicit AOI input by moving it from the input parameters to the compute method input
- simplify the plugin module with the new functionality in climatoology and now using the celery library
- Improved documentation and descriptions ([#14](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/14), [#17](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/17))
- Update climatoology to 6.4.2
- Rename plugin to "CO₂ Budget" ([#32](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/32))
- Create bar chart comparing CO2 budgets to projected emissions of Heidelberg with Plotly ([#38](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/38))
- Restructure plugin into a core and a components module ([#41](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/41))
- Changing the single bars in the comparison chart to the stacked bar ([#42](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/42))
- Splitting the emission curve to measured and projected sections ([#44](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/44))
- Modifying the colors in the charts to have uniform colors ([#47](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/47))
- Change wording throughout the plugin to "Grenzen/Grenzwerte" instead of "Temperaturziele" ([#46](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/46))
- Use decimal comma consequently throughout all charts, refine texts

### Fixed
- An issue caused by the ohsome-py library that prevented setting the correct logging level
- An issue induced by an update of pydantic that would break plugin representation in the front-end (see [climatoology#105](https://gitlab.heigit.org/climate-action/climatoology/-/issues/105))

### Added
- Chart with temporal development of emissions in Heidelberg, as well as alternative emission reduction paths ([#6](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/6))
- Updated emission data for Heidelberg ([#5](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/5))
- Simple version of GHG budget plugin ([#7](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/7))
- Chart showing cumulative emissions of Heidelberg ([#27](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/27))
- Chart showing different possible emission reduction paths for Heidelberg ([#28](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/28))
- Geoblocker for Heidelberg ([#33](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/33))
- Add commit hash to plugin version in dockerfile ([#37](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/37))
- Add test coverage checks to CI pipeline ([#36](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/36))
- Demo computation ([38](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/38))

## [Dummy](https://gitlab.gistools.geog.uni-heidelberg.de/climate-action/plugins/ghg-budget/-/releases/dummy)
### Added
- First version of CO2 budget calculation limited to city of Heidelberg, Germany
- Calculation with real input data (global CO2 budget estimates by IPCC, emission data from city of Heidelberg)
- Includes remaining CO2 budgets for 1.5, 1.7 and 2.0 °C warming
- Created artifacts: Methodology description, CO2 budget table, bar chart comparing CO2 budgets to projected emissions of Heidelberg
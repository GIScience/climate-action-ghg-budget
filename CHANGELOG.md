# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project mostly adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased](https://gitlab.gistools.geog.uni-heidelberg.de/climate-action/plugins/ghg-budget/-/compare/dummy...main?from_project_id=854&straight=false)
### Changed
This also means that a postgres server, that serves as the result backend for Celery, is now required to run the
plugin.
- use renamed BaseOperator instead of the old Operator class to inherit custom operators from
- account for new explicit AOI input by moving it from the input parameters to the compute method input
- simplify the plugin module with the new functionality in climatoology and now using the celery library
- Improved documentation and descriptions ([#14](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/14), [#17](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/17))
- Update climatoology to 6.4.1
- Rename plugin to "CO₂ Budget" ([#32](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/32))
### Fixed
- An issue caused by the ohsome-py library that prevented setting the correct logging level
- An issue induced by an update of pydantic that would break plugin representation in the front-end (see [climatoology#105](https://gitlab.heigit.org/climate-action/climatoology/-/issues/105))
### Added
- Chart with temporal development of emissions in Heidelberg, as well as alternative emission reduction paths [#6](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/6)
- Updated emission data for Heidelberg [#5](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/5)
- Simple version of GHG budget plugin [#7](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/7)
- Chart showing cumulative emissions of Heidelberg [#27](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/27)
- Geoblocker for Heidelberg [#33](https://gitlab.heigit.org/climate-action/plugins/ghg-budget/-/issues/33)

## [Dummy](https://gitlab.gistools.geog.uni-heidelberg.de/climate-action/plugins/ghg-budget/-/releases/dummy)
### Added
- First version of CO2 budget calculation limited to city of Heidelberg, Germany
- Calculation with real input data (global CO2 budget estimates by IPCC, emission data from city of Heidelberg)
- Includes remaining CO2 budgets for 1.5, 1.7 and 2.0 °C warming
- Created artifacts: Methodology description, CO2 budget table, bar chart comparing CO2 budgets to projected emissions of Heidelberg
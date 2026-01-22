# <img src="resources/info/icon.jpg" width="5%"> GHG Budget

The GHG Budget Tool calculates the CO₂ budget for the selected city or municipality that may be emitted in order to achieve the climate targets that were agreed at the COP 21 in Paris at the end of 2015.
The tool is currently limited to the following cities: Berlin, Bonn, Hamburg, Heidelberg, Karlsruhe.
However, it is to be extended to other cities in the future.

## Preparation

Use git to clone this repository to your computer.
Create a new branch by running git checkout -b <my_new_branch_name>.
After you have finished your implementation, you can create a merge request to the main branch that can be reviewed by the CA team.
We highly encourage you to create smaller intermediate MRs for review!

## Development setup

To run your plugin locally requires the following setup:

1. Set up the [infrastructure](https://gitlab.heigit.org/climate-action/infrastructure) locally in `devel` mode
2. Copy your [.env.base_template](.env.base_template) to `.env.base` and update it
3. Run `poetry run python ghg_budget/plugin.py`

### Testing

We use [pytest](pytest.org) as testing engine.
Ensure all tests are passing on the unmodified repository by running `poetry run pytest`.

#### Coverage

To get a coverage report of how much of your code is run during testing, execute
`poetry run pytest --ignore test/core/ --cov`.
We ignore the `test/core/` folder when assessing coverage because the core tests run the whole plugin to be sure
everything successfully runs with a very basic configuration.
Yet, they don't actually test functionality and therefore artificially inflate the test coverage results.

To get a more detailed report including which lines in each file are **not** tested,
run `poetry run pytest --ignore test/core/ --cov --cov-report term-missing`

### Linting and formatting

It is important that the code created by the different plugin developers adheres to a certain standard.
We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting the code as part of our pre-commit hooks.
Please activate pre-commit by running `poetry run pre-commit install`.
It will now run automatically before each commit and apply fixes for a variety of lint errors to your code.
Note that we have increased the maximum number of characters per line to be 120 to make better use of large modern displays.
If you want to keep short lines explicitly seperate (e.g. in the definition of functions or list) please use ["magic trailing commas"](https://docs.astral.sh/ruff/settings/#format_skip-magic-trailing-comma).

### Logging

Using the environment variable `LOG_Level` you can adjust the amount of log messages produced by the plugin.
Please make sure to use logging throughout your plugin.
This will make debugging easier at a later stage.

## Releasing a new plugin version

To release a new plugin version

1. Update the [CHANGELOG.md](CHANGELOG.md).
   It should already be up to date but give it one last read and update the heading above this upcoming release
2. Decide on the new version number.
   We suggest you adhere to the [Semantic Versioning](https://semver.org/) scheme, based on the changes since the last
   release.
   You can think of your plugin methods (info method, input parameters and artifacts) as the public API of your plugin.
3. Update the version attribute in the [pyproject.toml](pyproject.toml) (e.g. by running
   `poetry version {patch|minor|major}`)
4. Create a [release]((https://docs.gitlab.com/ee/user/project/releases/#create-a-release-in-the-releases-page)) on
   GitLab, including a changelog

## Docker



### Build

The tool is also [Dockerised](Dockerfile).
Images are automatically built and deployed in the [CI-pipeline](.gitlab-ci.yml).

In case you want to manually build and run locally (e.g. to test a new feature in development), execute


```shell
docker build . --tag repo.heigit.org/climate-action/ghg-budget:devel
```

Note that this will overwrite any existing image with the same tag (i.e. the one you previously pulled from the Climate
Action docker registry).

To mimic the build behaviour of the CI you have to add `--build-arg CI_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD)`
to the above command.

#### Canary

To build a canary version update your `climatoology` dependency declaration to point to the `main` branch and update
your lock file (`poetry update climatoology`).
Then run

```shell
docker build . \
  --build-arg CI_COMMIT_SHORT_SHA=$(git rev-parse --short HEAD) \
  --tag repo.heigit.org/climate-action/ghg-budget:canary \
  --push
```

### Run

If you have the Climate Infrastructure running (see [Development Setup](#development-setup)) you can now run the
container via

```shell
docker run --rm --network=host --env-file .env.base --env-file .env repo.heigit.org/climate-action/ghg-budget:devel
```

### Deploy

Deployment is handled by the GitLab CI automatically.
If for any reason you want to deploy manually (and have the required rights), after building the image, run

```shell
docker image push repo.heigit.org/climate-action/ghg-budget:devel
```

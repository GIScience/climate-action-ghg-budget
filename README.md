# <img src="resources/info/hourglass.jpg" width="5%"> GHG Budget

The GHG Budget Tool calculates the CO₂ budget for the selected city or municipality that may be emitted in order to achieve the climate targets that were agreed at the COP 21 in Paris at the end of 2015.
The demo version of the tool is initially limited to Heidelberg.
However, it is to be extended to other cities in the future.

## Preparation

Use git to clone this repository to your computer.
Create a new branch by running git checkout -b <my_new_branch_name>.
After you have finished your implementation, you can create a merge request to the main branch that can be reviewed by the CA team.
We highly encourage you to create smaller intermediate MRs for review!

### Python Environment

We use [poetry](https://python-poetry.org) as an environment management system.
Make sure you have it installed.
Apart from some base dependencies, there is only one fixed dependency for you, which is the [climatoology](https://gitlab.gistools.geog.uni-heidelberg.de/climate-action/climatoology) package that holds all the infrastructure functionality.
Make sure you have read-access to the climatoology repository (i.e. you can clone it).

Now run

```shell
poetry install --with dev,test
```

and you are ready to code within your poetry environment.

### Testing

We use [pytest](pytest.org) as testing engine.
Ensure all tests are passing on the unmodified repository by running `poetry run pytest`.

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

1. update the version attribute in the [pyproject.toml](pyproject.toml) (e.g. by running `poetry version {patch|minor|major}`)
2. update the version in the plugin `info` method
3. create a [release](https://docs.gitlab.com/ee/user/project/releases/) on GitLab, preferably including a changelog

Please adhere to the [Semantic Versioning](https://semver.org/) scheme.
You can think of the plugin methods (info method, input parameters and artifacts) as the public API of your plugin.

## Docker (for admins and interested devs)

If the infrastructure is reachable you can copy [.env_template](.env_template) to `.env` and then run

```shell
DOCKER_BUILDKIT=1 docker build --secret id=CI_JOB_TOKEN . --tag heigit/ca-ghg-budget:devel
docker run --env-file .env --network=host heigit/ca-ghg-budget:devel
```

Make sure the cone-token is copied to the text-file named `CI_JOB_TOKEN` that is mounted to the container build process as secret.

To deploy this plugin to the central docker repository run

```shell
DOCKER_BUILDKIT=1 docker build --secret id=CI_JOB_TOKEN . --tag heigit/ca-ghg-budget:devel
docker image push heigit/ca-ghg-budget:devel
```

## Kaniko

To test the docker build from Kaniko run

```shell
docker run -v ./:/workspace \
    -v ./CI_JOB_TOKEN:/kaniko/CI_JOB_TOKEN \
    gcr.io/kaniko-project/executor:v1.14.0-debug \
    --dockerfile /workspace/Dockerfile.Kaniko \
    --context dir:///workspace/ \
    --no-push
```

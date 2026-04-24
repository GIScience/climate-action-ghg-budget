FROM python:3.13-bookworm
SHELL ["/bin/bash", "-c"]

ARG CI_COMMIT_SHORT_SHA
ARG USER='plugin'
ENV PACKAGE_NAME='ghg_budget'

RUN useradd -ms /bin/bash $USER
USER $USER
ENV WD=/home/$USER
WORKDIR $WD

ENV POETRY_HOME="$WD/.cache/poetry"

RUN python3 -m venv $POETRY_HOME &&\
    $POETRY_HOME/bin/pip install poetry==2.*

ENV PATH="$PATH:$POETRY_HOME/bin"

COPY pyproject.toml poetry.lock ./


RUN poetry install --no-ansi --no-interaction --without dev,test --no-root

COPY $PACKAGE_NAME $PACKAGE_NAME
COPY --chown=$USER resources resources
COPY README.md ./README.md

# see https://github.com/python-babel/babel/issues/1268
RUN poetry run pybabel compile -d resources/locales; exit 0

RUN if [[ -n "${CI_COMMIT_SHORT_SHA}" ]]; then sed -E -i "s/^(version *= *\"[^+]*)\"/\\1+${CI_COMMIT_SHORT_SHA}\"/" pyproject.toml; fi;

RUN poetry install --no-ansi --no-interaction --only-root

ENTRYPOINT exec poetry run python ${PACKAGE_NAME}/plugin.py

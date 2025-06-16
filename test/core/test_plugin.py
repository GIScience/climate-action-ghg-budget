from climatoology.base.artifact import _Artifact
from climatoology.base.info import _Info


def test_plugin_info_request(operator):
    assert isinstance(operator.info(), _Info)


def test_plugin_compute_request(
    operator, expected_compute_input, compute_resources, default_aoi, default_aoi_properties
):
    computed_artifacts = operator.compute(
        resources=compute_resources,
        params=expected_compute_input,
        aoi=default_aoi,
        aoi_properties=default_aoi_properties,
    )
    assert len(computed_artifacts) == 6
    for artifact in computed_artifacts:
        assert isinstance(artifact, _Artifact)

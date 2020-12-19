import pkg_resources
import yaml


def get_refinement_test_data(series: int, inout: str) -> dict:
    filename: str = f"{series}.{inout}.yaml"
    stream = pkg_resources.resource_stream(
        "test_hootingyard.refinement_test_data", filename
    )
    return yaml.safe_load(stream)

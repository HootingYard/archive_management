import pprint
import textwrap

import openai

from hootingyard.config.config import get_config


def list_models():
    pprint.pprint(openai.FineTune.list())

if __name__ == "__main__":
    openai.api_key = get_config().openai_api_key
    list_models()
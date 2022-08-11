import pprint

import openai

from hootingyard.config.config import get_config

FINE_TUNE_MODEL_ID:str = 'curie:ft-team-rocket-ltd-2022-08-07-23-41-39'

def main():
    openai.FineTune.create()


def list_models():
    pprint.pprint(openai.FineTune.list())

if __name__ == "__main__":
    openai.api_key = get_config().openai_api_key
    main()
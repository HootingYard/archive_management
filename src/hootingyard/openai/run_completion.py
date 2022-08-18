import pprint
import textwrap

import openai

from hootingyard.config.config import get_config

# FINE_TUNE_MODEL_ID:str = 'ft-gWvovsDUGkvgKKrkJKz1s2db' # shorter dobson stories
# FINE_TUNE_MODEL_ID:str = "ft-3cdXuorPNCYSBM4WYUjEptC2" # all shorter stories
FINE_TUNE_MODEL_ID:str = 'davinci:ft-team-rocket-ltd-2022-08-10-23-16-36'

def main():
    result = openai.Completion.create(
        model=FINE_TUNE_MODEL_ID,
        prompt="Did Dobson really exist?\n",
        max_tokens=1024,
        temperature=0.90,
        n=1,
    )
    pprint.pprint(result)

    for choice in result["choices"]:
        for paragraph in choice["text"].partition("###")[0].split("\n"):
            print("\n")
            for line in textwrap.wrap(paragraph.strip()):
                print(line)


def list_models():
    pprint.pprint(openai.FineTune.list())

if __name__ == "__main__":
    openai.api_key = get_config().openai_api_key
    main()
import os

import yaml

def here(f, *args):
    """
    Get the absolute path of the current file.
    """
    return os.path.join(os.path.dirname(f), *args)

AHS_ACS_MAPPING = yaml.load(open(here(__file__, 'ahs-acs.yaml')))

AHS_FILEPATH = here(__file__, 'data/ahs.csv')
AHS_ADD_VARS = [
    "control",
    "smsa",
    "county",
    "metro3",
    "battery",
    "smoke"
]

ACS_FILEPATH = here(__file__, 'data/acs.csv')
ACS_JOIN_VAR = 'geoid'
ACS_SETUP_QUERIES = [
    'set search_path to acs2013_5yr'
]

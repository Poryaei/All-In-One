import json
import os


def getenv_json_config(str):
    return os.getenv(str) if os.getenv(str) else data[str]


with open('config.json') as f:
    data = json.load(f)
    api_id = getenv_json_config('api_id')
    api_hash = getenv_json_config('api_hash')
    sessionString = getenv_json_config('sessionString')
    admin = getenv_json_config('admin')
    version = getenv_json_config('version')
    auto_upgrade = getenv_json_config('auto_upgrade')
    max_tap_level = getenv_json_config('max_tap_level')
    max_charge_level = getenv_json_config('max_charge_level')
    max_energy_level = getenv_json_config('max_energy_level')
    max_days_for_return = getenv_json_config('max_days_for_return')
    cexio_clicker = getenv_json_config('cexio_clicker')
    tapswap_clicker = getenv_json_config('tapswap_clicker')
    hamster_clicker = getenv_json_config('hamster_clicker')
    cexio_ref_code = getenv_json_config('cexio_ref_code')

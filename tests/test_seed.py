import json
from pathlib import Path
from backend.app.main import validate_seed_payload

def test_seed_has_four_campaigns_and_thirty_scenarios():
    payload=json.loads((Path(__file__).parents[1]/'seed_data'/'campaigns.json').read_text(encoding='utf-8'))
    assert len(payload)==4
    assert sum(len(c['scenarios']) for c in payload)==30
    assert sum(len(s['choices']) for c in payload for s in c['scenarios'])==120
    validate_seed_payload(payload)

def test_all_scenario_ids_are_unique():
    payload=json.loads((Path(__file__).parents[1]/'seed_data'/'campaigns.json').read_text(encoding='utf-8'))
    ids=[s['code'] for c in payload for s in c['scenarios']]
    assert len(ids)==len(set(ids))==30

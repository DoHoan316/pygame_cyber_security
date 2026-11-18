import json
from pathlib import Path
from .main import validate_seed_payload
p=Path(__file__).resolve().parents[2]/'seed_data'/'campaigns.json'
data=json.loads(p.read_text(encoding='utf-8'))
validate_seed_payload(data)
print(f'OK: {len(data)} campaigns, {sum(len(c["scenarios"]) for c in data)} scenarios, {sum(len(s["choices"]) for c in data for s in c["scenarios"])} choices')
for c in data: print(f'- {c["code"]}: {len(c["scenarios"])} scenarios')

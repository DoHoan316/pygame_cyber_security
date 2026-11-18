"""Manual integration smoke test. Run with a fresh local DB and admin env vars."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from backend.app.main import app

def run():
    with TestClient(app) as client:
        assert client.get('/api/health').status_code==200
        reg=client.post('/api/auth/register',json={'email':'smoke.player@example.com','password':'PlayerPass123!','display_name':'Smoke Player'})
        assert reg.status_code==201,reg.text
        token=reg.json()['data']['access_token']; headers={'Authorization':f'Bearer {token}'}
        camps=client.get('/api/campaigns',headers=headers).json()['data']
        assert len(camps)==4
        start=client.post('/api/game/sessions',headers=headers,json={'campaign_id':camps[0]['id']})
        assert start.status_code==200,start.text
        session=start.json()['data']
        while session['status']!='COMPLETED':
            if session['status']=='PLAYING':
                sc=session['current_scenario']; choice=next((x for x in sc['choices'] if x['code']=='B'),sc['choices'][0])
                selected=client.post(f"/api/game/sessions/{session['id']}/choices",headers=headers,json={'scenario_id':sc['id'],'choice_id':choice['id']})
                assert selected.status_code==200,selected.text
                session=selected.json()['data']
                resumed=client.get(f"/api/game/sessions/{session['id']}",headers=headers).json()['data']
                assert resumed['status']=='FEEDBACK' and resumed['feedback']
                session=client.post(f"/api/game/sessions/{session['id']}/continue",headers=headers,json={}).json()['data']
        assert client.get(f"/api/game/sessions/{session['id']}/result",headers=headers).status_code==200
        assert client.get('/api/admin/analytics/overview',headers=headers).status_code==403
        print('PASS: health, register, campaigns, session, choice, feedback resume, completion, result, RBAC')
if __name__=='__main__': run()

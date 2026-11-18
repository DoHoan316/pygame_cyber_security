import os, json
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, desc
from sqlalchemy.exc import IntegrityError
from .database import Base, engine, get_db, SessionLocal
from .models import User, Campaign, Scenario, Choice, GameSession, ChoiceHistory
from .security import hash_password, verify_password, create_access_token, current_user, admin_user
from fastapi.middleware.cors import CORSMiddleware
@asynccontextmanager
async def lifespan(app):
    with SessionLocal() as db:
        seed_database(db)
        admin_email=os.getenv('ADMIN_EMAIL'); admin_password=os.getenv('ADMIN_PASSWORD')
        if admin_email and admin_password and not db.query(User).filter(User.email==admin_email.lower()).first():
            db.add(User(email=admin_email.lower(),password_hash=hash_password(admin_password),display_name='Quản trị viên',role='Admin'));db.commit()
    yield

app=FastAPI(title='CyberSafe API',version='3.0.0',description='Backend chiến dịch mô phỏng an toàn thông tin',lifespan=lifespan)

PROJECT_DIR = Path(__file__).resolve().parents[2]
ARCHIVES_DIR = PROJECT_DIR / 'archives'

app.mount('/app', StaticFiles(directory=PROJECT_DIR / 'admin_web', html=True), name='webapp')
app.mount('/archives', StaticFiles(directory=ARCHIVES_DIR), name='archives')
origins=os.getenv('CORS_ORIGINS','http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000').split(',')
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in origins],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

class RegisterIn(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)
    display_name:str=Field(min_length=2,max_length=80)
class LoginIn(BaseModel):
    email:EmailStr
    password:str=Field(min_length=1,max_length=128)
class StartIn(BaseModel): campaign_id:int
class ChoiceIn(BaseModel): scenario_id:int; choice_id:int
class StatusIn(BaseModel): is_active:bool

def ok(data,message='Thành công'):
    return {'success':True,'message':message,'data':data}
def fail(message,code='INVALID_REQUEST',details=None):
    return {'success':False,'message':message,'error_code':code,'details':details or {}}
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request:Request, exc:RequestValidationError):
    from fastapi.responses import JSONResponse
    details=[{'field':'.'.join(str(x) for x in e.get('loc',[])),'message':e.get('msg','Invalid value')} for e in exc.errors()]
    return JSONResponse(status_code=422,content=fail('Dữ liệu gửi lên không hợp lệ','INVALID_INPUT',{'errors':details}))

@app.exception_handler(HTTPException)
async def http_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=exc.status_code,content=fail(str(exc.detail),{400:'INVALID_INPUT',401:'UNAUTHORIZED',403:'FORBIDDEN',404:'NOT_FOUND',409:'CONFLICT'}.get(exc.status_code,'REQUEST_FAILED')))

def validate_seed_payload(payload):
    codes={c['code'] for c in payload}
    for camp in payload:
        nodes=camp['scenarios']; by={n['code']:n for n in nodes}
        starts=[n for n in nodes if n['is_start']]
        if len(starts)!=1: raise ValueError(f"{camp['code']}: cần đúng một start node")
        for n in nodes:
            if not 2<=len(n['choices'])<=4: raise ValueError(f"{n['code']}: số lựa chọn không hợp lệ")
            for ch in n['choices']:
                if not ch['choice_text'] or not ch['consequence_text'] or not ch['explanation_text']:
                    raise ValueError(f"{n['code']}: thiếu nội dung choice")
                nxt=ch.get('next_scenario_code')
                if nxt and nxt not in by: raise ValueError(f"{n['code']}: nhánh {nxt} không thuộc campaign")
        # Every node reachable from start; all edges move within the same campaign.
        seen=set(); stack=[starts[0]['code']]
        while stack:
            code=stack.pop()
            if code in seen: continue
            seen.add(code)
            for ch in by[code]['choices']:
                if ch.get('next_scenario_code'): stack.append(ch['next_scenario_code'])
        if seen!=set(by): raise ValueError(f"{camp['code']}: node không thể đi tới: {set(by)-seen}")
        # Since each transition is expected to be acyclic, verify no cycles and every route terminates.
        visiting=set(); done=set()
        def visit(code):
            if code in visiting: raise ValueError(f"{camp['code']}: phát hiện vòng lặp tại {code}")
            if code in done:return
            visiting.add(code)
            for ch in by[code]['choices']:
                nxt=ch.get('next_scenario_code')
                if nxt: visit(nxt)
            visiting.remove(code);done.add(code)
        visit(starts[0]['code'])

def seed_database(db:Session):
    path=Path(__file__).resolve().parents[2]/'seed_data'/'campaigns.json'
    if not path.exists(): return
    payload=json.loads(path.read_text(encoding='utf-8')); validate_seed_payload(payload)
    if db.query(Campaign).count(): return
    for item in payload:
        campaign=Campaign(code=item['code'],title=item['title'],description=item['description'],topic=item['topic'],order_no=item['order_no'],is_active=True)
        db.add(campaign); db.flush()
        scenario_map={}
        for n in item['scenarios']:
            obj=Scenario(campaign_id=campaign.id,code=n['code'],title=n['title'],body=n['body'],learning_objective=n['learning_objective'],cia_dimension=n['cia_dimension'],is_start=n['is_start'])
            db.add(obj);db.flush();scenario_map[n['code']]=obj
        for n in item['scenarios']:
            obj=scenario_map[n['code']]
            for ch in n['choices']:
                db.add(Choice(scenario_id=obj.id,code=ch['code'],choice_text=ch['choice_text'],consequence_text=ch['consequence_text'],explanation_text=ch['explanation_text'],safety_points=ch['safety_points'],risk_points=ch['risk_points'],error_category=ch['error_category'],next_scenario_id=scenario_map[ch['next_scenario_code']].id if ch.get('next_scenario_code') else None))
    db.commit()

def score_session(s):
    total=s.total_safety_points+s.total_risk_points
    s.safety_score=round(s.total_safety_points/total*100,2) if total else 0.0
    s.risk_score=round(s.total_risk_points/total*100,2) if total else 0.0

def rank_for(score):
    if score>=90:return 'Chuyên gia an toàn'
    if score>=75:return 'Người dùng cảnh giác'
    if score>=50:return 'Đang tiến bộ'
    return 'Cần rèn luyện thêm'

def session_payload(db,s):
    scenario=db.query(Scenario).options(joinedload(Scenario.choices)).filter(Scenario.id==s.current_scenario_id).first()
    pending=None
    if s.status=='FEEDBACK' and s.pending_history_id:
        h=db.get(ChoiceHistory,s.pending_history_id); ch=db.get(Choice,h.choice_id) if h else None
        if ch: pending={'choice_id':ch.id,'choice_code':ch.code,'consequence':ch.consequence_text,'explanation':ch.explanation_text,'safety_points':ch.safety_points,'risk_points':ch.risk_points,'error_category':ch.error_category}
    return {'id':s.id,'campaign_id':s.campaign_id,'status':s.status,'current_scenario':None if s.status=='COMPLETED' else {'id':scenario.id,'code':scenario.code,'title':scenario.title,'body':scenario.body,'learning_objective':scenario.learning_objective,'cia_dimension':scenario.cia_dimension,'choices':[{'id':c.id,'code':c.code,'text':c.choice_text} for c in sorted(scenario.choices,key=lambda x:x.code)]},'feedback':pending,'decision_count':s.decision_count,'safety_score':s.safety_score,'risk_score':s.risk_score}

@app.get('/')
def root():return ok({'name':'CyberSafe','version':'3.0.0','docs':'/docs'})
@app.get('/api/health')
def health(db:Session=Depends(get_db)):
    db.execute(select(1));return ok({'status':'healthy','database':'connected'})

@app.post('/api/auth/register',status_code=201)
def register(data:RegisterIn,db:Session=Depends(get_db)):
    email=data.email.lower().strip()
    if db.query(User).filter(User.email==email).first():raise HTTPException(409,'Email đã được sử dụng')
    user=User(email=email,password_hash=hash_password(data.password),display_name=data.display_name.strip(),role='Player')
    db.add(user)
    try:db.commit();db.refresh(user)
    except IntegrityError:db.rollback();raise HTTPException(409,'Email đã được sử dụng')
    token=create_access_token(user)
    return ok({'access_token':token,'token_type':'bearer','user':{'id':user.id,'email':user.email,'display_name':user.display_name,'role':user.role}},'Đăng ký thành công')
@app.post('/api/auth/login')
def login(data:LoginIn,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==data.email.lower().strip()).first()
    if not user or not verify_password(data.password,user.password_hash):raise HTTPException(401,'Email hoặc mật khẩu không chính xác')
    if not user.is_active:raise HTTPException(403,'Tài khoản đã bị vô hiệu hóa')
    return ok({'access_token':create_access_token(user),'token_type':'bearer','user':{'id':user.id,'email':user.email,'display_name':user.display_name,'role':user.role}},'Đăng nhập thành công')
@app.get('/api/auth/me')
def me(user:User=Depends(current_user)):
    return ok({'id':user.id,'email':user.email,'display_name':user.display_name,'role':user.role,'is_active':user.is_active})

@app.get('/api/campaigns')
def campaigns(db:Session=Depends(get_db),user:User=Depends(current_user)):
    rows=db.query(Campaign).filter(Campaign.is_active==True).order_by(Campaign.order_no).all();out=[]
    for c in rows:
        count=db.query(Scenario).filter(Scenario.campaign_id==c.id).count()
        active=db.query(GameSession).filter(GameSession.user_id==user.id,GameSession.campaign_id==c.id,GameSession.status!='COMPLETED').first()
        completed=db.query(GameSession).filter(GameSession.user_id==user.id,GameSession.campaign_id==c.id,GameSession.status=='COMPLETED').count()
        out.append({'id':c.id,'code':c.code,'title':c.title,'description':c.description,'topic':c.topic,'scenario_count':count,'active_session_id':active.id if active else None,'completed_attempts':completed})
    return ok(out)
@app.get('/api/campaigns/{campaign_id}')
def campaign_detail(campaign_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    c=db.get(Campaign,campaign_id)
    if not c or not c.is_active:raise HTTPException(404,'Không tìm thấy chiến dịch')
    return ok({'id':c.id,'code':c.code,'title':c.title,'description':c.description,'topic':c.topic,'scenario_count':db.query(Scenario).filter(Scenario.campaign_id==c.id).count()})

@app.post('/api/game/sessions')
def start_session(data:StartIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    c=db.get(Campaign,data.campaign_id)
    if not c or not c.is_active:raise HTTPException(404,'Chiến dịch không tồn tại')
    existing=db.query(GameSession).filter(GameSession.user_id==user.id,GameSession.campaign_id==c.id,GameSession.status.in_(['PLAYING','FEEDBACK'])).first()
    if existing:return ok(session_payload(db,existing),'Tiếp tục phiên đang chơi')
    start=db.query(Scenario).filter(Scenario.campaign_id==c.id,Scenario.is_start==True).first()
    if not start:raise HTTPException(500,'Chiến dịch chưa có tình huống bắt đầu')
    s=GameSession(user_id=user.id,campaign_id=c.id,current_scenario_id=start.id,status='PLAYING');db.add(s);db.commit();db.refresh(s)
    return ok(session_payload(db,s),'Đã bắt đầu chiến dịch')
@app.get('/api/game/sessions/{session_id}')
def get_session(session_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.get(GameSession,session_id)
    if not s or s.user_id!=user.id:raise HTTPException(404,'Không tìm thấy phiên chơi')
    return ok(session_payload(db,s))
@app.post('/api/game/sessions/{session_id}/choices')
def submit_choice(session_id:int,data:ChoiceIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.query(GameSession).filter(GameSession.id==session_id,GameSession.user_id==user.id).with_for_update().first()
    if not s:raise HTTPException(404,'Không tìm thấy phiên chơi')
    if s.status!='PLAYING':raise HTTPException(409,'Phiên không ở trạng thái nhận lựa chọn')
    if s.current_scenario_id!=data.scenario_id:raise HTTPException(409,'Tình huống hiện tại đã thay đổi')
    ch=db.query(Choice).filter(Choice.id==data.choice_id,Choice.scenario_id==data.scenario_id).first()
    if not ch:raise HTTPException(400,'Lựa chọn không thuộc tình huống hiện tại')
    step=s.decision_count+1
    if db.query(ChoiceHistory).filter(ChoiceHistory.session_id==s.id,ChoiceHistory.step_no==step).first():raise HTTPException(409,'Lựa chọn đã được ghi nhận')
    h=ChoiceHistory(session_id=s.id,step_no=step,scenario_id=data.scenario_id,choice_id=ch.id,safety_points=ch.safety_points,risk_points=ch.risk_points,error_category=ch.error_category)
    db.add(h);db.flush()
    s.total_safety_points+=ch.safety_points;s.total_risk_points+=ch.risk_points;s.decision_count=step
    s.pending_next_scenario_id=ch.next_scenario_id;s.pending_history_id=h.id;s.status='FEEDBACK';score_session(s)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,'Lựa chọn đã được ghi nhận ở một yêu cầu khác')
    db.refresh(s)
    return ok(session_payload(db,s),'Đã ghi nhận lựa chọn')
@app.post('/api/game/sessions/{session_id}/continue')
def continue_session(session_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.query(GameSession).filter(GameSession.id==session_id,GameSession.user_id==user.id).with_for_update().first()
    if not s:raise HTTPException(404,'Không tìm thấy phiên chơi')
    if s.status!='FEEDBACK':raise HTTPException(409,'Phiên không ở trạng thái feedback')
    nxt=s.pending_next_scenario_id;s.pending_next_scenario_id=None;s.pending_history_id=None
    if nxt is None:
        s.status='COMPLETED';s.completed_at=datetime.now(timezone.utc)
    else:
        s.current_scenario_id=nxt;s.status='PLAYING'
    score_session(s);db.commit();db.refresh(s)
    return ok(session_payload(db,s),'Chiến dịch đã hoàn thành' if s.status=='COMPLETED' else 'Tiếp tục chiến dịch')
@app.get('/api/game/sessions/{session_id}/result')
def result(session_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    s=db.get(GameSession,session_id)
    if not s or s.user_id!=user.id:raise HTTPException(404,'Không tìm thấy phiên chơi')
    if s.status!='COMPLETED':raise HTTPException(409,'Chiến dịch chưa hoàn thành')
    return ok({'session_id':s.id,'campaign_id':s.campaign_id,'status':s.status,'decision_count':s.decision_count,'total_safety_points':s.total_safety_points,'total_risk_points':s.total_risk_points,'safety_score':s.safety_score,'risk_score':s.risk_score,'rank':rank_for(s.safety_score),'completed_at':s.completed_at.isoformat() if s.completed_at else None})

@app.get('/api/me/dashboard')
def player_dashboard(db:Session=Depends(get_db),user:User=Depends(current_user)):
    sessions=db.query(GameSession).filter(GameSession.user_id==user.id).all();completed=[s for s in sessions if s.status=='COMPLETED']
    errors=db.query(ChoiceHistory.error_category,func.count(ChoiceHistory.id)).join(GameSession,ChoiceHistory.session_id==GameSession.id).filter(GameSession.user_id==user.id,ChoiceHistory.error_category.isnot(None)).group_by(ChoiceHistory.error_category).all()
    return ok({'campaigns_completed':len({s.campaign_id for s in completed}),'sessions_completed':len(completed),'sessions_in_progress':sum(s.status!='COMPLETED' for s in sessions),'average_safety_score':round(sum(s.safety_score for s in completed)/len(completed),2) if completed else 0,'best_safety_score':max((s.safety_score for s in completed),default=0),'error_groups':[{'category':k,'count':v} for k,v in errors]})
@app.get('/api/me/history')
def player_history(db:Session=Depends(get_db),user:User=Depends(current_user)):
    rows=db.query(GameSession).filter(GameSession.user_id==user.id).order_by(GameSession.created_at.desc()).limit(100).all()
    return ok([{'session_id':s.id,'campaign':db.get(Campaign,s.campaign_id).title,'status':s.status,'safety_score':s.safety_score,'risk_score':s.risk_score,'decision_count':s.decision_count,'created_at':s.created_at.isoformat(),'completed_at':s.completed_at.isoformat() if s.completed_at else None} for s in rows])
@app.get('/api/me/errors')
def player_errors(db:Session=Depends(get_db),user:User=Depends(current_user)):
    rows=db.query(ChoiceHistory.error_category,func.count(ChoiceHistory.id)).join(GameSession,ChoiceHistory.session_id==GameSession.id).filter(GameSession.user_id==user.id,ChoiceHistory.error_category.isnot(None)).group_by(ChoiceHistory.error_category).order_by(desc(func.count(ChoiceHistory.id))).all()
    return ok([{'error_category':k,'count':v} for k,v in rows])
@app.get('/api/leaderboard/{campaign_id}')
def leaderboard(campaign_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if not db.get(Campaign,campaign_id):raise HTTPException(404,'Chiến dịch không tồn tại')
    rows=db.query(GameSession,User).join(User,User.id==GameSession.user_id).filter(GameSession.campaign_id==campaign_id,GameSession.status=='COMPLETED').order_by(GameSession.safety_score.desc(),GameSession.risk_score.asc(),GameSession.completed_at.asc()).all()
    best={}
    for s,u in rows:
        if u.id not in best:best[u.id]={'display_name':u.display_name,'safety_score':s.safety_score,'risk_score':s.risk_score,'completed_at':s.completed_at.isoformat() if s.completed_at else None}
    return ok(sorted(best.values(),key=lambda x:(-x['safety_score'],x['risk_score'],x['completed_at'] or ''))[:10])

@app.get('/api/admin/users')
def admin_users(q:str='',offset:int=0,limit:int=50,db:Session=Depends(get_db),admin:User=Depends(admin_user)):
    query=db.query(User)
    if q:query=query.filter((User.email.ilike(f'%{q}%'))|(User.display_name.ilike(f'%{q}%')))
    total=query.count();users=query.order_by(User.created_at.desc()).offset(max(offset,0)).limit(min(max(limit,1),100)).all()
    return ok({'total':total,'items':[{'id':u.id,'email':u.email,'display_name':u.display_name,'role':u.role,'is_active':u.is_active,'created_at':u.created_at.isoformat()} for u in users]})
@app.get('/api/admin/users/{user_id}')
def admin_user_detail(user_id:int,db:Session=Depends(get_db),admin:User=Depends(admin_user)):
    u=db.get(User,user_id)
    if not u:raise HTTPException(404,'Không tìm thấy người dùng')
    return ok({'id':u.id,'email':u.email,'display_name':u.display_name,'role':u.role,'is_active':u.is_active,'created_at':u.created_at.isoformat()})
@app.patch('/api/admin/users/{user_id}/status')
def admin_user_status(user_id:int,data:StatusIn,db:Session=Depends(get_db),admin:User=Depends(admin_user)):
    u=db.get(User,user_id)
    if not u:raise HTTPException(404,'Không tìm thấy người dùng')
    if u.id==admin.id and not data.is_active:raise HTTPException(400,'Không thể tự vô hiệu hóa tài khoản đang đăng nhập')
    u.is_active=data.is_active;db.commit();return ok({'id':u.id,'is_active':u.is_active},'Đã cập nhật trạng thái tài khoản')
@app.get('/api/admin/analytics/overview')
def admin_overview(db:Session=Depends(get_db),admin:User=Depends(admin_user)):
    total_users=db.query(User).count();active_users=db.query(User).filter(User.is_active==True).count()
    total_sessions=db.query(GameSession).count();completed=db.query(GameSession).filter(GameSession.status=='COMPLETED').count()
    avg=db.query(func.avg(GameSession.safety_score)).filter(GameSession.status=='COMPLETED').scalar() or 0
    campaign_stats=[]
    for c in db.query(Campaign).order_by(Campaign.order_no):
        total=db.query(GameSession).filter(GameSession.campaign_id==c.id).count();done=db.query(GameSession).filter(GameSession.campaign_id==c.id,GameSession.status=='COMPLETED').count()
        campaign_stats.append({'campaign':c.title,'sessions':total,'completed':done})
    errors=db.query(ChoiceHistory.error_category,func.count(ChoiceHistory.id)).filter(ChoiceHistory.error_category.isnot(None)).group_by(ChoiceHistory.error_category).order_by(desc(func.count(ChoiceHistory.id))).all()
    return ok({'users_total':total_users,'users_active':active_users,'sessions_total':total_sessions,'sessions_completed':completed,'completion_rate':round(completed/total_sessions*100,2) if total_sessions else 0,'average_safety_score':round(float(avg),2),'campaigns':campaign_stats,'common_errors':[{'category':k,'count':v} for k,v in errors]})

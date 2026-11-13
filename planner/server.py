"""Small private HTTP app. Put behind an HTTPS reverse proxy for remote use."""
import argparse
import hashlib
import hmac
import json
import logging
import os
import secrets
import threading
import time
from datetime import datetime
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
from zoneinfo import ZoneInfo
from .store import Store

STATIC=Path(__file__).resolve().parent.parent/'static'

def make_server(store,password,host='127.0.0.1',port=8000,secure=False):
    sessions={}; failures={}; lock=threading.Lock()
    salt=secrets.token_bytes(16)
    digest=hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1)
    class Handler(BaseHTTPRequestHandler):
        server_version='DinnerPlanner'
        def log_message(self,fmt,*args): logging.info('%s %s',self.address_string(),fmt % args)
        def send(self,status,data,ctype='application/json; charset=utf-8',cookie=None):
            raw=json.dumps(data,ensure_ascii=False).encode() if ctype.startswith('application/json') else data
            self.send_response(status)
            self.send_header('Content-Type',ctype)
            self.send_header('Content-Length',str(len(raw)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Referrer-Policy','same-origin')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
            if cookie: self.send_header('Set-Cookie',cookie)
            self.end_headers(); self.wfile.write(raw)
        def session(self):
            try:
                cookie=SimpleCookie(self.headers.get('Cookie',''))
                token=cookie['planner_session'].value if 'planner_session' in cookie else ''
            except Exception: return None
            with lock:
                record=sessions.get(token)
                if record and record['expires']>time.time(): return record
                sessions.pop(token,None)
            return None
        def body(self):
            if self.headers.get('Content-Type','').split(';')[0]!='application/json': raise ValueError('Send JSON.')
            try: size=int(self.headers.get('Content-Length','0'))
            except ValueError: raise ValueError('Invalid request length.')
            if not 0<size<=100000: raise ValueError('Request body must be under 100 KB.')
            try: value=json.loads(self.rfile.read(size))
            except (ValueError,UnicodeDecodeError): raise ValueError('Invalid JSON.')
            if not isinstance(value,dict): raise ValueError('Expected a JSON object.')
            return value
        def do_GET(self):
            route=urlsplit(self.path)
            if route.path.startswith('/api/'):
                session=self.session()
                if not session: return self.send(401,{'error':'Please unlock your planner.'})
                try:
                    if route.path=='/api/state':
                        result=store.state(parse_qs(route.query).get('start',[None])[0]); result['csrf']=session['csrf']; result['today']=datetime.now(ZoneInfo('America/Detroit')).date().isoformat()
                        return self.send(200,result)
                    if route.path=='/api/history': return self.send(200,store.history())
                    return self.send(404,{'error':'Not found.'})
                except ValueError as error: return self.send(400,{'error':str(error)})
                except Exception:
                    logging.exception('Read failed'); return self.send(500,{'error':'Unable to load data. Saved records are retained.'})
            files={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
            name=files.get(route.path)
            if not name: return self.send(404,{'error':'Not found.'})
            ctype={'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[name.rsplit('.',1)[1]]
            self.send(200,(STATIC/name).read_bytes(),ctype)
        def do_POST(self):
            route=urlsplit(self.path).path
            origin=self.headers.get('Origin')
            expected=('https' if secure else 'http')+'://'+self.headers.get('Host','')
            if origin and origin!=expected: return self.send(403,{'error':'Cross-origin request blocked.'})
            try:
                data=self.body()
                if route=='/api/login':
                    key=self.client_address[0]
                    with lock:
                        attempts=[t for t in failures.get(key,[]) if t>time.time()-300]
                        failures[key]=attempts
                        if len(attempts)>=10: return self.send(429,{'error':'Too many attempts. Try again in five minutes.'})
                    candidate=data.get('password','')
                    if not isinstance(candidate,str) or len(candidate)>1024: raise ValueError('Invalid password.')
                    check=hashlib.scrypt(candidate.encode(),salt=salt,n=16384,r=8,p=1)
                    if not hmac.compare_digest(check,digest):
                        with lock: failures[key].append(time.time())
                        return self.send(401,{'error':'Incorrect planner password.'})
                    token=secrets.token_urlsafe(32); csrf=secrets.token_urlsafe(32)
                    with lock:
                        for old in list(sessions):
                            if sessions[old]['expires']<time.time(): sessions.pop(old)
                        sessions[token]={'csrf':csrf,'expires':time.time()+86400}
                        failures.pop(key,None)
                    return self.send(200,{'csrf':csrf},cookie=f'planner_session={token}; HttpOnly; SameSite=Strict; Path=/; Max-Age=86400'+('; Secure' if secure else ''))
                session=self.session()
                if not session: return self.send(401,{'error':'Please unlock your planner.'})
                if not hmac.compare_digest(self.headers.get('X-CSRF-Token',''),session['csrf']): return self.send(403,{'error':'Security token expired. Refresh and try again.'})
                if route=='/api/logout':
                    session['expires']=0
                    return self.send(200,{'ok':True},cookie='planner_session=; HttpOnly; SameSite=Strict; Path=/; Max-Age=0'+('; Secure' if secure else ''))
                if route=='/api/recipes': result=store.save_recipe(data)
                elif route=='/api/archive': store.archive(data.get('id')); result={'ok':True}
                elif route=='/api/generate':
                    if not isinstance(data.get('replace',False),bool): raise ValueError('Invalid replacement option.')
                    store.plan(data.get('start'),data.get('replace',False)); result={'ok':True}
                elif route=='/api/meal': store.change_meal(data.get('start'),data.get('date'),data.get('recipe_id'),data.get('special')); result={'ok':True}
                elif route=='/api/groceries': store.grocery(data.get('start'),data.get('edits')); result={'ok':True}
                elif route=='/api/settings': store.season(data.get('season')); result={'ok':True}
                else: return self.send(404,{'error':'Not found.'})
                self.send(200,result)
            except (ValueError,TypeError,KeyError) as error: self.send(400,{'error':str(error)})
            except Exception:
                logging.exception('Write failed'); self.send(500,{'error':'Unable to save. Your previous data is retained; please retry.'})
    return ThreadingHTTPServer((host,port),Handler)

def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser(description='Diesel Designs Dinner Planner')
    parser.add_argument('--host',default='127.0.0.1'); parser.add_argument('--port',type=int,default=8000)
    parser.add_argument('--db',default=os.environ.get('PLANNER_DB','/workspace/private/planner/planner.sqlite3'))
    parser.add_argument('--backup',help='Create and verify a database backup, then exit.')
    args=parser.parse_args()
    store=Store(args.db)
    if args.backup:
        if Path(args.backup).exists(): parser.error('Backup target already exists; choose a new path.')
        store.backup(args.backup); print('Database backup verified.'); return
    password=os.environ.get('PLANNER_PASSWORD')
    password_file=os.environ.get('PLANNER_PASSWORD_FILE')
    if password_file: password=Path(password_file).read_text().strip()
    if not password or len(password)<12: parser.error('Set PLANNER_PASSWORD or PLANNER_PASSWORD_FILE to a password of at least 12 characters.')
    logging.basicConfig(level=logging.INFO)
    server=make_server(store,password,args.host,args.port,os.environ.get('PLANNER_SECURE_COOKIE')=='1')
    logging.info('Dinner planner listening on %s:%d',args.host,args.port)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()

if __name__=='__main__': main()

import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from planner.store import Store
from planner.server import make_server

class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.server=make_server(Store(Path(self.tmp.name)/'db.sqlite3'),'test-password-12345',port=0)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.addCleanup(self.shutdown)
        self.cookie='';self.csrf=''
    def shutdown(self):self.server.shutdown();self.server.server_close();self.thread.join()
    def req(self,path,data=None,headers=None):
        con=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        h={'Content-Type':'application/json','Cookie':self.cookie,'X-CSRF-Token':self.csrf};h.update(headers or {})
        con.request('GET' if data is None else 'POST',path,body=None if data is None else json.dumps(data),headers=h)
        r=con.getresponse();status=r.status;head=dict(r.getheaders());raw=r.read();con.close()
        return status,json.loads(raw) if head.get('Content-Type','').startswith('application/json') else raw,head
    def login(self):
        status,data,headers=self.req('/api/login',{'password':'test-password-12345'});self.assertEqual(status,200)
        self.cookie=headers['Set-Cookie'].split(';')[0];self.csrf=data['csrf']
        self.assertIn('HttpOnly',headers['Set-Cookie']);self.assertIn('SameSite=Strict',headers['Set-Cookie'])
    def test_access_csrf_origin_static_boundaries_logout(self):
        self.assertEqual(self.req('/api/state')[0],401)
        self.assertEqual(self.req('/api/generate',{'start':'2026-11-14'})[0],401)
        self.assertEqual(self.req('/api/login',{'password':'wrong'})[0],401)
        self.login()
        self.assertEqual(self.req('/api/generate',{'start':'2026-11-14'},{'X-CSRF-Token':'bad'})[0],403)
        self.assertEqual(self.req('/api/generate',{'start':'2026-11-14'},{'Origin':'https://evil.test'})[0],403)
        self.assertEqual(self.req('/api/generate',{'start':'2026-11-14'})[0],200)
        status,data,_=self.req('/api/state?start=2026-11-14');self.assertEqual(len(data['meals']),14)
        for path in ['/../planner/seed.json','/planner.sqlite3','/.git/config','/backups/before-build.tar.gz']:
            self.assertEqual(self.req(path)[0],404)
        _,_,headers=self.req('/');self.assertIn("script-src 'self'",headers['Content-Security-Policy'])
        self.assertEqual(self.req('/api/logout',{})[0],200);self.assertEqual(self.req('/api/state')[0],401)
    def test_login_rate_limit(self):
        for _ in range(10):self.assertEqual(self.req('/api/login',{'password':'wrong'})[0],401)
        self.assertEqual(self.req('/api/login',{'password':'wrong'})[0],429)

if __name__=='__main__':unittest.main()

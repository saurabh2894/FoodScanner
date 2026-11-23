"""Deterministic cross-input provenance. Reader results are mocked, not real OCR."""
from pathlib import Path
import functools,http.server,json,os,subprocess,threading
ROOT=Path(__file__).resolve().parent.parent

def test_results_belong_to_the_active_input(tmp_path):
    logs=(tmp_path/'http.log').open('w')
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self,fmt,*args):
            logs.write((fmt%args)+'\n');logs.flush()
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT/'web_preview/dist')))
    t=threading.Thread(target=server.serve_forever,daemon=True);t.start()
    try:
        result=subprocess.run(['node',str(ROOT/'tests/js/result_source_provenance.js'),'http://127.0.0.1:'+str(server.server_address[1])+'/index.html',str(ROOT/'evaluation/browser_acceptance_18_senior/inputs/original_multigrain_label.jpg'),str(tmp_path)],capture_output=True,text=True,timeout=80,env=os.environ)
        assert result.returncode==0,result.stdout+'\n'+result.stderr
        x=json.loads((tmp_path/'result-source-controls.json').read_text())
        assert len(x['checks'])==22
        assert all(r['passed'] for r in x['checks'])
        print(result.stdout)
    finally:
        server.shutdown();server.server_close();logs.close()

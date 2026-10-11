#!/usr/bin/env python3
"""Offline current-source Market tests executed in the real Core consumer graph.
An explicit new MARKET_REGRESSION_OUTPUT is required. No frozen runner is invoked.
"""
from pathlib import Path
import collections,ctypes,datetime,hashlib,json,os,re,stat,subprocess,sys
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,message):
    if not ok: raise ValueError(message)
def load_manifest():
    return json.loads((Path(__file__).with_name('market_consumer_regression_manifest.json')).read_text())
def roots(m):
    return {k:Path(os.environ.get({'ACT':'SOUL_ACT_ROOT','ECO':'SOUL_ECOSYSTEM_ROOT'}[k],v)).resolve() for k,v in m['roots'].items()}
def bind(x,r):return r[x['root']]/x['relative']
def require_owned_ancestors(p,root):
    require(p.is_relative_to(root),'owning source outside selected root')
    parent=root
    for segment in p.relative_to(root).parts[:-1]:
        parent=parent/segment
        require(not parent.is_symlink(),'noncanonical owning source ancestor: '+str(parent))

def checked_aliases(m,r):
    aliases={str(bind(x['alias'],r)):bind(x['writer'],r) for x in m['aliases']}
    for x in m['aliases']:require_owned_ancestors(bind(x['writer'],r),r[x['writer']['root']])
    for p,target in aliases.items():
        try: valid=Path(p).is_symlink() and Path(p).resolve(strict=True)==target.resolve(strict=True)
        except (OSError,RuntimeError): valid=False
        require(valid,'producer source alias drift/cycle/dangling: '+p)
    return aliases

def recursive_move_members(directory,aliases,root):
    """Recursively follow only the13 reviewed aliases; never omit loader members.
    Unknown links (including dangling/cyclic paths) refuse before traversal.
    Return resolved owning file membership, so reviewed aliases select one owner.
    """
    def check_link(p):
        if p.is_symlink():
            require(str(p) in aliases,'unreviewed compiler input alias: '+str(p))
            try: valid=p.resolve(strict=True)==aliases[str(p)].resolve(strict=True)
            except (OSError,RuntimeError): valid=False
            require(valid,'producer source alias drift/cycle/dangling: '+str(p))
    # Check ancestor links too: is_file alone follows them invisibly.
    require(directory.is_relative_to(root),'compiler directory outside selected root')
    p=root
    for segment in directory.relative_to(root).parts:
        p=p/segment;check_link(p)
    def walk(p,ancestry):
        check_link(p)
        if not p.exists():return set()
        info=p.stat()
        if stat.S_ISDIR(info.st_mode):
            inode=(info.st_dev,info.st_ino)
            require(inode not in ancestry,'compiler input directory cycle: '+str(p))
            found=set()
            for child in sorted(p.iterdir()):found.update(walk(child,ancestry|{inode}))
            return found
        if p.suffix=='.move':
            require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,'non-owning recursive compiler source: '+str(p))
            return {str(p.resolve(strict=True))}
        return set()
    return walk(directory,set())

def read_current(m,test_root=None,tool=None):
    c=m['pinned_counts']
    require(len(m['files'])==c['source_files'] and len(m['tests'])==c['owning_test_files'] and len(m['graph_manifest'])==c['assembled_inputs'] and len(m['production_mv'])==c['production_modules'] and len(m['core_test_mv'])==c['core_test_modules'] and len(m['transport_test_mv'])==c['transport_test_modules'] and len(m['expected_identities'])==c['test_identities'] and len(m['compiler_input_directories'])==c['compiler_input_directories'] and len(m['aliases'])==c['reviewed_aliases'],'invalid explicit pinned manifest counts')
    r=roots(m); tool=Path(tool or os.environ.get('SUI_BINARY',r['ACT']/'output/contract-rebuild/local-ptb-2026-10-08/tooling/sui'))
    require(tool.is_file() and sha(tool)==m['tool_sha256'],'missing or changed pinned tooling')
    require(Path('/usr/bin/sandbox-exec').is_file(),'network/write-denying sandbox unavailable')
    aliases=checked_aliases(m,r)
    contents={}; before={}
    for row in m['files']:
        p=bind(row['source'],r);require_owned_ancestors(p,r[row['source']['root']]); require(p.is_file() and not p.is_symlink() and p.stat().st_nlink==1,'missing/non-owning current source: '+str(p))
        data=p.read_bytes(); mode=stat.S_IMODE(p.stat().st_mode)
        require(hashlib.sha256(data).hexdigest()==row['actual_sha256'] and mode==row['actual_mode'],'current source hash/mode drift: '+str(p))
        before[str(p)]={'sha256':hashlib.sha256(data).hexdigest(),'mode':mode}
        if 'local_edges' in row:
            edges=iter(row['local_edges'])
            def normalize(match):
                edge=next(edges,None);require(edge is not None and match[1]==edge['raw'],'unreviewed Move.toml edge')
                require((p.parent/match[1]).resolve()==bind(edge['target'],r).resolve(),'Move.toml dependency target drift')
                return 'local = "'+edge['normalized']+'"'
            data=re.sub(r'local\s*=\s*"([^"]+)"',normalize,data.decode()).encode()
            require(next(edges,None) is None,'missing reviewed Move.toml edge')
        require(hashlib.sha256(data).hexdigest()==row['normalized_sha256'],'normalized current source drift')
        contents[row['graph']]=data
    # Match the pinned Move loader's recursive WalkDir/follow_links semantics.
    # The manifest covers selected production and dev directories recursively,
    # including dependency test fixtures; owning Market tests are selected separately.
    observed_files=set()
    for source_directory in m['compiler_input_directories']:
        observed_files.update(recursive_move_members(bind(source_directory,r),aliases,r[source_directory['root']]))
    selected_graph_directories=[Path(d['graph_directory']) for d in m['compiler_input_directories']]
    expected_files={str(bind(row['source'],r).resolve()) for row in m['files'] if row['graph'].endswith('.move') and any(Path(row['graph']).is_relative_to(d) for d in selected_graph_directories)}
    require(observed_files==expected_files,'actual recursive compiler source inventory drift')
    owning=Path(test_root or os.environ.get('MARKET_OWNING_TEST_ROOT',r['ECO']/'soul-market')).resolve()
    observed_tests=recursive_move_members(owning/'move/soulidity_market/tests',{},owning)
    require(observed_tests=={str((owning/t['path']).resolve()) for t in m['tests']},'owning recursive test inventory drift')
    for t in m['tests']:
        p=owning/t['path'];require(p.is_file() and not p.is_symlink() and p.stat().st_nlink==1,'missing actual owning test')
        data=p.read_bytes();mode=stat.S_IMODE(p.stat().st_mode)
        require(hashlib.sha256(data).hexdigest()==t['sha256'] and mode==t['mode'],'stale/changed actual owning test: '+str(p))
        before[str(p)]={'sha256':hashlib.sha256(data).hexdigest(),'mode':mode};contents[t['graph']]=data
    require(len(contents)==m['pinned_counts']['assembled_inputs'] and {p:hashlib.sha256(d).hexdigest() for p,d in contents.items()}==m['graph_manifest'],'current assembled pinned graph identity drift')
    require(len(m['expected_identities'])==44 and len(set(m['expected_identities']))==44,'invalid reviewed identity set')
    return contents,before,tool,owning

def parse_outcomes(raw,expected):
    clean=re.sub(r'\x1b\[[0-9;]*m','',raw)
    outcomes=re.findall(r'\[\s*(PASS|FAIL|TIMEOUT)\s*\]\s+(\S+)',clean)
    counts=collections.Counter(i for s,i in outcomes)
    require(len(outcomes)==44 and all(v==1 for v in counts.values()) and set(counts)==set(expected),'zero/duplicate/extra/missing exact test identity')
    require(all(s=='PASS' for s,i in outcomes),'actual Market test failure')
    summaries=re.findall(r'Test result[^\n]*',clean)
    require(summaries==['Test result: OK. Total tests: 44; passed: 44; failed: 0'],'missing/nonexact raw test summary')
    return {'raw_identity_outcomes':[{'identity':i,'outcome':s} for s,i in outcomes],'summaries':summaries}

def inventory(root,suffix=None):
    return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file() and (suffix is None or p.suffix==suffix)}
def execute(run,mode,package,contents,tool):
    run.mkdir(); inputs=run/'inputs'
    for rel,data in contents.items():
        p=inputs/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);p.chmod(0o444)
    home=run/'private-home';conf=home/'.sui/sui_config';conf.mkdir(parents=True);key=conf/'empty.keystore';key.write_text('[]\n');key.chmod(0o600)
    (conf/'client.yaml').write_text('keystore:\n  File: '+str(key)+'\nenvs:\n  - alias: testnet\n    rpc: http://127.0.0.1:9\n    ws: null\n    basic_auth: null\nactive_env: testnet\nactive_address: null\n')
    cache=run/'move-home';cache.mkdir();tmp=run/'tmp';tmp.mkdir()
    policy='(version 1)(allow default)(deny network*)(deny file-write*)(allow file-write* (subpath '+json.dumps(str(run))+') (literal "/dev/null"))'
    (run/'sandbox.sb').write_text(policy+'\n')
    command=[str(tool),'move',mode,'--path',str(inputs/'move'/package),'--install-dir',str(run/'build')]
    if mode=='test':command.append('soulidity_market::')
    env=dict(os.environ,HOME=str(home),MOVE_HOME=str(cache),TMPDIR=str(tmp)+'/',TMP=str(tmp),TEMP=str(tmp),PYTHONDONTWRITEBYTECODE='1')
    started=datetime.datetime.now(datetime.timezone.utc).isoformat(); before=inventory(inputs)
    # macOS refuses nested sandbox_apply. A registered CI may already inherit
    # the same deny-network/deny-write sandbox; check its effective kernel state.
    lib=ctypes.CDLL('/usr/lib/libSystem.B.dylib');lib.sandbox_check.restype=ctypes.c_int
    inherited=all(lib.sandbox_check(os.getpid(),op,0)==1 for op in [b'network-outbound',b'network-inbound',b'file-write-data',b'file-write-create'])
    launch=command if inherited else ['/usr/bin/sandbox-exec','-f',str(run/'sandbox.sb')]+command
    with (run/'raw.log').open('w') as f:
        result=subprocess.run(launch,cwd=run,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=1500,check=False)
    raw=(run/'raw.log').read_text(); after=inventory(inputs)
    receipt={'command':command,'started':started,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'exit_code':result.returncode,'tool_sha256':sha(tool),'network_denied':True,'sandbox_mode':'inherited_kernel_checked' if inherited else 'per_compiler','default_budget':True,'budget_overrides':[],'keyless':{'keystore':json.loads(key.read_text()),'active_address':None,'rpc':'http://127.0.0.1:9'},'input_before':before,'input_after':after,'compiled_mv':inventory(run/'build','.mv'),'raw_sha256':sha(run/'raw.log'),'chain_transactions':0}
    (run/'result.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    require(result.returncode==0,'compiler failure; receipt retained at '+str(run/'result.json'))
    require(before==after,'compiler changed isolated source inputs')
    require(not re.search(r'recovery phrase|Secret Recovery Phrase|mnemonic',raw,re.I),'unexpected recovery material')
    require(receipt['keyless']['keystore']==[],'keystore changed')
    return receipt,raw

def main():
    m=load_manifest();contents,before,tool,owning=read_current(m)
    if '--preflight' in sys.argv:print(json.dumps({'status':'PREFLIGHT_PASS','actual_sources':m['pinned_counts']['source_files'],'owning_tests':m['pinned_counts']['owning_test_files'],'owning_test_root':str(owning)}));return
    require(os.environ.get('MARKET_REGRESSION_OUTPUT'),'MARKET_REGRESSION_OUTPUT must name a fresh isolated output directory')
    output=Path(os.environ['MARKET_REGRESSION_OUTPUT']).resolve();require(not output.exists(),'output exists; preserve all previous runs')
    r=roots(m)
    require(all(not output.is_relative_to(bind(x['source'],r).parent) for x in m['files']),'output overlaps source package directory')
    output.mkdir(parents=True)
    result={'status':'RUNNING','scope':m['scope'],'owning_test_root':str(owning),'actual_activation':all(r[k]==Path(m['canonical_actual_roots'][k]).resolve() for k in r) and owning==(Path(m['canonical_actual_roots']['ECO'])/'soul-market').resolve(),'source_before':before,'network_denied':True,'max_meaningful_attempts':5,'compiler_invocations':0,'standalone_market_ci_release':'pending','full_goal_complete':False}
    try:
        result['compiler_invocations']+=1;production,_=execute(output/'production-market','build','soulidity_market',contents,tool)
        require(production['compiled_mv']==m['production_mv'],'production Market byte map differs from accepted current-source reference')
        result['production_market_mv_exact']=True;result['production_module_count']=len(production['compiled_mv'])
        result['compiler_invocations']+=1;test,raw=execute(output/'combined-market-tests','test','soulidity_v1',contents,tool)
        result.update(parse_outcomes(raw,m['expected_identities']))
        require(test['compiled_mv']==m['transport_test_mv'],'combined test byte map differs from accepted transport')
        require(all(test['compiled_mv'].get(p)==h for p,h in m['core_test_mv'].items()),'accepted current Core test module bytes changed')
        require(set(test['compiled_mv'])-set(m['core_test_mv'])=={'build/soulidity_v1/bytecode_modules/'+Path(t['path']).stem+'_owned_transport_v1.mv' for t in m['tests']},'extra module is not one of four reviewed test-only modules')
        result.update({'current_core_test_modules_exact':m['pinned_counts']['core_test_modules'],'extra_test_only_modules':m['pinned_counts']['extra_test_only_modules'],'status':'PASS'})
    except Exception as e:result['status']='FAIL';result['error']=str(e);raise
    finally:
        try:
            _,after,_,_=read_current(m);result['source_after']=after;result['source_unchanged']=before==after
            require(before==after,'actual sources changed during execution')
        except Exception as e:result['status']='FAIL';result['source_guard_error']=str(e)
        (output/'evidence.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    require(result['status']=='PASS','final source guard failed')
    print(json.dumps({'status':'PASS','scope':m['scope'],'actual_activation':result['actual_activation'],'source_unchanged':result['source_unchanged'],'tests':44,'production_modules':len(m['production_mv']),'current_core_test_modules':m['pinned_counts']['core_test_modules'],'extra_test_only_modules':m['pinned_counts']['extra_test_only_modules'],'evidence':str(output/'evidence.json'),'chain_transactions':0}))
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,subprocess.TimeoutExpired) as error: print('current consumer regression refused: '+str(error),file=sys.stderr);sys.exit(1)

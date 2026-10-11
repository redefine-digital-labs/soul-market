from pathlib import Path
import hashlib,json,subprocess
OLD=Path('/Users/naoer/.codex/worktrees/ecosystem-market-extraction/soulidity/repository-extraction/evidence/production-build-final/build/SoulidityMarket')
NEW=Path('/Users/naoer/Documents/Claude/Projects/soulidity-ecosystem/soul-market/output/import-check-r1/production-build/build/SoulidityMarket')
OUT=Path(__file__).parent
CLI='/Users/naoer/.codex/worktrees/soul-dof-v1-rebuild/soulidity/output/contract-rebuild/local-ptb-2026-10-08/tooling/sui'
def uleb(b,p):
 n=0;shift=0
 while True:
  x=b[p];p+=1;n|=(x&127)<<shift
  if x<128:return n,p
  shift+=7
  assert shift<64

def enc(n):
 r=[]
 while n>127:r.append((n&127)|128);n>>=7
 return bytes(r+[n])
def pairs(b):
 r=[];p=0
 while p<len(b):
  a,p=uleb(b,p);n,p=uleb(b,p);r.append((a,n))
 assert p==len(b)
 return r

def parse(b):
 assert b[:4]==bytes.fromhex('a11ceb0b')
 nt,p=uleb(b,8);tables={}
 for _ in range(nt):
  kind=b[p];p+=1;offset,p=uleb(b,p);size,p=uleb(b,p);tables[kind]=(offset,size)
 start=p
 tabs={k:b[start+o:start+o+z] for k,(o,z) in tables.items()}
 end=start+max(o+z for o,z in tables.values())
 selfi,end2=uleb(b,end);assert end2==len(b)
 addresses=[tabs[8][i:i+32] for i in range(0,len(tabs[8]),32)]
 handles=pairs(tabs[1]);own=addresses[handles[selfi][0]]
 return {'header':b[:start],'start':start,'tables':tables,'tabs':tabs,'addresses':addresses,'self':own,'selfi':selfi,'trailer':b[end:]}

oldfiles={str(x.relative_to(OLD/'bytecode_modules')):x for x in (OLD/'bytecode_modules').rglob('*.mv')}
newfiles={str(x.relative_to(NEW/'bytecode_modules')):x for x in (NEW/'bytecode_modules').rglob('*.mv')}
assert oldfiles.keys()==newfiles.keys()
mods={key:(parse(oldfiles[key].read_bytes()),parse(newfiles[key].read_bytes())) for key in oldfiles}
new_to_old={};mapping=[]
for key,(a,b) in mods.items():
 if b['self'] in new_to_old:assert new_to_old[b['self']]==a['self']
 new_to_old[b['self']]=a['self']
 if a['self']!=b['self']:
  pkg=key.split('/')[1]
  entry={'package':pkg,'old':'0x'+a['self'].hex().lstrip('0'),'new':'0x'+b['self'].hex().lstrip('0')}
  if entry not in mapping:mapping.append(entry)
report={'method':'Module format v7: parse ULEB128 table directory; only restore AddressIdentifiers by established per-package self-ID bijection, remap AddressIdentifierIndex in ModuleHandles/FriendDecls. Every other byte must equal the old artifact. No opcode/constant/type/signature changes are permitted.','addressMapping':sorted(mapping,key=lambda x:x['package']),'moduleResults':[]}
for key,(a,b) in sorted(mods.items()):
 old=oldfiles[key].read_bytes();new=newfiles[key].read_bytes()
 norm=bytearray(new)
 oldidx={addr:i for i,addr in enumerate(a['addresses'])}
 idxmap={i:oldidx[new_to_old[addr]] for i,addr in enumerate(b['addresses'])}
 assert len(set(idxmap.values()))==len(idxmap)==len(a['addresses'])
 changed=[k for k in a['tabs'] if a['tabs'][k]!=b['tabs'][k]]
 assert a['tables']==b['tables'] and a['header']==b['header']
 for kind in [1,15]:
  if kind not in b['tabs']:continue
  replacement=b''.join(enc(idxmap[i])+enc(n)for i,n in pairs(b['tabs'][kind]))
  off,size=b['tables'][kind];assert len(replacement)==size
  norm[b['start']+off:b['start']+off+size]=replacement
 off,size=b['tables'][8];norm[b['start']+off:b['start']+off+size]=b''.join(a['addresses'])
 eq=bytes(norm)==old
 if not eq:raise AssertionError('Normalization failed '+key)
 report['moduleResults'].append({'path':key,'rawEqual':old==new,'addressNormalizedByteEqual':eq,'changedTableKinds':[hex(k)for k in changed],'oldSHA':hashlib.sha256(old).hexdigest(),'newSHA':hashlib.sha256(new).hexdigest(),'normalizedSHA':hashlib.sha256(norm).hexdigest()})
 if key=='market.mv':
  (OUT/'new-normalized-to-old.mv').write_bytes(norm)
  report['marketDifferingByteOffsets']=[i for i,(x,y)in enumerate(zip(old,new))if x!=y]
report['summary']={'total':len(mods),'rawEqual':sum(r['rawEqual']for r in report['moduleResults']),'rawDifferent':sum(not r['rawEqual']for r in report['moduleResults']),'normalizedEqual':sum(r['addressNormalizedByteEqual']for r in report['moduleResults'])}
(OUT/'normalized-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k!='moduleResults'},indent=2))

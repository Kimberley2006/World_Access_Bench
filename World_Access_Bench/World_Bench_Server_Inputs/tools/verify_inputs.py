"""Verify packaged inputs only. Does not generate videos or certify final labels."""
from pathlib import Path
import collections,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def jl(p):return [json.loads(x)for x in (ROOT/p).read_text().splitlines()if x.strip()]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());bad=[]
 for x in manifest['files']:
  p=ROOT/x['path']
  if not p.is_file()or p.stat().st_size!=x['bytes']or sha(p)!=x['sha256']:bad.append(x['path'])
 if bad:raise ValueError('Missing/changed files: '+str(bad))
 ss,tt,jobs=jl('sources.jsonl'),jl('tasks.jsonl'),jl('generation/jobs.jsonl')
 assert len(ss)==97 and len(tt)==277 and len(jobs)==1662
 sm={s['source_id']:s for s in ss};tm={t['task_id']:t for t in tt}
 assert len(sm)==97 and len(tm)==277 and len({j['job_id']for j in jobs})==1662
 excluded={r['source_id']for r in jl('provenance/excluded_sources.jsonl')}
 excluded_tasks={r['task_id']for r in jl('provenance/excluded_incomplete_tasks.jsonl')}
 assert not (set(sm)&excluded) and not (set(tm)&excluded_tasks)
 groups=collections.defaultdict(set);hashes=collections.defaultdict(set)
 for s in ss:
  assert sha(ROOT/s['video_path'])==s['sha256'];groups[s['split_group_id']].add(s['benchmark_split']);hashes[s['sha256']].add(s['benchmark_split'])
  assert all((ROOT/f).is_file()for f in s['source_evidence']['sheets'])
 assert all(len(x)==1 for x in groups.values())and all(len(x)==1 for x in hashes.values())
 bytask=collections.defaultdict(list)
 for j in jobs:
  t=tm[j['task_id']];assert t['source_id']==j['source_id']
  assert t['benchmark_split']==j['benchmark_split']==sm[t['source_id']]['benchmark_split']
  assert j['spec_revision']==t['spec_revision'];bytask[t['task_id']].append(j)
  assert j['actual_video_path']is None and j['status']=='planned_not_generated'
 for tid,rows in bytask.items():assert {(r['method_id'],r['seed'])for r in rows}=={(m,s)for m in ['h3_ref2va','wan_flowedit','wan_flowalign']for s in [4101,4102]}
 for split in ['train','validation','test']:
  assert {t['task_id']for t in jl(f'splits/{split}_tasks.jsonl')}=={t['task_id']for t in tt if t['benchmark_split']==split}
  assert {j['job_id']for j in jl(f'splits/{split}_jobs.jsonl')}=={j['job_id']for j in jobs if j['benchmark_split']==split}
 diagnostics=jl('diagnostics/results.jsonl');assert len(diagnostics)==831
 assert all(r['task_id']in tm and (ROOT/r['video_path']).is_file()for r in diagnostics)
 print(json.dumps({'input_validation':'passed','verified_packaged_files':len(manifest['files']),'sources':97,'tasks':277,'planned_natural_outputs':1662,'actual_natural_outputs':0,'actual_physics_labels':0,'final_training_dataset_ready':False},ensure_ascii=False))
if __name__=='__main__':
 try:main()
 except Exception as e:print('VALIDATION FAILED:',e,file=sys.stderr);sys.exit(1)

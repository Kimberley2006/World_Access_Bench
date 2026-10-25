from pathlib import Path
import json,shutil,os,hashlib,collections

BASE=Path(__file__).parent
OLD=BASE/'worldbench_auto_release'
OUT=BASE/'World_Bench_Server_Inputs'
EVIDENCE=BASE/'worldbench_revision/package'
VERSION='worldbench-server-inputs-20261025-fixed'
def jl(p):return [json.loads(x)for x in Path(p).read_text().splitlines()if x.strip()]
def writejl(p,rows):
 p=OUT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n'for x in rows))
def writejson(p,x):
 p=OUT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def copy(src,dest):
 dest=OUT/dest;dest.parent.mkdir(parents=True,exist_ok=True)
 if not dest.exists():
  try:os.link(src,dest)
  except OSError:shutil.copyfile(src,dest)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
sources=jl(OLD/'sources.jsonl');alltasks=jl(OLD/'tasks.jsonl')
held=[t for t in alltasks if not t['generation_gate']['formal_generation_allowed']]
tasks=[t for t in alltasks if t not in held];ids={t['task_id']for t in tasks}
assert len(sources)==97 and len(tasks)==277 and len(held)==2
for t in tasks:
 t['previous_spec_revision']=t['spec_revision'];t['spec_revision']=VERSION;t['schema_version']=VERSION
 t['generation_gate']={'status':'ready_for_server_backend_binding','formal_generation_allowed':True}
 t['review']['historical_ai_review_ref']='provenance/input_spec_reviews.jsonl'
 t['candidate_result_ids']=[];t['generated_results']=0;t['candidate_plan_count']=6
 t['evaluation_protocol_ref']='protocols/ANNOTATION_PROTOCOL.md'
for s in sources:
 s['release_version']=VERSION;copy(OLD/s['video_path'],Path(s['video_path']))
 for f in s['source_evidence']['sheets']:copy(EVIDENCE/f,Path(f))
writejl(Path('sources.jsonl'),sources);writejl(Path('tasks.jsonl'),tasks)
writejl(Path('provenance/excluded_incomplete_tasks.jsonl'),held)
for f in ['excluded_sources.jsonl','excluded_tasks.jsonl','input_spec_reviews.jsonl','task_revision_log.jsonl']:
 copy(OLD/'provenance'/f,Path('provenance')/f)
copy(OLD/'rules.json',Path('protocols/rules.json'))
contract=json.loads((OLD/'output_contract.json').read_text());contract.update(schema_version=VERSION,annotation_states=['unannotated','ai_a','ai_b','ai_reconciled'],reference_tier='AI_silver_not_human_gold')
writejson(Path('protocols/output_contract.json'),contract)
methods=[('h3_ref2va','MiniMax-H3-Base-Ref2VA'),('wan_flowedit','Wan2.1-T2V-1.3B + FlowEdit'),('wan_flowalign','Wan2.1-T2V-1.3B + FlowAlign')]
jobs=[]
for t in tasks:
 for method,name in methods:
  for seed in [4101,4102]:
   jid=t['task_id']+'__'+method+'__s'+str(seed)
   jobs.append(dict(job_id=jid,result_id=jid,task_id=t['task_id'],source_id=t['source_id'],benchmark_split=t['benchmark_split'],split_group_id=t['split_group_id'],spec_revision=VERSION,method_id=method,method_name=name,seed=seed,source_video_path='videos/sources/'+t['source_id']+'.mp4',requested_duration_seconds=t['time_contract']['duration_seconds'],planned_output_path='results/videos/'+jid+'.mp4',actual_video_path=None,actual_video_sha256=None,status='planned_not_generated',annotation_status='not_started'))
writejl(Path('generation/jobs.jsonl'),jobs)
writejson(Path('generation/backends.json'),{'version':VERSION,'backends':{k:{'method_name':v,'project_path':None,'checkpoint_path':None,'checkpoint_sha256':None,'commit_id':None,'launch_argv':None,'status':'requires_server_local_binding'}for k,v in methods},'seeds':[4101,4102],'prompt_policy':'translate_expand_task_without_semantic_change; no output labels or future ground-truth intervals','video_policy':'retain_entire_source_time_range; record input/output PTS and preprocessing; do not blindly export at fixed16fps'})
for split in ['train','validation','test']:
 writejl(Path(f'splits/{split}_sources.jsonl'),[s for s in sources if s['benchmark_split']==split])
 writejl(Path(f'splits/{split}_tasks.jsonl'),[t for t in tasks if t['benchmark_split']==split])
 writejl(Path(f'splits/{split}_jobs.jsonl'),[j for j in jobs if j['benchmark_split']==split])
controlrows=jl(OLD/'results/results.jsonl');controlanns=jl(OLD/'annotations/ai_silver_partial.jsonl')
for s in sources:
 for recipe in ['global_slowdown_1p25','full_frame_freeze']:
  f=Path('videos/controls')/(s['source_id']+'__'+recipe+'.mp4');copy(OLD/f,Path('diagnostics')/f)
for r in controlrows:
 if r['role']!='unedited_source_control':r['video_path']='diagnostics/'+r['video_path']
 r['diagnostic_only']=True;r['not_validated_against_current_task_revision']=True
writejl(Path('diagnostics/results.jsonl'),[r for r in controlrows if r['task_id']in ids])
writejl(Path('diagnostics/ai_silver_partial_previous_revision.jsonl'),[r for r in controlanns if r['task_id']in ids])
writejl(Path('diagnostics/media_verification.jsonl'),[{**r,'video_path':('diagnostics/'+r['video_path']) if r['recipe']!='identity' else r['video_path']}for r in jl(OLD/'results/media_verification.jsonl')])
writejson(Path('provenance/package_transition.json'),{'prior_package':'World_Bench_AI97_Server_Package.zip','change':'Implement latest agreed plan: six natural outputs = three editing methods x two seeds; prior controls become diagnostics; two incomplete tasks removed, their other well-defined source tasks remain.','task_text_changed_in_packaging':False,'source_videos_removed_this_packaging':[],'excluded_task_ids':[t['task_id']for t in held],'historical_review_files_are_not_training_labels':True})
writejson(Path('PACKAGE_STATUS.json'),{'version':VERSION,'purpose':'all_in_one_server_input_bundle','sources':97,'tasks':277,'source_groups':len({s['split_group_id']for s in sources}),'planned_natural_outputs':len(jobs),'actual_natural_outputs':0,'actual_physics_labels':0,'source_video_count':97,'diagnostic_transformed_video_count':194,'evidence_image_count':len({f for s in sources for f in s['source_evidence']['sheets']}),'diagnostic_pair_count':sum(r['task_id']in ids for r in controlrows),'source_counts':dict(collections.Counter(s['benchmark_split']for s in sources)),'task_counts':dict(collections.Counter(t['benchmark_split']for t in tasks)),'job_counts':dict(collections.Counter(j['benchmark_split']for j in jobs)),'model_weights_included':False,'server_launch_commands_bound':False,'final_training_dataset_ready':False})
print((OUT/'PACKAGE_STATUS.json').read_text())

#!/usr/bin/env python3
"""Compare recorded usage with a catalog-based task-complexity estimate, without replay."""
import argparse, json, os
from pathlib import Path

def files(root, sid):
    hits=[]
    for base in [Path(root)/'sessions', Path(root)/'archived_sessions']:
        if base.exists(): hits += list(base.rglob(f'*{sid}*.jsonl'))
    return hits
def main():
    p=argparse.ArgumentParser(); p.add_argument('--session-id',required=True); p.add_argument('--codex-home',default=str(Path.home()/'.codex')); p.add_argument('--format',choices=['json','markdown'],default='markdown'); a=p.parse_args()
    fs=files(a.codex_home,a.session_id)
    if not fs: print(json.dumps({'available':False,'error':'session not found'}) if a.format=='json' else 'Sessie niet gevonden.'); return
    model_counts={}; effort_counts={}; tier_counts={}; total=0; events=0; tools=0; compactions=0
    for f in fs:
        for line in f.read_text(errors='ignore').splitlines():
            try: x=json.loads(line); pld=x.get('payload',x)
            except Exception: continue
            typ=x.get('type') or pld.get('type')
            if typ=='token_count':
                u=pld.get('info',{}).get('last_token_usage',{}) or pld.get('last_token_usage',{})
                if u:
                    total += int(u.get('total_tokens') or (int(u.get('input_tokens') or 0) + int(u.get('output_tokens') or 0)))
                    events+=1
            if typ in ('function_call','tool_call'): tools+=1
            if 'compaction' in str(typ).lower(): compactions+=1
            if typ=='thread_settings_applied':
                s=pld.get('thread_settings') or pld.get('settings') or pld; m=s.get('model'); e=s.get('reasoning_effort') or s.get('reasoning_level'); t=s.get('service_tier')
                if m:model_counts[m]=model_counts.get(m,0)+1
                if e:effort_counts[e]=effort_counts.get(e,0)+1
                if t:tier_counts[t]=tier_counts.get(t,0)+1
    complexity='complex' if compactions or tools>=20 or events>=30 else ('simple' if tools<=8 and events<=8 else 'standard')
    result={'available':True,'files':[str(f) for f in fs],'actual':{'tokens':total,'token_events':events,'models':model_counts,'reasoning':effort_counts,'service_tiers':tier_counts},'estimated_task_complexity':complexity,'credit_comparison':{'status':'not_calculable_without_pricing_mapping','note':'Tokens are measured; hypothetical credits cannot be measured without replay or a supplied pricing map.'},'confidence':'medium' if events else 'low'}
    if a.format=='json': print(json.dumps(result,ensure_ascii=False,indent=2))
    else:
        print(f"Recorded tokens: {total:,} · token events: {events}")
        print(f"Recorded models: {model_counts or 'unknown'}")
        print(f"Estimated task complexity: {complexity} (estimate, confidence {result['confidence']})")
        print('Credits: not calculable without a pricing mapping; no replay performed.')
if __name__=='__main__': main()

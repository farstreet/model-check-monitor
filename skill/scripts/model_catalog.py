#!/usr/bin/env python3
"""Print a safe, prompt-free summary of the local Codex model catalog."""
import argparse, json, os
from pathlib import Path

def main():
    p = argparse.ArgumentParser(); p.add_argument('--path'); p.add_argument('--format', choices=['json','markdown'], default='markdown'); a=p.parse_args()
    path = Path(a.path or os.environ.get('CODEX_MODELS_CACHE', str(Path.home()/'.codex/models_cache.json')))
    try: data=json.loads(path.read_text())
    except Exception as e:
        out={'available':False,'path':str(path),'error':str(e)}
        print(json.dumps(out, ensure_ascii=False, indent=2) if a.format=='json' else f'Catalogus: niet beschikbaar ({e})'); return
    rows=[]
    for m in data.get('models',[]):
        rows.append({'slug':m.get('slug'),'display_name':m.get('display_name') or m.get('displayName') or m.get('slug'),
                     'description':m.get('description',''), 'default_reasoning':m.get('default_reasoning_level') or m.get('defaultReasoningEffort'),
                     'reasoning_levels':m.get('supported_reasoning_levels') or m.get('supportedReasoningLevels') or [],
                     'service_tiers':m.get('service_tiers') or m.get('serviceTiers') or []})
    out={'available':True,'path':str(path),'fetched_at':data.get('fetched_at'),'client_version':data.get('client_version'),'models':rows}
    if a.format=='json': print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(f"Catalogus: {len(rows)} modellen · opgehaald {out['fetched_at'] or 'onbekend'}")
        for r in rows:
            levels=[x if isinstance(x,str) else (x.get('effort') or x.get('level') or str(x)) for x in r['reasoning_levels']]
            print(f"- {r['display_name']} ({r['slug']}) · reasoning: {', '.join(levels) or 'onbekend'}")
if __name__=='__main__': main()

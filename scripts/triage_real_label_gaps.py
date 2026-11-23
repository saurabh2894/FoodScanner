"""Current, input-deduplicated triage of recorded real-label texts.

Unlike the historical demand inventory, this ranks no terms and does not treat
recognition as classification. Outputs go outside tracked evaluation evidence.
No network, classifier changes, synthetic expansion or source admission.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from foodscan.pipeline import analyse_text

BATCHES = ('fresh_batch_1', 'fresh_batch_2', 'fresh_batch_3', 'dev_regression_15', 'negation_addendum', 'browser_acceptance_18_senior')


def triage(root=ROOT):
    records = []
    seen = {}
    for batch in BATCHES:
        for f in sorted((root / 'evaluation' / batch / 'inputs').glob('*.txt')):
            text = f.read_text(encoding='utf-8')
            key = ' '.join(text.split())
            source = str(f.relative_to(root))
            if key in seen:
                seen[key]['also_recorded_at'].append(source)
                continue
            a = analyse_text(text, source='text')
            r = dict(input_path=source, also_recorded_at=[], group=a.group, answered=a.answered,
                     reason=a.reason, not_assessed=[u for u in a.unassessed if 'group name; its contents were assessed separately' not in u],
                     recognised_unplaced=a.unplaced, completeness=a.completeness,
                     warnings=a.warnings, decisive_or_weak_items=[dict(ingredient=d.ingredient, detail=d.detail, source=d.source) for d in a.drivers])
            seen[key] = r
            records.append(r)
    return dict(scope='Existing recorded real-label text, not a representative or held-out sample. No new accuracy claim.',
                limits='Reference text can contain transcription damage. Group4 may stand despite other gaps. Read original pack before fixing a name. Recognition alone is not placement.',
                unique_inputs=len(records), answered=sum(r['answered'] for r in records),
                abstained=sum(not r['answered'] for r in records), records=records)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    if args.out.exists():
        ap.error('refusing to overwrite existing evidence')
    if args.out.resolve().is_relative_to((ROOT / 'evaluation').resolve()):
        ap.error('output must be outside tracked evaluation evidence')
    result = triage()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print({k: result[k] for k in ('unique_inputs', 'answered', 'abstained')})


if __name__ == '__main__':
    main()

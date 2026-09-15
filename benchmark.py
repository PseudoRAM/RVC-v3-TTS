"""Benchmark text -> Kokoro -> English VCTK; publish only synthesized source/output pairs."""
import argparse
import hashlib
import json
import os
import platform
import shutil
import statistics
import time
from pipeline import Pipeline, Request, ROOT

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', type=int, default=4)
    args = parser.parse_args()
    if args.runs < 2:
        parser.error('At least two runs are required')
    run_root = ROOT/'demos'/time.strftime('%Y%m%d-%H%M%S')
    run_root.mkdir(parents=True)
    report = {'scope':'text -> Kokoro -> RVC, no recorded audio input', 'platform':platform.platform(),
        'tts_python':platform.python_version(), 'rvc_python':'Configured RVC worker interpreter',
        'tts_provider':'CPUExecutionProvider', 'tts_threads':4, 'cases':[]}
    text = 'Hello, and welcome! This speech began as text. Let us take a moment to listen, then try a different voice.'
    with Pipeline() as pipeline:
        report['setup_seconds'] = pipeline.setup_seconds
        report['tts_setup_seconds'] = pipeline.tts_setup_seconds
        for label, voice, source in [('vctk226','VCTK226','am_michael'), ('vctk231','VCTK231','af_heart')]:
            request = Request(text, voice, source, 1.0, 0, 180, True)
            results=[]
            for i in range(args.runs):
                folder, metrics = pipeline.run(request, run_root/f'{label}-{i}')
                results.append(metrics)
                if i==0:
                    for kind in ('source','speech'):
                        shutil.copy2(folder/f'{kind}.wav', ROOT/'examples/audio'/f'{label}-{kind}.wav')
                print(label, i, metrics['total_seconds'], flush=True)
            row={'name':label, 'voice':voice, 'runs':results,
                'warm_median_seconds':statistics.median(r['total_seconds'] for r in results[1:]),
                'audio':{}}
            for kind in ('source','speech'):
                path=ROOT/'examples/audio'/f'{label}-{kind}.wav'
                row['audio'][kind]={'path':path.relative_to(ROOT).as_posix(),
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            report['cases'].append(row)
        report['setup_plus_first_request_seconds']=report['setup_seconds']+report['cases'][0]['runs'][0]['total_seconds']
    report['target_provenance'] = {}
    for voice in ('VCTK226', 'VCTK231'):
        checkpoint = next((ROOT/'vendor/rvc-v3/rvc_models'/voice).glob('*.pth'))
        report['target_provenance'][voice] = {
            'index_sha256': hashlib.sha256(next(checkpoint.parent.glob('*.index')).read_bytes()).hexdigest(), 'filename': checkpoint.name, 'sha256': hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
            'license': 'Apache-2.0', 'publisher': 'https://huggingface.co/Nekochu/RVC-VCTK_Voice-sample',
            'revision': '005c2f948ee9dafd7e3aa7f261b4c3a24beebeef', 'f0': True, 'sample_rate':40000}
    (ROOT/'examples/manifest.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (run_root/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__': main()

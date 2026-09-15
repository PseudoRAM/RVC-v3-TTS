import argparse
import json
from pipeline import Pipeline, Request

def main():
    parser = argparse.ArgumentParser(description='Local text to cloned speech; source.wav, speech.wav, metrics.json')
    parser.add_argument('text', help='Spoken text; newlines create explicit pauses')
    parser.add_argument('--voice', required=True, help='Installed, authorized RVC voice folder')
    parser.add_argument('--source-voice', default='af_heart')
    parser.add_argument('--speed', type=float, default=1)
    parser.add_argument('--pitch', type=int, default=0)
    parser.add_argument('--pause-ms', type=int, default=180)
    parser.add_argument('--use-index', action='store_true')
    parser.add_argument('--rvc-python')
    parser.add_argument('--output-dir')
    parser.add_argument('--repeat', type=int, default=1, help='Repeated requests in one warm process')
    args = parser.parse_args()
    if args.repeat < 1:
        parser.error('--repeat must be positive')
    request = Request(**{key:getattr(args,key) for key in Request.__dataclass_fields__})
    request.validate()
    with Pipeline(args.rvc_python) as pipeline:
        print(json.dumps({'setup_seconds':pipeline.setup_seconds}))
        for i in range(args.repeat):
            output = f'{args.output_dir}-{i}' if args.output_dir and args.repeat>1 else args.output_dir
            folder, metrics = pipeline.run(request, output)
            print(json.dumps({'folder':str(folder), **metrics}))

if __name__ == '__main__':
    main()

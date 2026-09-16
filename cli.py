import argparse
import json
from emotion import EMOTIONS, SPEAKERS
from pipeline import Pipeline, Request, PITCH_CHANGE, INDEX_RATE, USE_INDEX

def build_parser():
    parser = argparse.ArgumentParser(description='Local text to cloned speech; source.wav, speech.wav, metrics.json')
    parser.add_argument('text', help='Spoken text; newlines create explicit pauses')
    parser.add_argument('--voice', required=True, help='Installed, authorized RVC voice folder')
    parser.add_argument('--source-voice', default='af_heart')
    parser.add_argument('--speed', type=float, default=1)
    parser.add_argument('--pitch', type=int, default=PITCH_CHANGE, help='Semitones (default: +4); use 0 to preserve source pitch')
    parser.add_argument('--pause-ms', type=int, default=180)
    parser.add_argument('--use-index', action=argparse.BooleanOptionalAction, default=USE_INDEX,
                        help='Use retrieval when available (default: enabled); --no-use-index disables it')
    parser.add_argument('--index-rate', type=float, default=INDEX_RATE, help='Retrieval blend (default: 0.75)')
    parser.add_argument('--engine', choices=['auto', 'kokoro', 'qwen'], default='auto')
    parser.add_argument('--emotion', choices=EMOTIONS, default='neutral')
    parser.add_argument('--intensity', type=float, default=.7, help='Prompt strength from 0 to 1; not a volume multiplier')
    parser.add_argument('--instruct', default='', help='Custom acted delivery instructions (Qwen)')
    parser.add_argument('--expressive-speaker', choices=SPEAKERS, default='Ryan')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--rvc-python')
    parser.add_argument('--output-dir')
    parser.add_argument('--repeat', type=int, default=1, help='Repeated requests in one warm process')
    return parser

def main():
    parser = build_parser()
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

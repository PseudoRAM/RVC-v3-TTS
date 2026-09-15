"""Create text-to-RVC examples using the installed English VCTK checkpoints."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from benchmark import main
if __name__ == '__main__': main()

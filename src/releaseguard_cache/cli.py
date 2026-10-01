import argparse
import json
from pathlib import Path

from .models import CacheMode
from .scenarios import run_batch


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="releaseguard-cache")
    parser.add_argument("--mode", choices=[mode.value for mode in CacheMode], default="semantic")
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    payload = run_batch(CacheMode(args.mode))
    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        Path(args.output).write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


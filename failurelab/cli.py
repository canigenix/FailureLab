from __future__ import annotations
import argparse,sys
from pathlib import Path
from .policy import load_policy

def build_parser():
    p=argparse.ArgumentParser(prog="failurelab",description="Stress-test machine-learning models and enforce robustness policies.")
    s=p.add_subparsers(dest="command",required=True)
    c=s.add_parser("check",help="Validate a saved robustness policy.")
    c.add_argument("--policy",type=Path,required=True)
    return p

def main():
    args=build_parser().parse_args()
    if args.command=="check":
        thresholds=load_policy(args.policy)
        print(f"Loaded {len(thresholds)} robustness requirement(s).")
        return 0
    return 2
if __name__=="__main__": sys.exit(main())

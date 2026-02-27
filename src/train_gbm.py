import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def ts():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def run(cmd, cwd):
    print("")
    print(f"[{ts()}] RUN START")
    print(f"[{ts()}] CWD: {cwd}")
    print(f"[{ts()}] PY : {sys.executable}")
    print(f"[{ts()}] CMD: {' '.join(cmd)}")
    start = time.perf_counter()
    p = subprocess.Popen(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )
    assert p.stdout is not None
    for line in p.stdout:
        print(line.rstrip("\n"))
    code = p.wait()
    elapsed = time.perf_counter() - start
    print(f"[{ts()}] RUN END exit_code={code} elapsed_s={elapsed:.3f}")
    if code != 0:
        raise SystemExit(code)
    return elapsed


def must_exist(path_str, label):
    if not os.path.exists(path_str):
        print(f"[{ts()}] ERROR: expected {label} not found: {path_str}")
        raise SystemExit(2)
    size = os.path.getsize(path_str)
    print(f"[{ts()}] OK: {label} exists: {path_str} size_bytes={size}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", default=r"C:\Repos\a3data-churn\data\raw\Customer-Churn.xlsx")
    ap.add_argument("--sheet", default="Customer-Churn")

    ap.add_argument("--artifacts_dir", default=r"C:\Repos\a3data-churn\artifacts")
    ap.add_argument("--figures_dir", default=r"C:\Repos\a3data-churn\reports\figures")

    ap.add_argument("--model_path", default=r"C:\Repos\a3data-churn\artifacts\model_gbm.joblib")
    ap.add_argument("--metrics_path", default=r"C:\Repos\a3data-churn\artifacts\metrics_gbm_test.json")
    ap.add_argument("--out_scored_xlsx", default=r"C:\Repos\a3data-churn\reports\figures\scored_customers.xlsx")

    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--random_state", type=int, default=42)
    ap.add_argument("--cv_splits", type=int, default=5)
    ap.add_argument("--search_iter", type=int, default=20)

    ap.add_argument("--top_frac", type=float, default=0.10)
    ap.add_argument("--threshold", type=float, default=None)

    ap.add_argument("--train_only", action="store_true")
    ap.add_argument("--score_only", action="store_true")
    args = ap.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    train_py = repo_root / "src" / "train_gbm.py"
    score_py = repo_root / "src" / "score_customers.py"

    print(f"[{ts()}] PIPELINE START")
    print(f"[{ts()}] repo_root={repo_root}")
    print(f"[{ts()}] train_py={train_py}")
    print(f"[{ts()}] score_py={score_py}")
    print(f"[{ts()}] xlsx={args.xlsx}")
    print(f"[{ts()}] sheet={args.sheet}")
    print(f"[{ts()}] artifacts_dir={args.artifacts_dir}")
    print(f"[{ts()}] figures_dir={args.figures_dir}")
    print(f"[{ts()}] model_path={args.model_path}")
    print(f"[{ts()}] metrics_path={args.metrics_path}")
    print(f"[{ts()}] out_scored_xlsx={args.out_scored_xlsx}")
    print(f"[{ts()}] test_size={args.test_size}")
    print(f"[{ts()}] random_state={args.random_state}")
    print(f"[{ts()}] cv_splits={args.cv_splits}")
    print(f"[{ts()}] search_iter={args.search_iter}")
    print(f"[{ts()}] top_frac={args.top_frac}")
    print(f"[{ts()}] threshold={args.threshold}")
    print(f"[{ts()}] train_only={args.train_only}")
    print(f"[{ts()}] score_only={args.score_only}")

    if not train_py.exists():
        print(f"[{ts()}] ERROR: missing train script: {train_py}")
        raise SystemExit(2)
    if not score_py.exists():
        print(f"[{ts()}] ERROR: missing score script: {score_py}")
        raise SystemExit(2)
    if not os.path.exists(args.xlsx):
        print(f"[{ts()}] ERROR: missing input xlsx: {args.xlsx}")
        raise SystemExit(2)

    do_train = True
    do_score = True
    if args.train_only and not args.score_only:
        do_score = False
    if args.score_only and not args.train_only:
        do_train = False

    t0 = time.perf_counter()
    steps = []

    if do_train:
        cmd_train = [
            sys.executable,
            str(train_py),
            "--xlsx",
            args.xlsx,
            "--sheet",
            args.sheet,
            "--artifacts_dir",
            args.artifacts_dir,
            "--figures_dir",
            args.figures_dir,
            "--test_size",
            str(args.test_size),
            "--random_state",
            str(args.random_state),
            "--cv_splits",
            str(args.cv_splits),
            "--search_iter",
            str(args.search_iter),
        ]
        elapsed = run(cmd_train, repo_root)
        steps.append(("train", elapsed))
        must_exist(args.model_path, "model")
        must_exist(args.metrics_path, "metrics")

    if do_score:
        cmd_score = [
            sys.executable,
            str(score_py),
            "--model",
            args.model_path,
            "--metrics",
            args.metrics_path,
            "--xlsx",
            args.xlsx,
            "--sheet",
            args.sheet,
            "--out_xlsx",
            args.out_scored_xlsx,
            "--top_frac",
            str(args.top_frac),
        ]
        if args.threshold is not None:
            cmd_score += ["--threshold", str(args.threshold)]
        elapsed = run(cmd_score, repo_root)
        steps.append(("score", elapsed))
        must_exist(args.out_scored_xlsx, "scored_xlsx")

    total = time.perf_counter() - t0
    print("")
    print(f"[{ts()}] PIPELINE SUMMARY")
    for name, sec in steps:
        print(f"[{ts()}] step={name} elapsed_s={sec:.3f}")
    print(f"[{ts()}] total_elapsed_s={total:.3f}")
    print(f"[{ts()}] PIPELINE END")


if __name__ == "__main__":
    main()
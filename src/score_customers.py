import os
import json
import argparse
import numpy as np
import pandas as pd
import joblib


def fix_total_charges(df):
    if "TotalCharges" in df.columns and df["TotalCharges"].isna().sum() > 0:
        if "MonthlyCharges" in df.columns and "tenure" in df.columns:
            m = df["TotalCharges"].isna()
            df.loc[m, "TotalCharges"] = df.loc[m, "MonthlyCharges"] * df.loc[m, "tenure"]
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=r"C:\Repos\a3data-churn\artifacts\model_gbm.joblib")
    ap.add_argument("--metrics", default=r"C:\Repos\a3data-churn\artifacts\metrics_gbm_test.json")
    ap.add_argument("--xlsx", default=r"C:\Repos\a3data-churn\data\raw\Customer-Churn.xlsx")
    ap.add_argument("--sheet", default="Customer-Churn")
    ap.add_argument("--out_xlsx", default=r"C:\Repos\a3data-churn\reports\scored_customers.xlsx")
    ap.add_argument("--threshold", type=float, default=None)
    ap.add_argument("--top_frac", type=float, default=0.10)
    args = ap.parse_args()

    print("SCORE START")
    print("MODEL PATH:", args.model)
    print("METRICS PATH:", args.metrics)
    print("INPUT XLSX:", args.xlsx)
    print("SHEET:", args.sheet)
    print("OUT XLSX:", args.out_xlsx)
    print("TOP_FRAC:", args.top_frac)
    print("THRESHOLD (arg):", args.threshold)

    pipe = joblib.load(args.model)
    print("MODEL LOADED")

    threshold = args.threshold
    if threshold is None and os.path.exists(args.metrics):
        with open(args.metrics, "r", encoding="utf-8") as f:
            m = json.load(f)
        if m.get("ks_threshold") is not None:
            threshold = float(m["ks_threshold"])
    print("THRESHOLD (final):", threshold)

    df = pd.read_excel(args.xlsx, sheet_name=args.sheet)
    print("RAW SHAPE:", df.shape)
    print("RAW COLUMNS:", list(df.columns))

    df = fix_total_charges(df)

    id_col = "customerID" if "customerID" in df.columns else None

    X = df.copy()
    if "Churn" in X.columns:
        X = X.drop(columns=["Churn"])
    if "churn_flag" in X.columns:
        X = X.drop(columns=["churn_flag"])

    print("SCORING X SHAPE:", X.shape)

    proba = pipe.predict_proba(X)[:, 1]
    out = pd.DataFrame({"score_churn": proba})

    if id_col is not None:
        out.insert(0, id_col, df[id_col].astype(str))

    out["risk_decile"] = pd.qcut(out["score_churn"], 10, labels=False, duplicates="drop")

    if args.top_frac is not None:
        frac = float(args.top_frac)
        n = len(out)
        k = int(np.ceil(frac * n))
        idx = np.argsort(-out["score_churn"].values)
        flag = np.zeros(n, dtype=int)
        flag[idx[:k]] = 1
        out["action_top_frac"] = flag
        print("TOP_FRAC_K:", k)

    if threshold is not None:
        out["pred_churn_by_threshold"] = (out["score_churn"] >= float(threshold)).astype(int)

    os.makedirs(os.path.dirname(args.out_xlsx), exist_ok=True)
    out.to_excel(args.out_xlsx, index=False)

    print("SAVED:", args.out_xlsx)
    print("OUT SHAPE:", out.shape)
    print("SCORE END")


if __name__ == "__main__":
    main()
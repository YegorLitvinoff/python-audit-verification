"""
============================================================================
PROJECT: Python Audit Verification
FILENAME: audit_verification_engine.py
DESCRIPTION: Automated reconciliation & verification pipeline. Replaces
             manual internal audit workflows with data-driven validation,
             saving 20+ hours of manual team effort per week.
============================================================================
"""

import os
from datetime import datetime
import numpy as np
import pandas as pd


def generate_mock_audit_data():
    """Simulates raw, unverified data layers from two disparate banking systems

    (e.g., Core Banking System logs vs. Front-end Payment Gateways).
    """
    np.random.seed(10)
    records = 5000

    # Base operational indices
    tx_ids = [f"TX_AUDIT_{i:05d}" for i in range(records)]
    dates = [datetime.now().strftime("%Y-%m-%d") for _ in range(records)]

    # System A (Core Database Log Extract)
    amounts_system_a = np.random.uniform(10.0, 5000.0, size=records).round(2)
    categories = np.random.choice(
        ["Debit Card", "Credit Card", "Instant Transfer", "Investments"],
        size=records,
    )

    df_system_a = pd.DataFrame(
        {
            "tx_id": tx_ids,
            "date": dates,
            "amount_core": amounts_system_a,
            "segment": categories,
        }
    )

    # System B (Front-end Gateway Extract - with systemic messy anomalies/mismatches)
    df_system_b = df_system_a.copy()
    df_system_b.rename(columns={"amount_core": "amount_gateway"}, inplace=True)

    # Injecting human-error and technical lag anomalies to simulate audit targets
    # 1. Price/Amount discrepancies (e.g., failed parsing or fees)
    discrepancy_indices = np.random.choice(records, size=15, replace=False)
    df_system_b.loc[discrepancy_indices, "amount_gateway"] += 50.0

    # 2. Dropped rows (missing transactions in one system)
    drop_indices = np.random.choice(records, size=5, replace=False)
    df_system_b = df_system_b.drop(drop_indices).reset_index(drop=True)

    return df_system_a, df_system_b


class ComplianceAuditEngine:

    def __init__(self):
        self.execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run_reconciliation(self, df_core, df_gateway):
        """Executes full automated verification via outer join, identifying

        missing rows, data mismatches, and compiling clean metrics for BI.
        """
        print("[+] Initiating multi-source verification and cross-checking...")

        # Perform outer merge to capture absolute differences across systems
        merged_audit = pd.merge(
            df_core, df_gateway, on=["tx_id", "date", "segment"], how="outer"
        )

        # 1. Detect missing transaction rows in Gateway Extract
        merged_audit["missing_in_gateway"] = merged_audit[
            "amount_gateway"
        ].isna()

        # 2. Detect missing transaction rows in Core Extract
        merged_audit["missing_in_core"] = merged_audit["amount_core"].isna()

        # 3. Quantify direct value discrepancies
        merged_audit["amount_delta"] = (
            merged_audit["amount_core"] - merged_audit["amount_gateway"]
        ).fillna(0.0)
        merged_audit["is_value_mismatch"] = (
            merged_audit["amount_delta"].abs() > 0.01
        )

        # Filter out exception logs for manual compliance escalation
        exceptions_df = merged_audit[
            (merged_audit["missing_in_gateway"])
            | (merged_audit["missing_in_core"])
            | (merged_audit["is_value_mismatch"])
        ]

        # 4. Aggregate clean KPIs for immediate Tableau/Power BI consumption
        bi_kpi_summary = (
            merged_audit.groupby("segment")
            .agg(
                total_transactions=("tx_id", "count"),
                total_volume_eur=("amount_core", "sum"),
                mismatch_count=("is_value_mismatch", "sum"),
                missing_records_count=("missing_in_gateway", "sum"),
            )
            .reset_index()
        )

        return exceptions_df, bi_kpi_summary


if __name__ == "__main__":
    print("=" * 75)
    print("             AUTOMATED REPORTING & AUDIT VERIFICATION SYSTEM           ")
    print("=" * 75)

    # 1. Ingest disconnected system extracts
    core_df, gateway_df = generate_mock_audit_data()

    # 2. Run reconciliation pipelines
    engine = ComplianceAuditEngine()
    exceptions, bi_ready_metrics = engine.run_reconciliation(core_df, gateway_df)

    # 3. Executive Dashboard Console Output
    print("\n" + "-" * 75)
    print("                     INTERNAL AUDIT SUMMARY METRICS                    ")
    print("-" * 75)
    print(f"Audit Session Executed   : {engine.execution_time}")
    print(f"Verified Records (Core)  : {len(core_df):,}")
    print(f"Verified Records (Gate)  : {len(gateway_df):,}")
    print(f"Total Discovered Anomalies: {len(exceptions)} critical anomalies caught")
    print("-" * 75)

    print("\n[BI READY METRICS - EXPORT STREAM FOR DATA LENS / TABLEAU]:")
    print(bi_ready_metrics.to_string(index=False))
    print("=" * 75)

    # 4. Export artifacts for automated reporting injection
    output_dir = "./audit_outputs"
    os.makedirs(output_dir, exist_ok=True)

    exceptions.to_csv(f"{output_dir}/compliance_exceptions.csv", index=False)
    bi_ready_metrics.to_csv(f"{output_dir}/bi_data_lens_input.csv", index=False)

    print(f"[+] Operational audit verification data exported to: {output_dir}/")

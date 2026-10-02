"""
Task B9: Job Queue & State Checkpointer "Resume from Failed Step" Spike
Author: Brij (RepoLens Team)

Demonstrates:
1. A 3-step pipeline (Step 1: Clone & Extract -> Step 2: Score & Summarize -> Step 3: Synthesis)
2. State Checkpointing in PostgreSQL 18 / Persistent Store (run_checkpoints)
3. Simulating a transient failure at Step 2 (e.g. LLM 429 RateLimitError or Worker Crash)
4. Resuming with the same run_id -> Automatically skips Step 1 and resumes from Step 2 -> Completes run.
"""

import os
import sys
import json
import time
import uuid

def get_db_connection():
    try:
        import psycopg
        ports_to_try = [15432, 5432]
        for p in ports_to_try:
            try:
                conn = psycopg.connect(
                    f"host=127.0.0.1 port={p} dbname=postgres user=postgres password=postgres",
                    connect_timeout=1
                )
                return conn, p
            except Exception:
                continue
    except ImportError:
        pass
    return None, None

class PersistentCheckpointer:
    """Manages persistent step-level state checkpointing in PostgreSQL 18 or local fallback."""
    def __init__(self, conn=None):
        self.conn = conn
        self.local_store = {}
        if self.conn:
            self._ensure_pg_table()

    def _ensure_pg_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS run_checkpoints (
                    run_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    step_status TEXT NOT NULL,
                    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (run_id, step_name)
                );
            """)
            self.conn.commit()

    def get_completed_steps(self, run_id: str) -> dict:
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("SELECT step_name, step_status, payload FROM run_checkpoints WHERE run_id = %s;", (run_id,))
                rows = cur.fetchall()
                return {r[0]: {"status": r[1], "payload": r[2]} for r in rows}
        else:
            return self.local_store.get(run_id, {})

    def save_checkpoint(self, run_id: str, step_name: str, status: str, payload: dict):
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO run_checkpoints (run_id, step_name, step_status, payload)
                    VALUES (%s, %s, %s, %s::jsonb)
                    ON CONFLICT (run_id, step_name) 
                    DO UPDATE SET step_status = EXCLUDED.step_status, payload = EXCLUDED.payload, created_at = CURRENT_TIMESTAMP;
                """, (run_id, step_name, status, json.dumps(payload)))
                self.conn.commit()
        else:
            if run_id not in self.local_store:
                self.local_store[run_id] = {}
            self.local_store[run_id][step_name] = {"status": status, "payload": payload}

    def clear_run(self, run_id: str):
        if self.conn:
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM run_checkpoints WHERE run_id = %s;", (run_id,))
                self.conn.commit()
        else:
            self.local_store.pop(run_id, None)

class ResilientAnalysisPipeline:
    """Simulates the 3-step LangGraph / Procrastinate analysis engine."""
    def __init__(self, checkpointer: PersistentCheckpointer, simulate_failure: bool = False):
        self.checkpointer = checkpointer
        self.simulate_failure = simulate_failure

    def execute(self, run_id: str, repo_name: str) -> dict:
        state = {
            "run_id": run_id,
            "repo_name": repo_name,
            "facts": {},
            "scores": {},
            "synthesis": ""
        }

        # Check existing checkpoints for this run_id
        checkpoints = self.checkpointer.get_completed_steps(run_id)

        # -------------------------------------------------------------
        # STEP 1: Clone & Extract Facts
        # -------------------------------------------------------------
        if checkpoints.get("step_1_clone_and_extract", {}).get("status") == "completed":
            print(f"  [Step 1/3] Clone & Extract Facts: [SKIPPED - LOADED FROM CHECKPOINT]")
            state["facts"] = checkpoints["step_1_clone_and_extract"]["payload"]
        else:
            print(f"  [Step 1/3] Clone & Extract Facts: RUNNING...")
            time.sleep(0.15)
            state["facts"] = {
                "repo": repo_name,
                "commit_sha": "440ddd8f1a2b",
                "files_scanned": 42,
                "nloc": 3250,
                "languages": ["Python", "C#"]
            }
            self.checkpointer.save_checkpoint(run_id, "step_1_clone_and_extract", "completed", state["facts"])
            print(f"  [Step 1/3] Clone & Extract Facts: COMPLETED (Checkpoint Saved)")

        # -------------------------------------------------------------
        # STEP 2: Score & Summarize
        # -------------------------------------------------------------
        if checkpoints.get("step_2_score_and_summarize", {}).get("status") == "completed":
            print(f"  [Step 2/3] Score & Summarize:     [SKIPPED - LOADED FROM CHECKPOINT]")
            state["scores"] = checkpoints["step_2_score_and_summarize"]["payload"]
        else:
            print(f"  [Step 2/3] Score & Summarize:     RUNNING...")
            time.sleep(0.15)

            if self.simulate_failure:
                err_payload = {"error": "HTTP 429: Rate limit exceeded during LLM summarization"}
                self.checkpointer.save_checkpoint(run_id, "step_2_score_and_summarize", "failed", err_payload)
                print(f"  [Step 2/3] Score & Summarize:     FAILED! (Simulated LLM 429 RateLimitError)")
                raise RuntimeError("Step 2 Failed: HTTP 429 Rate limit exceeded.")
            
            state["scores"] = {
                "maintainability": 84.5,
                "security": 92.0,
                "dependency_hygiene": 88.0,
                "safety_net": 79.5
            }
            self.checkpointer.save_checkpoint(run_id, "step_2_score_and_summarize", "completed", state["scores"])
            print(f"  [Step 2/3] Score & Summarize:     COMPLETED (Checkpoint Saved)")

        # -------------------------------------------------------------
        # STEP 3: Repo Synthesis & Finalize
        # -------------------------------------------------------------
        if checkpoints.get("step_3_repo_synthesis", {}).get("status") == "completed":
            print(f"  [Step 3/3] Repo Synthesis:        [SKIPPED - LOADED FROM CHECKPOINT]")
            state["synthesis"] = checkpoints["step_3_repo_synthesis"]["payload"]["summary"]
        else:
            print(f"  [Step 3/3] Repo Synthesis:        RUNNING...")
            time.sleep(0.1)
            state["synthesis"] = f"Repository '{repo_name}' is in healthy status with overall score 86/100."
            self.checkpointer.save_checkpoint(run_id, "step_3_repo_synthesis", "completed", {"summary": state["synthesis"]})
            print(f"  [Step 3/3] Repo Synthesis:        COMPLETED (Final Checkpoint Saved)")

        return state

def test_checkpoint_resume():
    """Pytest test verifying step 1 skipping on retry."""
    conn, _ = get_db_connection()
    checkpointer = PersistentCheckpointer(conn)
    test_run_id = f"test_{uuid.uuid4().hex[:8]}"
    
    # 1. Run with failure at step 2
    pipeline_fail = ResilientAnalysisPipeline(checkpointer, simulate_failure=True)
    failed = False
    try:
        pipeline_fail.execute(test_run_id, "test_repo")
    except RuntimeError:
        failed = True
    assert failed, "Expected failure at Step 2"

    # Verify Step 1 is marked completed in checkpointer
    checkpoints = checkpointer.get_completed_steps(test_run_id)
    assert checkpoints["step_1_clone_and_extract"]["status"] == "completed"

    # 2. Retry execution -> must resume from Step 2 and succeed
    pipeline_retry = ResilientAnalysisPipeline(checkpointer, simulate_failure=False)
    final_state = pipeline_retry.execute(test_run_id, "test_repo")
    assert final_state["scores"]["maintainability"] == 84.5
    assert "healthy status" in final_state["synthesis"]

    # Cleanup
    checkpointer.clear_run(test_run_id)

def main():
    print("=========================================================")
    print("RepoLens Spike B9: Job Queue & State Checkpointer Spike")
    print("=========================================================")
    
    conn, port = get_db_connection()
    if conn:
        print(f"[Storage Mode]: Connected to PostgreSQL 18 on port {port} (table: run_checkpoints)\n")
    else:
        print("[Storage Mode]: Local persistent checkpointer (PostgreSQL container offline)\n")

    checkpointer = PersistentCheckpointer(conn)
    demo_run_id = f"run_{int(time.time())}"
    repo_name = "wca_obsidian_vault"

    print("---------------------------------------------------------")
    print(f">> PHASE 1: Initial Run (Simulating Failure at Step 2)")
    print(f"Run ID: {demo_run_id}")
    print("---------------------------------------------------------")
    
    pipeline_run1 = ResilientAnalysisPipeline(checkpointer, simulate_failure=True)
    try:
        pipeline_run1.execute(demo_run_id, repo_name)
    except RuntimeError as e:
        print(f"\n[ALERT] Pipeline Halted: {e}")

    print("\n---------------------------------------------------------")
    print("[STATE] Checkpoint State in Store:")
    checkpoints = checkpointer.get_completed_steps(demo_run_id)
    for step, data in checkpoints.items():
        print(f"   * {step:<28} -> Status: {data['status'].upper()}")
    print("---------------------------------------------------------")

    print("\n---------------------------------------------------------")
    print(f">> PHASE 2: User Clicks 'Retry from Failed Step'")
    print(f"Re-invoking pipeline with same Run ID: {demo_run_id}")
    print("---------------------------------------------------------")
    
    pipeline_run2 = ResilientAnalysisPipeline(checkpointer, simulate_failure=False)
    result = pipeline_run2.execute(demo_run_id, repo_name)

    print("\n=========================================================")
    print("[SUCCESS] Pipeline Resumed & Completed 100%!")
    print(f"Final Synthesis: {result['synthesis']}")
    print("=========================================================")

    # Cleanup demo run
    checkpointer.clear_run(demo_run_id)

if __name__ == "__main__":
    main()

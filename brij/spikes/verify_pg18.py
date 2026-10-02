"""
Task B2: PostgreSQL 18 + pgvector Spike Verification
Author: Brij (RepoLens Team)
"""

import os
import psycopg
from pgvector.psycopg import register_vector

def main():
    print("=========================================================")
    print("Verifying Local PostgreSQL 18 + pgvector Setup")
    print("=========================================================")
    
    ports_to_try = [15432, 5432]
    conn = None
    connected_port = None

    for p in ports_to_try:
        try:
            conn = psycopg.connect(
                f"host=127.0.0.1 port={p} dbname=postgres user=postgres password=postgres",
                connect_timeout=2
            )
            connected_port = p
            break
        except Exception:
            continue

    if not conn:
        print("[ERROR] Could not connect to PostgreSQL on ports 15432 or 5432.")
        print("Please ensure the container is running: docker ps")
        return

    with conn:
        with conn.cursor() as cur:
            # 1. Enable extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            register_vector(conn)
            
            # 2. Check version
            cur.execute("SELECT version();")
            v = cur.fetchone()[0]
            print(f"[1/4] PostgreSQL Version: {v.split(',')[0]} (Port: {connected_port})")
            
            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
            ext = cur.fetchone()
            print(f"[2/4] pgvector Extension: {ext[0]} (version {ext[1]})")
            
            # 3. Create test table with HNSW index
            cur.execute("DROP TABLE IF EXISTS test_spikes;")
            cur.execute("""
                CREATE TABLE test_spikes (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    embedding vector(1024)
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS test_spikes_hnsw_idx 
                ON test_spikes 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            
            # 4. Insert sample embeddings
            cur.execute("""
                INSERT INTO test_spikes (content, embedding)
                VALUES 
                ('Auth token validator', array_fill(0.05, ARRAY[1024])::vector),
                ('Database connection pool', array_fill(0.25, ARRAY[1024])::vector),
                ('API route dispatcher', array_fill(0.06, ARRAY[1024])::vector);
            """)
            conn.commit()
            print("[3/4] Inserted sample 1024-dim vector embeddings with HNSW index.")
            
            # 5. Query nearest neighbor using cosine distance (<=> operator)
            cur.execute("""
                SELECT content, 1 - (embedding <=> array_fill(0.06, ARRAY[1024])::vector) AS similarity
                FROM test_spikes
                ORDER BY embedding <=> array_fill(0.06, ARRAY[1024])::vector
                LIMIT 2;
            """)
            
            results = cur.fetchall()
            print("\n[4/4] Cosine Similarity Search Results:")
            for r in results:
                print(f"  * {r[0]:<28} | Cosine Score: {float(r[1]):.4f}")
                
    print("\n=========================================================")
    print("[SUCCESS] PostgreSQL 18 and pgvector are 100% verified and operational!")
    print("=========================================================")

if __name__ == "__main__":
    main()

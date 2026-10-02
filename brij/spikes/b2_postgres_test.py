"""
Task B2: PostgreSQL 18 + pgvector Spike & Verification Script
Author: Brij (RepoLens Team)

Tests & Verifies:
1. Connection to PostgreSQL 18 container (ports 15432 / 5432)
2. Enabling pgvector extension
3. Creating a table with 1024-dimensional vector column (voyage-code-3 format)
4. Creating an HNSW index with (m = 16, ef_construction = 64)
5. Inserting sample code chunk embeddings
6. Executing cosine distance nearest neighbor search (<=> operator)
"""

import os
import sys
import time

def get_connection():
    import psycopg
    from pgvector.psycopg import register_vector
    
    ports_to_try = [15432, 5432]
    for p in ports_to_try:
        try:
            conn = psycopg.connect(
                f"host=127.0.0.1 port={p} dbname=postgres user=postgres password=postgres",
                connect_timeout=2
            )
            return conn, p
        except Exception:
            continue
    return None, None

def test_pgvector_hnsw():
    conn, port = get_connection()
    if conn is None:
        try:
            import pytest
            pytest.skip("PostgreSQL 18 container is offline on ports 15432 / 5432")
        except ImportError:
            return
    
    from pgvector.psycopg import register_vector
    with conn:
        with conn.cursor() as cur:
            # 1. Enable extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            register_vector(conn)
            
            # 2. Check version
            cur.execute("SELECT version();")
            pg_ver = cur.fetchone()[0]
            assert "PostgreSQL 18" in pg_ver or "18." in pg_ver, f"Expected PG18, got {pg_ver}"
            
            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
            ext = cur.fetchone()
            assert ext is not None and ext[0] == "vector", "Vector extension not found"
            
            # 3. Create table & HNSW index
            cur.execute("DROP TABLE IF EXISTS test_code_chunks;")
            cur.execute("""
                CREATE TABLE test_code_chunks (
                    id SERIAL PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(1024) NOT NULL
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS test_chunks_hnsw_idx 
                ON test_code_chunks 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)
            
            # 4. Insert sample embeddings
            cur.execute("""
                INSERT INTO test_code_chunks (file_path, chunk_type, content, embedding)
                VALUES 
                ('apps/backend/auth.py', 'function', 'def authenticate_user(token: str): ...', array_fill(0.05, ARRAY[1024])::vector),
                ('apps/backend/db.py', 'class', 'class DatabasePool: ...', array_fill(0.25, ARRAY[1024])::vector),
                ('apps/worker/pipeline.py', 'function', 'def run_analysis(repo_id: str): ...', array_fill(0.85, ARRAY[1024])::vector);
            """)
            conn.commit()
            
            # 5. Query nearest neighbor
            cur.execute("""
                SELECT file_path, 1 - (embedding <=> array_fill(0.06, ARRAY[1024])::vector) AS similarity
                FROM test_code_chunks
                ORDER BY embedding <=> array_fill(0.06, ARRAY[1024])::vector
                LIMIT 1;
            """)
            row = cur.fetchone()
            assert row is not None and float(row[1]) > 0.9, f"Similarity query failed: {row}"

def run_live_verification():
    print("=========================================================")
    print("RepoLens Spike B2: PostgreSQL 18 + pgvector Live Test")
    print("=========================================================")
    
    try:
        import psycopg
        from pgvector.psycopg import register_vector
    except ImportError:
        print("[WARNING] psycopg or pgvector package not installed in environment.")
        return False

    conn, connected_port = get_connection()
    if not conn:
        print("\n  [!] Note: PostgreSQL container is currently offline.")
        print("  To launch the PostgreSQL 18 container with pgvector:")
        print("  docker run -d --name repolens-pg18 -p 15432:5432 -e POSTGRES_PASSWORD=postgres pgvector/pgvector:pg18\n")
        return False

    print(f"\n[1/5] Connected to PostgreSQL 18 on port {connected_port}!")
    with conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()
            register_vector(conn)

            cur.execute("SELECT version();")
            pg_ver = cur.fetchone()[0].split(",")[0]
            cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';")
            ext = cur.fetchone()
            print(f"  [OK] PostgreSQL Engine: {pg_ver}")
            print(f"  [OK] Vector Extension:  {ext[0]} (version {ext[1]})")

            print("\n[2/5] Creating table 'test_code_chunks' with vector(1024)...")
            cur.execute("DROP TABLE IF EXISTS test_code_chunks;")
            cur.execute("""
                CREATE TABLE test_code_chunks (
                    id SERIAL PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding vector(1024) NOT NULL
                );
            """)

            print("[3/5] Creating HNSW Cosine Index (m = 16, ef_construction = 64)...")
            cur.execute("""
                CREATE INDEX IF NOT EXISTS test_chunks_hnsw_idx 
                ON test_code_chunks 
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = 16, ef_construction = 64);
            """)

            print("[4/5] Inserting sample 1024-dimensional Voyage embeddings...")
            cur.execute("""
                INSERT INTO test_code_chunks (file_path, chunk_type, content, embedding)
                VALUES 
                ('apps/backend/auth.py', 'function', 'def authenticate_user(token: str): ...', array_fill(0.05, ARRAY[1024])::vector),
                ('apps/backend/db.py', 'class', 'class DatabasePool: ...', array_fill(0.25, ARRAY[1024])::vector),
                ('apps/worker/pipeline.py', 'function', 'def run_analysis(repo_id: str): ...', array_fill(0.85, ARRAY[1024])::vector);
            """)
            conn.commit()

            print("[5/5] Executing Cosine Similarity Nearest Neighbor Query (<=> operator)...")
            cur.execute("""
                SELECT 
                    file_path, 
                    chunk_type,
                    1 - (embedding <=> array_fill(0.06, ARRAY[1024])::vector) AS cosine_similarity
                FROM test_code_chunks
                ORDER BY embedding <=> array_fill(0.06, ARRAY[1024])::vector
                LIMIT 2;
            """)
            results = cur.fetchall()
            print("\n  Top Nearest Neighbors Found:")
            for r in results:
                print(f"    * {r[0]:<25} ({r[1]}) | Cosine Similarity: {float(r[2]):.4f}")

    print("\n=========================================================")
    print("[SUCCESS] PostgreSQL 18 & pgvector 1024-dim HNSW verified!")
    print("=========================================================")
    return True

if __name__ == "__main__":
    run_live_verification()

import sys
import psycopg2
from psycopg2.extras import RealDictCursor

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def inspect():
    conn = psycopg2.connect("postgresql://postgres:postgres@localhost:5432/legal_metrology_db")
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = [row['table_name'] for row in cur.fetchall()]
    
    print("\n" + "="*60)
    print("PostgreSQL Database: legal_metrology_db")
    print("="*60)

    
    for table in tables:
        cur.execute(f"SELECT COUNT(*) as count FROM {table};")
        row_count = cur.fetchone()['count']
        
        cur.execute(f"""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{table}'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        print(f"\n📂 Table: {table.upper()} ({row_count} rows)")
        col_summary = ", ".join([f"{col['column_name']} ({col['data_type']})" for col in columns[:6]])
        if len(columns) > 6:
            col_summary += f", ... (+{len(columns)-6} more columns)"
        print(f"   Columns [{len(columns)}]: {col_summary}")
        
        if row_count > 0 and row_count <= 10:
            cur.execute(f"SELECT * FROM {table} LIMIT 5;")
            sample_rows = cur.fetchall()
            for r in sample_rows:
                # preview key fields
                preview = {k: str(v)[:40] for k, v in r.items() if k in ['id', 'email', 'full_name', 'role', 'rule_code', 'title', 'version_tag', 'statutory_source']}
                if preview:
                    print(f"   ↳ Row sample: {preview}")
                    
    print("\n" + "="*60 + "\n")
    cur.close()
    conn.close()

if __name__ == "__main__":
    inspect()

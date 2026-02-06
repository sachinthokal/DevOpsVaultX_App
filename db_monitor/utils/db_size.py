from django.db import connection
import logging

# Logger initialize (central logger)
logger = logging.getLogger("request.audit")

def generate_db_size_report():
    """
    Generates database size report. 
    Errors are automatically captured by the central middleware.
    """
    logger.debug("Executing SQL query for database size report")

    with connection.cursor() as cursor:
        cursor.execute("""
            WITH db AS (
                SELECT current_database() AS name,
                       pg_database_size(current_database()) AS size_bytes
            )
            SELECT
                db.name,
                db.size_bytes,
                t.relname,
                pg_relation_size(t.relid) AS data_bytes,
                pg_indexes_size(t.relid) AS index_bytes,
                pg_total_relation_size(t.relid) AS total_bytes
            FROM db, pg_statio_user_tables t
            ORDER BY pg_total_relation_size(t.relid) DESC
            LIMIT 20;
        """)
        rows = cursor.fetchall()
    logger.debug(f"Fetched {len(rows)} tables from PostgreSQL")
    if not rows:
        logger.debug("No rows found in database report query")
        return {
            "database": "N/A", "database_size": "0 bytes",
            "total_data": "0 bytes", "total_index": "0 bytes",
            "db_percentage": 0, "DB_Bar_Cap": 102.4,
            "db_bar_color": "green", "tables": []
        }

    # ---------- helpers ----------
    def human_readable(size_bytes):
        size_bytes = float(size_bytes or 0)
        if size_bytes >= 1024**3:
            return f"{size_bytes / (1024**3):.2f} GB"
        elif size_bytes >= 1024**2:
            return f"{size_bytes / (1024**2):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.0f} KB"
        return f"{int(size_bytes)} bytes"

    def bytes_to_mb(b):
        return (b or 0) / (1024 * 1024)

    # ---------- TABLE LEVEL ----------
    MAX_BAR_MB = 102.4 
    tables = []

    for r in rows:
        total_mb = bytes_to_mb(r[5])
        # Table level debug (loop)
        logger.debug(f"Processing table: {r[2]} | Size: {total_mb:.2f} MB")
        percentage = max(1, min((total_mb / MAX_BAR_MB) * 100, 100))

        if total_mb > 400:
            status_emoji, bar_color = "🔴", "red"
        elif total_mb > 200:
            status_emoji, bar_color = "🟡", "yellow"
        else:
            status_emoji, bar_color = "🟢", "green"

        tables.append({
            "table": r[2],
            "data": human_readable(r[3]),
            "index": human_readable(r[4]),
            "total": human_readable(r[5]),
            "percentage": round(percentage, 1),
            "status_emoji": status_emoji,
            "bar_color": bar_color,
            "Table_Bar_Cap": MAX_BAR_MB
        })

    # ---------- SUMMARY ----------
    total_data_bytes = sum((r[3] or 0) for r in rows)
    total_index_bytes = sum((r[4] or 0) for r in rows)
    database_bytes = rows[0][1]
    database_mb = bytes_to_mb(database_bytes)

    MAX_DB_MB = 102.4 
    db_percentage = min((database_mb / MAX_DB_MB) * 100, 100)

    if database_mb > 800:
        db_bar_color = "red"
    elif database_mb > 400:
        db_bar_color = "yellow"
    else:
        db_bar_color = "green"

    logger.debug(f"Final DB Summary: {rows[0][0]} | Total Size: {database_mb:.2f} MB")
    return {
        "database": rows[0][0],
        "database_size": human_readable(database_bytes),
        "total_data": human_readable(total_data_bytes),
        "total_index": human_readable(total_index_bytes),
        "db_percentage": round(db_percentage, 1),
        "DB_Bar_Cap": MAX_DB_MB,
        "db_bar_color": db_bar_color,
        "tables": tables
    }
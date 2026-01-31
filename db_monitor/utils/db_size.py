from django.db import connection
import logging

# Logger client
logger = logging.getLogger(__name__)

def generate_db_size_report():
    logger.info("Generating database size report")

    try:
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
            logger.debug(f"Fetched {len(rows)} tables for DB report")
    except Exception as e:
        logger.error("Error fetching database size report", exc_info=True)
        return {
            "database": "N/A",
            "database_size": "N/A",
            "total_data": "N/A",
            "total_index": "N/A",
            "db_percentage": 0,
            "DB_Bar_Cap": 0,
            "db_bar_color": "red",
            "tables": []
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
    MAX_BAR_MB = 102.4 # 10 MB = 100% bar width

    tables = []
    for r in rows:
        total_mb = bytes_to_mb(r[5])

        # Percentage based on fixed cap
        percentage = (total_mb / MAX_BAR_MB) * 100
        percentage = max(1, min(percentage, 100))  # clamp 1–100%

        # Color thresholds (MB)
        if total_mb > 400:
            status_emoji = "🔴"
            bar_color = "red"
        elif total_mb > 200:
            status_emoji = "🟡"
            bar_color = "yellow"
        else:
            status_emoji = "🟢"
            bar_color = "green"

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
        logger.debug(f"Table {r[2]}: {human_readable(r[5])}, status: {status_emoji}")

    # ---------- SUMMARY ----------
    total_data_bytes = sum((r[3] or 0) for r in rows)
    total_index_bytes = sum((r[4] or 0) for r in rows)
    database_bytes = rows[0][1] if rows else 0
    database_mb = bytes_to_mb(database_bytes)

    # DB SCALE (Fixed 1 GB = 100%)
    MAX_DB_MB = 102.4 # 10 MB = 100% bar width
    db_percentage = min((database_mb / MAX_DB_MB) * 100, 100)

    if database_mb > 800:
        db_bar_color = "red"
    elif database_mb > 400:
        db_bar_color = "yellow"
    else:
        db_bar_color = "green"

    logger.info(f"Database '{rows[0][0] if rows else 'N/A'}' size: {human_readable(database_bytes)}, status color: {db_bar_color}")

    return {
        "database": rows[0][0] if rows else "N/A",
        "database_size": human_readable(database_bytes),
        "total_data": human_readable(total_data_bytes),
        "total_index": human_readable(total_index_bytes),
        "db_percentage": db_percentage,
        "DB_Bar_Cap": MAX_DB_MB,
        "db_bar_color": db_bar_color,
        "tables": tables
    }

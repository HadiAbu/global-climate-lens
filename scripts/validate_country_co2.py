# scripts/validate_country_co2.py
from sqlalchemy import create_engine, text
import os
import sys
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL_LOCAL or DATABASE_URL is not set")
    sys.exit(1)


engine = create_engine(DATABASE_URL)


def main() -> None:
    with engine.connect() as conn:
        # 1) Row count
        total = conn.execute(
            text("SELECT COUNT(*) FROM fact_country_co2_yearly")
        ).scalar()

        print(f"Total fact rows: {total:,}")

        if total < 10_000:
            print("❌ Row count too low — load likely failed")
            sys.exit(1)

        # 2) Orphan join check
        orphan = conn.execute(
            text(
                """
            SELECT COUNT(*)
            FROM fact_country_co2_yearly f
            LEFT JOIN dim_country d ON d.iso3 = f.iso3
            WHERE d.iso3 IS NULL
        """
            )
        ).scalar()

        print(f"Orphan rows: {orphan}")

        if orphan != 0:
            print("❌ Orphan rows detected — country join is broken")
            sys.exit(1)

        # 3) Sanity sample
        rows = conn.execute(
            text(
                """
            SELECT iso3, year, co2_total_mt, co2_per_capita
            FROM fact_country_co2_yearly
            WHERE iso3 IN ('USA', 'CHN', 'IND')
            ORDER BY iso3, year
            LIMIT 12
        """
            )
        ).fetchall()

        print("\nSample rows:")
        for r in rows:
            print(r)

    print("\n✅ Validation passed")


if __name__ == "__main__":
    main()

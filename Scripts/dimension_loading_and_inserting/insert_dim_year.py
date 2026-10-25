import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL is missing from the project .env file')

import pandas as pd
from sqlalchemy import create_engine

# ---- 1. Load the master year list ----
year_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\dim_year_master_list.csv")

print(f"Loading {len(year_df)} years into dim_year table...")
print(year_df)
print()

# ---- 2. Connect to PostgreSQL ----
engine = create_engine(DATABASE_URL)

# ---- 3. Insert into dim_year table ----
year_df.to_sql('dim_year', engine, if_exists='append', index=False)

print("Successfully loaded years into dim_year table!")
print()

# ---- 4. Verify ----
verify_df = pd.read_sql('SELECT * FROM dim_year ORDER BY year_id', engine)
print(f"Verification: {len(verify_df)} rows now in dim_year table")
print(verify_df)
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL is missing from the project .env file')

import pandas as pd
from sqlalchemy import create_engine

# ---- 1. Load the master management list ----
management_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\dim_management_master_list.csv")

print(f"Loading {len(management_df)} management values into dim_management table...")
print(management_df)
print()

# ---- 2. Connect to PostgreSQL ----
engine = create_engine(DATABASE_URL)

# ---- 3. Insert into dim_management table ----
management_df.to_sql('dim_management', engine, if_exists='append', index=False)

print("Successfully loaded management values into dim_management table!")
print()

# ---- 4. Verify ----
verify_df = pd.read_sql('SELECT * FROM dim_management ORDER BY management_id', engine)
print(f"Verification: {len(verify_df)} rows now in dim_management table")
print(verify_df)
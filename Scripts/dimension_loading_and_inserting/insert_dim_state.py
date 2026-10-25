import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL is missing from the project .env file')

import pandas as pd
from sqlalchemy import create_engine

# ---- 1. Load the master state list we already built and verified ----
state_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\dim_state_master_list.csv")

print(f"Loading {len(state_df)} states into dim_state table...")
print(state_df.head())
print()

# ---- 2. Connect to PostgreSQL ----
engine = create_engine(DATABASE_URL)

# ---- 3. Insert into dim_state table ----
# if_exists='append' adds these rows to the existing empty table 
# (does NOT delete/recreate the table structure)
state_df.to_sql('dim_state', engine, if_exists='append', index=False)

print("Successfully loaded states into dim_state table!")
print()

# ---- 4. Verify by reading the data back from PostgreSQL ----
verify_df = pd.read_sql('SELECT * FROM dim_state ORDER BY state_id', engine)
print(f"Verification: {len(verify_df)} rows now in dim_state table")
print(verify_df)
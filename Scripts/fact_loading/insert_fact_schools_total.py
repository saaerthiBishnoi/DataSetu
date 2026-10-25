import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError('DATABASE_URL is missing from the project .env file')

import pandas as pd
from sqlalchemy import create_engine

# ---- 1. Connect to PostgreSQL ----
engine = create_engine(DATABASE_URL)

# ---- 2. Load the cleaned fact data ----
fact_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_schools_total.csv")
print(f"Loaded {len(fact_df)} rows from cleaned file")
print(fact_df.head())
print()

# ---- 3. Load the dimension tables (to look up IDs) ----
dim_state = pd.read_sql('SELECT * FROM dim_state', engine)
dim_year = pd.read_sql('SELECT * FROM dim_year', engine)
dim_management = pd.read_sql('SELECT * FROM dim_management', engine)

# ---- 4. Replace text values with their corresponding IDs (this is the "lookup") ----
fact_df = fact_df.merge(dim_state, left_on='state', right_on='state_name', how='left')
fact_df = fact_df.merge(dim_year, left_on='year', right_on='year_value', how='left')
fact_df = fact_df.merge(dim_management, left_on='management', right_on='management_name', how='left')

# ---- 5. Check for any lookup failures (a name that didn't match any dimension row) ----
missing_state = fact_df[fact_df['state_id'].isna()]
missing_year = fact_df[fact_df['year_id'].isna()]
missing_mgmt = fact_df[fact_df['management_id'].isna()]

if len(missing_state) > 0:
    print(f"WARNING: {len(missing_state)} rows have unmatched state names:")
    print(missing_state['state'].unique())
if len(missing_year) > 0:
    print(f"WARNING: {len(missing_year)} rows have unmatched years:")
    print(missing_year['year'].unique())
if len(missing_mgmt) > 0:
    print(f"WARNING: {len(missing_mgmt)} rows have unmatched management values:")
    print(missing_mgmt['management'].unique())

# ---- 6. Keep only the columns the fact table actually needs ----
final_df = fact_df[['state_id', 'year_id', 'management_id', 'school_count']].copy()

# Drop any rows where a lookup failed (shouldn't happen if dimensions are correct, but safety check)
before_count = len(final_df)
final_df = final_df.dropna()
after_count = len(final_df)
if before_count != after_count:
    print(f"\nDROPPED {before_count - after_count} rows due to failed lookups - investigate before proceeding!")

# Convert ID columns to proper integer type (merge can turn them into floats)
final_df['state_id'] = final_df['state_id'].astype(int)
final_df['year_id'] = final_df['year_id'].astype(int)
final_df['management_id'] = final_df['management_id'].astype(int)

# ---- 7. Insert into fact_schools_total table ----
final_df.to_sql('fact_schools_total', engine, if_exists='append', index=False)
print(f"\nSuccessfully loaded {len(final_df)} rows into fact_schools_total!")

# ---- 8. Verify ----
verify_df = pd.read_sql('SELECT COUNT(*) as row_count FROM fact_schools_total', engine)
print(f"\nVerification: {verify_df['row_count'][0]} rows now in fact_schools_total table")
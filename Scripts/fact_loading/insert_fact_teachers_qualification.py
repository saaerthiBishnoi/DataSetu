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
fact_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_teachers_by_qualification.csv")
print(f"Loaded {len(fact_df)} rows from cleaned file")
print(fact_df.head())
print()

# ---- 3. Load the dimension tables ----
dim_state = pd.read_sql('SELECT * FROM dim_state', engine)
dim_year = pd.read_sql('SELECT * FROM dim_year', engine)
dim_qualification = pd.read_sql('SELECT * FROM dim_qualification', engine)

# ---- 4. Lookup IDs ----
fact_df = fact_df.merge(dim_state, left_on='state', right_on='state_name', how='left')
fact_df = fact_df.merge(dim_year, left_on='year', right_on='year_value', how='left')
fact_df = fact_df.merge(dim_qualification, left_on='qualification', right_on='qualification_name', how='left')

# ---- 5. Check for lookup failures ----
for col, name in [('state_id', 'state'), ('year_id', 'year'), ('qualification_id', 'qualification')]:
    missing = fact_df[fact_df[col].isna()]
    if len(missing) > 0:
        print(f"WARNING: {len(missing)} rows have unmatched {name} values:")
        print(missing[name].unique())

# ---- 6. Keep only needed columns ----
final_df = fact_df[['state_id', 'year_id', 'qualification_id', 'teacher_pct']].copy()

before_count = len(final_df)
final_df = final_df.dropna()
after_count = len(final_df)
if before_count != after_count:
    print(f"\nDROPPED {before_count - after_count} rows due to failed lookups - investigate!")

final_df['state_id'] = final_df['state_id'].astype(int)
final_df['year_id'] = final_df['year_id'].astype(int)
final_df['qualification_id'] = final_df['qualification_id'].astype(int)

# ---- 7. Insert ----
final_df.to_sql('fact_teachers_qualification', engine, if_exists='append', index=False)
print(f"\nSuccessfully loaded {len(final_df)} rows into fact_teachers_qualification!")

# ---- 8. Verify ----
verify_df = pd.read_sql('SELECT COUNT(*) as row_count FROM fact_teachers_qualification', engine)
print(f"\nVerification: {verify_df['row_count'][0]} rows now in fact_teachers_qualification table")
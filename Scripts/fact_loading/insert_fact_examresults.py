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

# ---- 2. Load both cleaned fact files and tag each with its grade ----
grade10_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_exam_results_grade10.csv")
grade10_df['grade'] = 'X'

grade12_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_exam_results_grade12.csv")
grade12_df['grade'] = 'XII'

# ---- 3. Combine into one dataframe ----
fact_df = pd.concat([grade10_df, grade12_df], ignore_index=True)
print(f"Combined {len(grade10_df)} (Grade X) + {len(grade12_df)} (Grade XII) = {len(fact_df)} total rows")
print(fact_df.head())
print()

# ---- 4. Load the dimension tables ----
dim_state = pd.read_sql('SELECT * FROM dim_state', engine)
dim_year = pd.read_sql('SELECT * FROM dim_year', engine)
dim_management = pd.read_sql('SELECT * FROM dim_management', engine)

# ---- 5. Lookup IDs ----
fact_df = fact_df.merge(dim_state, left_on='state', right_on='state_name', how='left')
fact_df = fact_df.merge(dim_year, left_on='year', right_on='year_value', how='left')
fact_df = fact_df.merge(dim_management, left_on='management', right_on='management_name', how='left')

# ---- 6. Check for lookup failures ----
for col, name in [('state_id', 'state'), ('year_id', 'year'), ('management_id', 'management')]:
    missing = fact_df[fact_df[col].isna()]
    if len(missing) > 0:
        print(f"WARNING: {len(missing)} rows have unmatched {name} values:")
        print(missing[name].unique())

# ---- 7. Keep only needed columns ----
final_df = fact_df[['state_id', 'year_id', 'management_id', 'grade', 'appeared', 'pass_pct']].copy()

before_count = len(final_df)
final_df = final_df.dropna()
after_count = len(final_df)
if before_count != after_count:
    print(f"\nDROPPED {before_count - after_count} rows due to failed lookups - investigate!")

final_df['state_id'] = final_df['state_id'].astype(int)
final_df['year_id'] = final_df['year_id'].astype(int)
final_df['management_id'] = final_df['management_id'].astype(int)

# ---- 8. Insert ----
final_df.to_sql('fact_examresults', engine, if_exists='append', index=False)
print(f"\nSuccessfully loaded {len(final_df)} rows into fact_examresults!")

# ---- 9. Verify ----
verify_df = pd.read_sql('SELECT grade, COUNT(*) as row_count FROM fact_examresults GROUP BY grade', engine)
print(f"\nVerification (by grade):")
print(verify_df)
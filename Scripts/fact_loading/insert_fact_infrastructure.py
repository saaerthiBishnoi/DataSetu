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

# ---- 2. Load all 5 infrastructure files, standardize columns, tag facility_type ----

internet_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_internet_facility.csv")
internet_df = internet_df.rename(columns={'schools_with_facility': 'schools_with_facility', 'pct_with_facility': 'pct_with_facility'})
internet_df['facility_type'] = 'Internet'

computer_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_computer_facility.csv")
computer_df['facility_type'] = 'Computer'

water_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_drinking_water.csv")
water_df = water_df.rename(columns={'schools_with_water': 'schools_with_facility', 'pct_with_water': 'pct_with_facility'})
water_df['facility_type'] = 'Drinking Water'
# Drop the "functional" columns for this unioned table (keep it simple - 
# functional water tracked separately if needed later)
water_df = water_df.drop(columns=['schools_with_functional_water', 'pct_with_functional_water'])

boys_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_boys_toilet.csv")
boys_df = boys_df.rename(columns={'schools_with_toilet': 'schools_with_facility', 'pct_with_toilet': 'pct_with_facility'})
boys_df['facility_type'] = 'Boys Toilet'
boys_df = boys_df.drop(columns=['schools_with_functional_toilet', 'pct_with_functional_toilet'])

girls_df = pd.read_csv(r"D:\Downloads\DataSetu\Cleaned\fact_girls_toilet.csv")
girls_df = girls_df.rename(columns={'schools_with_toilet': 'schools_with_facility', 'pct_with_toilet': 'pct_with_facility'})
girls_df['facility_type'] = 'Girls Toilet'
girls_df = girls_df.drop(columns=['schools_with_functional_toilet', 'pct_with_functional_toilet'])

# ---- 3. Combine all 5 into one dataframe ----
fact_df = pd.concat([internet_df, computer_df, water_df, boys_df, girls_df], ignore_index=True)
print(f"Combined all 5 infrastructure files: {len(fact_df)} total rows")
print(fact_df['facility_type'].value_counts())
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
final_df = fact_df[['state_id', 'year_id', 'management_id', 'facility_type', 
                     'total_schools', 'schools_with_facility', 'pct_with_facility']].copy()

before_count = len(final_df)
final_df = final_df.dropna()
after_count = len(final_df)
if before_count != after_count:
    print(f"\nDROPPED {before_count - after_count} rows due to failed lookups - investigate!")

final_df['state_id'] = final_df['state_id'].astype(int)
final_df['year_id'] = final_df['year_id'].astype(int)
final_df['management_id'] = final_df['management_id'].astype(int)

# ---- 8. Insert ----
final_df.to_sql('fact_infrastructure', engine, if_exists='append', index=False)
print(f"\nSuccessfully loaded {len(final_df)} rows into fact_infrastructure!")

# ---- 9. Verify ----
verify_df = pd.read_sql('SELECT facility_type, COUNT(*) as row_count FROM fact_infrastructure GROUP BY facility_type', engine)
print(f"\nVerification (by facility_type):")
print(verify_df)
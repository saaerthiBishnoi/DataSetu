import pandas as pd
import numpy as np

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\1-Unified District Information System For Education (UDISE) - Flash Statistics\Examination Results for Grade X by Management.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_exam_results_grade10.csv"

# ---- 2. LOAD ----
df = pd.read_csv(input_path)

print("Columns found in file:")
print(df.columns.tolist())
print()

# ---- 3. RENAME core columns ----
df = df.rename(columns={
    'State/Ut Name': 'state',
    'Year': 'year_raw',
    'Type Of School Management': 'management',
})
df['year'] = df['year_raw'].astype(str).str.extract(r'(\d{4})').astype(int)
df = df.rename(columns={
    'Appeared In Grade X (UOM:Number), Scaling Factor:1': 'appeared',
    'Pass Percentage In Grade X (UOM:%(Percentage)), Scaling Factor:1': 'pass_pct',
})

# ---- 4. FIX state/management issues ----
# Drop "All India" - national aggregate, not a real state
df = df[df['state'] != 'All India']

# Drop "Total" management rows - check-total, not a real category
df = df[df['management'] != 'Total']

# Merge pre-2020 UT names into post-2020 combined name (matches Files 1, 2, 3)
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 5. FLAG impossible pass_pct values (data quality issue, not fixed - documented) ----
bad_pct = df[(df['pass_pct'] > 100) | (df['pass_pct'] < 0)]
if len(bad_pct) > 0:
    print(f"WARNING: {len(bad_pct)} rows have pass_pct outside 0-100 range (source data issue):")
    print(bad_pct[['state', 'year', 'management', 'appeared', 'pass_pct']])
    print()

# ---- 6. MERGE duplicate rows (from Dadra/Daman rename) ----
# "appeared" (a count) -> SUM
# "pass_pct" (a percentage) -> WEIGHTED AVERAGE using "appeared" as weight
# (simple average or sum would be mathematically wrong for percentages)
def weighted_avg(group):
    total_appeared = group['appeared'].sum()
    if total_appeared == 0:
        weighted_pass = 0
    else:
        weighted_pass = (group['pass_pct'] * group['appeared']).sum() / total_appeared
    return pd.Series({'appeared': total_appeared, 'pass_pct': round(weighted_pass, 2)})

df = df.groupby(['state', 'year', 'management']).apply(weighted_avg, include_groups=False).reset_index()

# ---- 7. This file is ALREADY LONG FORMAT - no melt needed ----
long_df = df.copy()

print("Total rows (already long format, cleaned):", len(long_df))
print("Unique states:", long_df['state'].nunique())
print(sorted(long_df['state'].unique()))
print()
print(long_df.head(10))

# ---- 8. SAVE cleaned file ----
long_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
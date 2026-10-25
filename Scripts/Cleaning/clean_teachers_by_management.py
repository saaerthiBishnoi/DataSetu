import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\1-Unified District Information System For Education (UDISE) - Flash Statistics\Distribution of Teachers by Management.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_teachers_by_management.csv"

# ---- 2. LOAD ----
df = pd.read_csv(input_path)

print("Columns found in file:")
print(df.columns.tolist())
print()

# ---- 3. RENAME core columns to clean, consistent names ----
df = df.rename(columns={
    'State/Ut Name': 'state',
    'Year': 'year_raw',
    'Gender': 'gender',
})

# Clean Year: "Financial Year (Apr - Mar), 2017" -> 2017
df['year'] = df['year_raw'].astype(str).str.extract(r'(\d{4})').astype(int)

# ---- 4. FIX state name issues ----
# Drop "India" - it's a national aggregate row, not a real state
df = df[df['state'] != 'India']

# Merge pre-2020 UT names into the post-2020 combined name
# (matches naming used in Files 1 and 2)
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 5. RENAME the 4 management percentage columns directly to category names ----
mgmt_column_map = {
    'Teachers In Government Schools (UOM:%(Percentage)), Scaling Factor:1': 'Government',
    'Teachers In Government Aided Schools (UOM:%(Percentage)), Scaling Factor:1': 'Government Aided',
    'Teachers In Private Unaided Schools (UOM:%(Percentage)), Scaling Factor:1': 'Private Unaided',
    'Teachers In Other Management Schools (UOM:%(Percentage)), Scaling Factor:1': 'Other',
}
df = df.rename(columns=mgmt_column_map)

# The 5th column ("Across All Management Types") is a check total, NOT a category - keep separately
df = df.rename(columns={
    'Teachers Across All Management Types (UOM:%(Percentage)), Scaling Factor:1': 'total_pct_reported'
})

mgmt_cols = list(mgmt_column_map.values())

# ---- 6. MERGE the now-duplicated state rows (from the Dadra/Daman rename above) ----
# Two old rows now share the same new state name for the same year+gender - sum them
value_cols = mgmt_cols + ['total_pct_reported']
df = df.groupby(['state', 'year', 'gender'], as_index=False)[value_cols].sum()

# ---- 7. MELT: wide -> long (management becomes a row value) ----
long_df = df.melt(
    id_vars=['state', 'year', 'gender'],
    value_vars=mgmt_cols,
    var_name='management',
    value_name='teacher_pct'
)

# ---- 8. SANITY CHECK: sum of 4 category percentages vs reported "All Management" total ----
check = long_df.groupby(['state', 'year', 'gender'], as_index=False)['teacher_pct'].sum()
check = check.rename(columns={'teacher_pct': 'recomputed_total_pct'})
verify = df[['state', 'year', 'gender', 'total_pct_reported']].merge(
    check, on=['state', 'year', 'gender']
)
# Allow tolerance of 2 now (merged rows may compound rounding slightly)
verify['match'] = (verify['recomputed_total_pct'] - verify['total_pct_reported']).abs() <= 2

print("Total rows after melt:", len(long_df))
print("Unique states (verify count and no typos):")
print(sorted(long_df['state'].unique()))
print("Total unique states:", long_df['state'].nunique())
print()
print("Sanity check results:")
print(verify['match'].value_counts())
mismatches = verify[~verify['match']]
if len(mismatches) > 0:
    print(f"\n{len(mismatches)} rows outside tolerance - needs review:")
    print(mismatches)
else:
    print("All totals within acceptable rounding tolerance.")

# ---- 9. SAVE cleaned file ----
long_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
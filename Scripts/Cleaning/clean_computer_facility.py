import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\2-Unified District Information System for Education Plus (UDISE+)\Schools by Management and Availability of Computer Facility.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_computer_facility.csv"

# ---- 2. LOAD ----
df = pd.read_csv(input_path)

print("Columns found in file:")
print(df.columns.tolist())
print()

# ---- 3. RENAME core columns ----
df = df.rename(columns={
    'State/Ut Name': 'state',
    'Year': 'year_raw',
})
df['year'] = df['year_raw'].astype(str).str.extract(r'(\d{4})').astype(int)

# ---- 4. FIX state issues ----
df = df[df['state'] != 'India']
df['state'] = df['state'].str.replace(r'(?<=[a-z])And(?=s?$)', 'and', regex=True)

# This file has FOUR different Dadra/Daman spellings across different years
# (unlike File 9, where merging was already mostly done) - all map to the 
# same standard merged name
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Daman And Diu And Dadra And Nagar Haveli': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Dadra And Nagar Haveli And Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu',
})

# ---- 5. PAIRED MELT: Total Schools + Schools With Facility (2 groups this time, 
#         percentage will be RECOMPUTED, not melted directly - see step 7) ----
total_cols = {
    'Total Government Schools (UOM:Number), Scaling Factor:1': 'Government',
    'Total Government-Aided Schools (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Total Private Unaided Schools (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Total Other Schools (UOM:Number), Scaling Factor:1': 'Other',
}
with_facility_cols = {
    'Government Schools With Computer Facility (UOM:Number), Scaling Factor:1': 'Government',
    'Government-Aided Schools With Computer Facility (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Private Unaided Schools With Computer Facility (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Other Schools With Computer Facility (UOM:Number), Scaling Factor:1': 'Other',
}

total_long = df.melt(id_vars=['state', 'year'], value_vars=list(total_cols.keys()),
                      var_name='management', value_name='total_schools')
total_long['management'] = total_long['management'].map(total_cols)

facility_long = df.melt(id_vars=['state', 'year'], value_vars=list(with_facility_cols.keys()),
                         var_name='management', value_name='schools_with_facility')
facility_long['management'] = facility_long['management'].map(with_facility_cols)

merged_counts = total_long.merge(facility_long, on=['state', 'year', 'management'])

# ---- 6. SUM the raw counts for any duplicate rows (this correctly handles 
#         the genuine 2018/2019 Dadra+Daman split, where both were real, 
#         separate, non-overlapping territories that DO need summing - 
#         different from File 9's stale-duplicate situation) ----
final_df = merged_counts.groupby(['state', 'year', 'management'], as_index=False)[
    ['total_schools', 'schools_with_facility']
].sum()

# ---- 7. RECOMPUTE percentage from the summed counts ----
# (Correct approach: NEVER sum or average pre-calculated percentages when 
# merging groups - always recalculate from the underlying raw counts)
final_df['pct_with_facility'] = (
    final_df['schools_with_facility'] / final_df['total_schools'] * 100
).round(2).fillna(0)

print("Total rows after melt + merge:", len(final_df))
print("Unique states:", final_df['state'].nunique())
print(sorted(final_df['state'].unique()))
print()
print(final_df.head(10))

# ---- 8. SAVE cleaned file ----
final_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\1-Unified District Information System For Education (UDISE) - Flash Statistics\Examination Results for Grade XII by Management.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_exam_results_grade12.csv"

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

# ---- 4. DROP "Additional Info" - not real data ----
df = df.drop(columns=['Additional Info'])

# ---- 5. FIX state issues ----
df = df[df['state'] != 'All India']
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 6. PAIRED MELT: this file has 2 metrics (appeared, pass_pct) per management type ----
# We melt each metric group SEPARATELY, then merge them back together on (state, year, management)

appeared_cols = {
    'Government Grade Xii Students Appeared (UOM:Number), Scaling Factor:1': 'Government',
    'Government-Aided Grade Xii Students Appeared (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Private Unaided Grade Xii Students Appeared (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Other Schools Grade Xii Students Appeared (UOM:Number), Scaling Factor:1': 'Other',
}
pass_cols = {
    'Government Grade Xii Pass Percentage (UOM:%(Percentage)), Scaling Factor:1': 'Government',
    'Government-Aided Grade Xii Pass Percentage (UOM:%(Percentage)), Scaling Factor:1': 'Government Aided',
    'Private Unaided Grade Xii Pass Percentage (UOM:%(Percentage)), Scaling Factor:1': 'Private Unaided',
    'Other Schools Grade Xii Pass Percentage (UOM:%(Percentage)), Scaling Factor:1': 'Other',
}
# "Total Grade Xii ..." columns are check-totals - excluded from melt entirely (not a real category)

appeared_long = df.melt(id_vars=['state', 'year'], value_vars=list(appeared_cols.keys()),
                          var_name='management', value_name='appeared')
appeared_long['management'] = appeared_long['management'].map(appeared_cols)

pass_long = df.melt(id_vars=['state', 'year'], value_vars=list(pass_cols.keys()),
                     var_name='management', value_name='pass_pct')
pass_long['management'] = pass_long['management'].map(pass_cols)

# Merge the two melted metric tables back together
merged = appeared_long.merge(pass_long, on=['state', 'year', 'management'])

# ---- 7. MERGE duplicate rows (from Dadra/Daman rename) ----
# "appeared" -> SUM (raw count)
# "pass_pct" -> WEIGHTED AVERAGE using "appeared" as weight
def weighted_avg(group):
    total_appeared = group['appeared'].sum()
    weighted_pass = (group['pass_pct'] * group['appeared']).sum() / total_appeared if total_appeared > 0 else 0
    return pd.Series({'appeared': total_appeared, 'pass_pct': round(weighted_pass, 2)})

final_df = merged.groupby(['state', 'year', 'management']).apply(weighted_avg, include_groups=False).reset_index()

# ---- 8. FLAG impossible pass_pct values ----
bad_pct = final_df[(final_df['pass_pct'] > 100) | (final_df['pass_pct'] < 0)]
if len(bad_pct) > 0:
    print(f"WARNING: {len(bad_pct)} rows have pass_pct outside 0-100 range:")
    print(bad_pct)
    print()

print("Total rows after paired melt + merge:", len(final_df))
print("Unique states:", final_df['state'].nunique())
print(sorted(final_df['state'].unique()))
print()
print(final_df.head(10))

# ---- 9. SAVE cleaned file ----
final_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
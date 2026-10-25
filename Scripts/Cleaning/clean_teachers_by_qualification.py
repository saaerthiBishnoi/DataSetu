import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\1-Unified District Information System For Education (UDISE) - Flash Statistics\Distribution of Teachers by Academic Qualification.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_teachers_by_qualification.csv"

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

# ---- 4. FIX state name issues ----
df = df[df['state'] != 'All India']
df['state'] = df['state'].str.replace(r'(?<=[a-z])And(?=s?$)', 'and', regex=True)

# Merge pre-2020 UT names into post-2020 combined name
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 5. DROP "Additional Info" ----
df = df.drop(columns=['Additional Info'])

# ---- 6. RENAME the 9 qualification percentage columns ----
qual_column_map = {
    'Below Secondary (UOM:%(Percentage)), Scaling Factor:1': 'Below Secondary',
    'Secondary (UOM:%(Percentage)), Scaling Factor:1': 'Secondary',
    'Higher Secondary School ( I-Xii ) (UOM:%(Percentage)), Scaling Factor:1': 'Higher Secondary (I-XII)',
    'Graduate (UOM:%(Percentage)), Scaling Factor:1': 'Graduate',
    'Post Graduate (UOM:%(Percentage)), Scaling Factor:1': 'Post Graduate',
    'Master Of Philosophy (UOM:%(Percentage)), Scaling Factor:1': 'M.Phil',
    'Ph.D/Post Doctoral (UOM:%(Percentage)), Scaling Factor:1': 'PhD/Post Doctoral',
    'State Defined Qualification (UOM:%(Percentage)), Scaling Factor:1': 'State Defined',
    'No Response (UOM:%(Percentage)), Scaling Factor:1': 'No Response',
}
df = df.rename(columns=qual_column_map)
df = df.rename(columns={'Total (UOM:%(Percentage)), Scaling Factor:1': 'total_pct_reported'})

qual_cols = list(qual_column_map.values())

# ---- 7. MERGE duplicate rows created by the Dadra/Daman rename ----
value_cols = qual_cols + ['total_pct_reported']
df = df.groupby(['state', 'year'], as_index=False)[value_cols].sum()

# ---- 8. MELT: wide -> long ----
long_df = df.melt(
    id_vars=['state', 'year'],
    value_vars=qual_cols,
    var_name='qualification',
    value_name='teacher_pct'
)

# ---- 9. SANITY CHECK ----
check = long_df.groupby(['state', 'year'], as_index=False)['teacher_pct'].sum()
check = check.rename(columns={'teacher_pct': 'recomputed_total_pct'})
verify = df[['state', 'year', 'total_pct_reported']].merge(check, on=['state', 'year'])
verify['match'] = (verify['recomputed_total_pct'] - verify['total_pct_reported']).abs() <= 2

print("Total rows after melt:", len(long_df))
print("Unique states:", long_df['state'].nunique())
print(sorted(long_df['state'].unique()))
print()
print("Sanity check results:")
print(verify['match'].value_counts())
mismatches = verify[~verify['match']]
if len(mismatches) > 0:
    print(f"\n{len(mismatches)} rows outside tolerance:")
    print(mismatches)

# ---- 10. SAVE ----
long_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
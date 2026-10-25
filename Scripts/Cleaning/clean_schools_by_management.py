import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\1-Unified District Information System For Education (UDISE) - Flash Statistics\Number of Schools by School Management.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_schools_total.csv"

# ---- 2. LOAD ----
df = pd.read_csv(input_path)

print("Columns found in file:")
print(df.columns.tolist())
print()

# ---- 3. RENAME core columns to clean, consistent names ----
df = df.rename(columns={
    'State/Ut Name': 'state',
    'Year': 'year_raw',
})

# Clean Year: "Financial Year (Apr - Mar), 2017" -> 2017
df['year'] = df['year_raw'].astype(str).str.extract(r'(\d{4})').astype(int)

# ---- 4. RENAME the 11 management columns to short, clean codes ----
mgmt_column_map = {
    'NOSB Department Of Education (Doe) (UOM:Number), Scaling Factor:1': 'DoE',
    'NOSB Tribal Social Welfare Department (Tswd) (UOM:Number), Scaling Factor:1': 'TSWD',
    'NOSB Local Body (Lb) (UOM:Number), Scaling Factor:1': 'LB',
    'NOSB Government Aided (Ga) (UOM:Number), Scaling Factor:1': 'GA',
    'NOSB Private Unaided (Pvtu) (UOM:Number), Scaling Factor:1': 'PVTU',
    'NOSB Other Government Managements (Ogm) (UOM:Number), Scaling Factor:1': 'OGM',
    'NOSB Central Government (Cg) (UOM:Number), Scaling Factor:1': 'CG',
    'NOSB Other Unrecognised Institutions (Ouri) (UOM:Number), Scaling Factor:1': 'OURI',
    'NOSB No Response (Nr) (UOM:Number), Scaling Factor:1': 'NR',
    'NOSB Recognised Madarsa (Rmd) (UOM:Number), Scaling Factor:1': 'RMD',
    'NOSB Unrecognised Madarsa (Urmd) (UOM:Number), Scaling Factor:1': 'URMD',
}
df = df.rename(columns=mgmt_column_map)
df = df.rename(columns={'Total Number Of Schools (UOM:Number), Scaling Factor:1': 'total_schools_reported'})

mgmt_cols = list(mgmt_column_map.values())

# ---- 5. MELT: wide -> long ----
long_df = df.melt(
    id_vars=['state', 'year'],
    value_vars=mgmt_cols,
    var_name='management_detailed',
    value_name='school_count'
)

# ---- 6. RELABEL: 11 detailed categories -> 4 standard categories ----
mapping_11_to_4 = {
    'DoE': 'Government',
    'TSWD': 'Government',
    'LB': 'Government',
    'CG': 'Government',
    'OGM': 'Government',
    'GA': 'Government Aided',
    'PVTU': 'Private Unaided',
    'OURI': 'Other',
    'NR': 'Other',
    'RMD': 'Other',
    'URMD': 'Other',
}
long_df['management'] = long_df['management_detailed'].map(mapping_11_to_4)

# ---- 7. SUM: aggregate rows that now share the same management label ----
final_df = (
    long_df.groupby(['state', 'year', 'management'], as_index=False)['school_count']
    .sum()
)

# ---- 8. SANITY CHECK: recomputed total vs original Total column ----
check = final_df.groupby(['state', 'year'], as_index=False)['school_count'].sum()
check = check.rename(columns={'school_count': 'recomputed_total'})
verify = df[['state', 'year', 'total_schools_reported']].merge(check, on=['state', 'year'])
verify['match'] = verify['recomputed_total'] == verify['total_schools_reported']

print("Total rows after melt + relabel + sum:", len(final_df))
print(final_df.head(8))
print()
print("Sanity check results:")
print(verify['match'].value_counts())
mismatches = verify[~verify['match']]
if len(mismatches) > 0:
    print("\nRows that didn't match exactly (small discrepancies expected):")
    print(mismatches)

# ---- 9. SAVE cleaned file ----
final_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
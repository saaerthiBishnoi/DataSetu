import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\1-Unified District Information System For Education (UDISE) - Flash Statistics\Number of Schools by Management and School Category.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_schools_by_category.csv"

# ---- 2. LOAD ----
df = pd.read_csv(input_path)

print("Columns found in file:")
print(df.columns.tolist())
print()

# ---- 3. RENAME core columns to clean, consistent names ----
df = df.rename(columns={
    'State/Ut Name': 'state',
    'Year': 'year_raw',
    'Type Of Management': 'management',
})

# Clean Year: "Financial Year (Apr - Mar), 2017" -> 2017
df['year'] = df['year_raw'].astype(str).str.extract(r'(\d{4})').astype(int)

# ---- 4. RENAME the 10 school-category columns to short, clean names ----
category_column_map = {
    'Primary School (I -V) (UOM:Number), Scaling Factor:1': 'Primary (I-V)',
    'Upper Primary School (I - Viii) (UOM:Number), Scaling Factor:1': 'Upper Primary (I-VIII)',
    'Higher Secondary School (I - Xii) (UOM:Number), Scaling Factor:1': 'Higher Secondary (I-XII)',
    'Upper Primary School (Vi - Viii) (UOM:Number), Scaling Factor:1': 'Upper Primary (VI-VIII)',
    'Higher Secondary School (Vi - Xiii) (UOM:Number), Scaling Factor:1': 'Higher Secondary (VI-XIII)',
    'Secondary School (I - X) (UOM:Number), Scaling Factor:1': 'Secondary (I-X)',
    'Secondary School (Vi - X) (UOM:Number), Scaling Factor:1': 'Secondary (VI-X)',
    'Secondary School (Ix - X) (UOM:Number), Scaling Factor:1': 'Secondary (IX-X)',
    'Higher Secondary School (Ix - Xii) (UOM:Number), Scaling Factor:1': 'Higher Secondary (IX-XII)',
    'Higher Secondary School (Xi - Xii) (UOM:Number), Scaling Factor:1': 'Higher Secondary (XI-XII)',
}
df = df.rename(columns=category_column_map)
df = df.rename(columns={
    'Total Number Of Schools By Management (UOM:Number), Scaling Factor:1': 'total_schools_reported'
})

category_cols = list(category_column_map.values())

# ---- 5. MELT: wide category columns -> long (one row per state, year, management, category) ----
long_df = df.melt(
    id_vars=['state', 'year', 'management'],
    value_vars=category_cols,
    var_name='school_category',
    value_name='school_count'
)

# ---- 6. FIX: standardize management category spelling to match all other files ----
# (this file had "Others" instead of "Other", and "Private unaided" instead 
# of "Private Unaided" - caught during Dim_Management master list review)
long_df['management'] = long_df['management'].replace({
    'Others': 'Other',
    'Private unaided': 'Private Unaided'
})

# ---- 7. SANITY CHECK: sum of all categories per state+year+management vs reported total ----
check = long_df.groupby(['state', 'year', 'management'], as_index=False)['school_count'].sum()
check = check.rename(columns={'school_count': 'recomputed_total'})

# Also fix the management column in df (original) so the merge for verification works
df['management'] = df['management'].replace({
    'Others': 'Other',
    'Private unaided': 'Private Unaided'
})

verify = df[['state', 'year', 'management', 'total_schools_reported']].merge(
    check, on=['state', 'year', 'management']
)
verify['match'] = verify['recomputed_total'] == verify['total_schools_reported']

print("Total rows after melt:", len(long_df))
print("Unique management values (verify only 4 remain):")
print(sorted(long_df['management'].unique()))
print()
print(long_df.head(10))
print()
print("Sanity check results:")
print(verify['match'].value_counts())
mismatches = verify[~verify['match']]
if len(mismatches) > 0:
    print(f"\n{len(mismatches)} rows didn't match exactly:")
    print(mismatches.head(15))
else:
    print("All totals match exactly.")

# ---- 8. SAVE cleaned file ----
long_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
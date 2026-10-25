import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\2-Unified District Information System for Education Plus (UDISE+)\Schools by Management and Availability of Boys Toilet and Functional Boys Toile.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_boys_toilet.csv"

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
# Dadra/Daman already merged, no duplicates, no "India" row, 
# full 7-year coverage (unlike Girls Toilet file, which had a 2020 gap)
df['state'] = df['state'].str.replace(r'(?<=[a-z])And(?=s?$)', 'and', regex=True)
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli And Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 5. TRIPLE MELT: Total (Boys+CoEd) Schools, With Toilet, With Functional Toilet ----
total_cols = {
    'Government Boys And Co-Educational Schools (UOM:Number), Scaling Factor:1': 'Government',
    'Government-Aided Boys And Co-Educational Schools (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Private Unaided Boys And Co-Educational Schools (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Other Boys And Co-Educational Schools (UOM:Number), Scaling Factor:1': 'Other',
}
toilet_cols = {
    'Government Schools With Boys Toilet Facility (UOM:Number), Scaling Factor:1': 'Government',
    'Government-Aided Schools With Boys Toilet Facility (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Private Unaided Schools With Boys Toilet Facility (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Other Schools With Boys Toilet Facility (UOM:Number), Scaling Factor:1': 'Other',
}
functional_cols = {
    'Government Schools With Functional Boys Toilet Facility (UOM:Number), Scaling Factor:1': 'Government',
    'Government-Aided Schools With Functional Boys Toilet Facility (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Private Unaided Schools With Functional Boys Toilet Facility (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Other Schools With Functional Boys Toilet Facility (UOM:Number), Scaling Factor:1': 'Other',
}

total_long = df.melt(id_vars=['state', 'year'], value_vars=list(total_cols.keys()),
                      var_name='management', value_name='total_schools')
total_long['management'] = total_long['management'].map(total_cols)

toilet_long = df.melt(id_vars=['state', 'year'], value_vars=list(toilet_cols.keys()),
                       var_name='management', value_name='schools_with_toilet')
toilet_long['management'] = toilet_long['management'].map(toilet_cols)

functional_long = df.melt(id_vars=['state', 'year'], value_vars=list(functional_cols.keys()),
                           var_name='management', value_name='schools_with_functional_toilet')
functional_long['management'] = functional_long['management'].map(functional_cols)

final_df = total_long.merge(toilet_long, on=['state', 'year', 'management']) \
                      .merge(functional_long, on=['state', 'year', 'management'])

# ---- 6. Derive percentage columns ----
final_df['pct_with_toilet'] = (final_df['schools_with_toilet'] / final_df['total_schools'] * 100).round(2).fillna(0)
final_df['pct_with_functional_toilet'] = (final_df['schools_with_functional_toilet'] / final_df['total_schools'] * 100).round(2).fillna(0)

print("Total rows after triple melt + merge:", len(final_df))
print("Unique states:", final_df['state'].nunique())
print(sorted(final_df['state'].unique()))
print()
print(final_df.head(10))

# ---- 7. SAVE cleaned file ----
final_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
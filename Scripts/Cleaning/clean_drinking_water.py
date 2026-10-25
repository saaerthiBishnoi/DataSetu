import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\2-Unified District Information System for Education Plus (UDISE+)\Schools by Management and Availability of Drinking Water and Functional Drinking Water.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_drinking_water.csv"

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
# This file's Dadra/Daman data is ALREADY fully merged, no duplicates, 
# no "India" row - simplest state cleanup so far
df['state'] = df['state'].str.replace(r'(?<=[a-z])And(?=s?$)', 'and', regex=True)
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli And Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 5. TRIPLE MELT: Total Schools, With Drinking Water, With Functional Drinking Water ----
# Note: this file has NO percentage column at all - only raw counts

total_cols = {
    'Government Schools (UOM:Number), Scaling Factor:1': 'Government',
    'Govt Aided Schools (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Private Unaided Schools (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Other Schools (UOM:Number), Scaling Factor:1': 'Other',
}
water_cols = {
    'Government Schools With Drinking Water (UOM:Number), Scaling Factor:1': 'Government',
    'Govt Aided Schools With Drinking Water (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Private Unaided Schools With Drinking Water (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Other Schools With Drinking Water (UOM:Number), Scaling Factor:1': 'Other',
}
functional_cols = {
    'Government Schools With Functional Drinking Water (UOM:Number), Scaling Factor:1': 'Government',
    'Govt Aided Schools With Functional Drinking Water (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Private Unaided Schools With Functional Drinking Water (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Other Schools With Functional Drinking Water (UOM:Number), Scaling Factor:1': 'Other',
}

total_long = df.melt(id_vars=['state', 'year'], value_vars=list(total_cols.keys()),
                      var_name='management', value_name='total_schools')
total_long['management'] = total_long['management'].map(total_cols)

water_long = df.melt(id_vars=['state', 'year'], value_vars=list(water_cols.keys()),
                      var_name='management', value_name='schools_with_water')
water_long['management'] = water_long['management'].map(water_cols)

functional_long = df.melt(id_vars=['state', 'year'], value_vars=list(functional_cols.keys()),
                           var_name='management', value_name='schools_with_functional_water')
functional_long['management'] = functional_long['management'].map(functional_cols)

# Merge all 3 melted metric tables together
final_df = total_long.merge(water_long, on=['state', 'year', 'management']) \
                      .merge(functional_long, on=['state', 'year', 'management'])

# ---- 6. Derive percentage columns ourselves (not provided in source) ----
final_df['pct_with_water'] = (final_df['schools_with_water'] / final_df['total_schools'] * 100).round(2).fillna(0)
final_df['pct_with_functional_water'] = (final_df['schools_with_functional_water'] / final_df['total_schools'] * 100).round(2).fillna(0)

print("Total rows after triple melt + merge:", len(final_df))
print("Unique states:", final_df['state'].nunique())
print(sorted(final_df['state'].unique()))
print()
print(final_df.head(10))

# ---- 7. SAVE cleaned file ----
final_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
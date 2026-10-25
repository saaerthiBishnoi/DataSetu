import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\2-Unified District Information System for Education Plus (UDISE+)\Schools by Management and Availability of Internet Facility.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_internet_facility.csv"

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
# Drop "India" - national aggregate
df = df[df['state'] != 'India']

# Drop standalone "Daman And Diu" rows - this file ALREADY has a merged
# "Dadra And Nagar Haveli And Daman And Diu" entry for the same years (2018-2019),
# so the standalone rows are stale/duplicate leftovers, NOT additional data to sum.
# (Verified: years 2020-2024 only have the merged entry, confirming this pattern.)
df = df[df['state'] != 'Daman And Diu']

# Fix "And" typo (JharkhAnd -> Jharkhand, etc.)
df['state'] = df['state'].str.replace(r'(?<=[a-z])And(?=s?$)', 'and', regex=True)

# Add missing "The" prefix to match naming in Files 1-8
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli And Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 5. PAIRED MELT (3 metric groups): Total Schools, Schools With Facility, % With Facility ----
# "All Management" columns are check-totals - excluded from melt (like "Total" in other files)

total_cols = {
    'Total Government Schools (UOM:Number), Scaling Factor:1': 'Government',
    'Total Government-Aided Schools (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Total Private Unaided Schools (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Total Other Schools (UOM:Number), Scaling Factor:1': 'Other',
}
with_facility_cols = {
    'Number Of Government Schools With Internet Facility Available (UOM:Number), Scaling Factor:1': 'Government',
    'Number Of Government Aided Schools With Internet Facility Available (UOM:Number), Scaling Factor:1': 'Government Aided',
    'Number Of Private Unaided Schools With Internet Facility Available (UOM:Number), Scaling Factor:1': 'Private Unaided',
    'Number Of Other Schools With Internet Facility Available (UOM:Number), Scaling Factor:1': 'Other',
}
pct_cols = {
    'Percentage Of Government Schools (UOM:%(Percentage)), Scaling Factor:1': 'Government',
    'Percentage Of Government Aided Schools  (UOM:%(Percentage)), Scaling Factor:1': 'Government Aided',
    'Percentage Of Private Unaided Schools  (UOM:%(Percentage)), Scaling Factor:1': 'Private Unaided',
    'Percentage Of Other Schools (UOM:%(Percentage)), Scaling Factor:1': 'Other',
}

total_long = df.melt(id_vars=['state', 'year'], value_vars=list(total_cols.keys()),
                      var_name='management', value_name='total_schools')
total_long['management'] = total_long['management'].map(total_cols)

facility_long = df.melt(id_vars=['state', 'year'], value_vars=list(with_facility_cols.keys()),
                         var_name='management', value_name='schools_with_facility')
facility_long['management'] = facility_long['management'].map(with_facility_cols)

pct_long = df.melt(id_vars=['state', 'year'], value_vars=list(pct_cols.keys()),
                    var_name='management', value_name='pct_with_facility')
pct_long['management'] = pct_long['management'].map(pct_cols)

# Merge all 3 melted metric tables back together
final_df = total_long.merge(facility_long, on=['state', 'year', 'management']) \
                      .merge(pct_long, on=['state', 'year', 'management'])

print("Total rows after 3-way melt + merge:", len(final_df))
print("Unique states:", final_df['state'].nunique())
print(sorted(final_df['state'].unique()))
print()
print(final_df.head(10))

# ---- 6. SAVE cleaned file ----
final_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
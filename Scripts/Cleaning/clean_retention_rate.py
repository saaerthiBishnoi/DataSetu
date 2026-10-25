import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\1-Unified District Information System For Education (UDISE) - Flash Statistics\Retention Rate by Educational Stage.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_retention_rate.csv"

# ---- 2. LOAD ----
df = pd.read_csv(input_path)

print("Columns found in file:")
print(df.columns.tolist())
print()

# ---- 3. RENAME core columns ----
df = df.rename(columns={
    'State/Ut Name': 'state',
    'Year': 'year_raw',
    'Gender': 'gender',
})
df['year'] = df['year_raw'].astype(str).str.extract(r'(\d{4})').astype(int)

# ---- 4. FIX state issues ----
# Drop "All India" - national aggregate
df = df[df['state'] != 'All India']

# Fix "And" typo (JharkhAnd -> Jharkhand, NagalAnd -> Nagaland, etc.)
df['state'] = df['state'].str.replace(r'(?<=[a-z])And(?=s?$)', 'and', regex=True)

# Fix missing "The" prefix to match naming used in Files 1-6
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli And Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 5. FIX gender trailing space issue ("Girls " -> "Girls") ----
df['gender'] = df['gender'].str.strip()

# ---- 6. RENAME the 3 stage columns ----
stage_column_map = {
    'Primary (I-V) (UOM:Ratio), Scaling Factor:1': 'Primary (I-V)',
    'Elementary (I-Viii) (UOM:Ratio), Scaling Factor:1': 'Elementary (I-VIII)',
    'Secondary (I-X) (UOM:Ratio), Scaling Factor:1': 'Secondary (I-X)',
}
df = df.rename(columns=stage_column_map)
stage_cols = list(stage_column_map.values())

# ---- 7. MELT: wide stage columns -> long (stage becomes a row value) ----
long_df = df.melt(
    id_vars=['state', 'year', 'gender'],
    value_vars=stage_cols,
    var_name='stage',
    value_name='retention_rate'
)

print("Total rows after melt:", len(long_df))
print("Unique states:", long_df['state'].nunique())
print(sorted(long_df['state'].unique()))
print()
print("Unique gender values:", long_df['gender'].unique())
print()
print(long_df.head(9))

# ---- 8. SAVE cleaned file ----
long_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
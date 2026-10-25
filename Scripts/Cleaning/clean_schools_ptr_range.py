import pandas as pd

# ---- 1. FILE PATHS ----
input_path = r"D:\Downloads\DataSetu\DataSet\1-Unified District Information System For Education (UDISE) - Flash Statistics\Distribution of Schools by School Category and Range of Pupil Teacher Ratio.csv"
output_path = r"D:\Downloads\DataSetu\Cleaned\fact_schools_ptr_range.csv"

# ---- 2. LOAD ----
df = pd.read_csv(input_path)

print("Original columns found in file (note: some names repeat - see notes below):")
print(df.columns.tolist())
print()

# ---- 3. RENAME columns BY POSITION (not by name, since NDAP's export has 
#         genuinely duplicate column names that pandas auto-suffixes with .1) ----
# ASSUMPTION (documented, not verified against NDAP source - site was down 
# during this cleaning): for each duplicate pair, the FIRST occurrence = 
# All Management, the SECOND occurrence = Government only. This matches 
# the one unambiguous pair in the file ("Primary Schools" vs "Government 
# Primary Schools").
df.columns = [
    'country', 'year_raw', 'state', 'ptr_range',
    'all_Primary(I-V)', 'govt_Primary(I-V)',
    'all_UpperPrimary(I-VIII)', 'govt_UpperPrimary(I-VIII)',
    'all_HigherSecondary(I-XII)', 'govt_HigherSecondary(I-XII)',
    'all_UpperPrimary(VI-VIII)', 'govt_UpperPrimary(VI-VIII)',
    'all_HigherSecondary(VI-XII)', 'govt_HigherSecondary(VI-XII)',
    'all_Secondary(I-X)', 'govt_Secondary(I-X)',
    'all_Secondary(VI-X)', 'govt_Secondary(VI-X)',
    'total_all_categories', 'total_govt_categories'
]

df['year'] = df['year_raw'].astype(str).str.extract(r'(\d{4})').astype(int)

# ---- 4. FIX state issues ----
df = df[df['state'] != 'All India']
df['state'] = df['state'].str.replace(r'(?<=[a-z])And(?=s?$)', 'and', regex=True)
df['state'] = df['state'].replace({
    'Dadra And Nagar Haveli': 'The Dadra And Nagar Haveli And Daman And Diu',
    'Daman And Diu': 'The Dadra And Nagar Haveli And Daman And Diu'
})

# ---- 5. SPLIT into TWO separate long tables: "All Management" and "Government only" ----
# (kept separate rather than melted into one "management" column, since only 
# 2 management scopes exist here - not the standard 4-category Dim_Management)

all_mgmt_cols = {
    'all_Primary(I-V)': 'Primary (I-V)',
    'all_UpperPrimary(I-VIII)': 'Upper Primary (I-VIII)',
    'all_HigherSecondary(I-XII)': 'Higher Secondary (I-XII)',
    'all_UpperPrimary(VI-VIII)': 'Upper Primary (VI-VIII)',
    'all_HigherSecondary(VI-XII)': 'Higher Secondary (VI-XII)',
    'all_Secondary(I-X)': 'Secondary (I-X)',
    'all_Secondary(VI-X)': 'Secondary (VI-X)',
}
govt_mgmt_cols = {
    'govt_Primary(I-V)': 'Primary (I-V)',
    'govt_UpperPrimary(I-VIII)': 'Upper Primary (I-VIII)',
    'govt_HigherSecondary(I-XII)': 'Higher Secondary (I-XII)',
    'govt_UpperPrimary(VI-VIII)': 'Upper Primary (VI-VIII)',
    'govt_HigherSecondary(VI-XII)': 'Higher Secondary (VI-XII)',
    'govt_Secondary(I-X)': 'Secondary (I-X)',
    'govt_Secondary(VI-X)': 'Secondary (VI-X)',
}

all_long = df.melt(id_vars=['state', 'year', 'ptr_range'], value_vars=list(all_mgmt_cols.keys()),
                    var_name='school_category', value_name='pct_schools')
all_long['school_category'] = all_long['school_category'].map(all_mgmt_cols)
all_long['management_scope'] = 'All Management'

govt_long = df.melt(id_vars=['state', 'year', 'ptr_range'], value_vars=list(govt_mgmt_cols.keys()),
                     var_name='school_category', value_name='pct_schools')
govt_long['school_category'] = govt_long['school_category'].map(govt_mgmt_cols)
govt_long['management_scope'] = 'Government'

long_df = pd.concat([all_long, govt_long], ignore_index=True)

# ---- 6. MERGE duplicate rows (from Dadra/Daman rename) - simple average is 
#         acceptable here since these are already percentage-of-schools values ----
long_df = long_df.groupby(
    ['state', 'year', 'ptr_range', 'school_category', 'management_scope'],
    as_index=False
)['pct_schools'].mean().round(2)

print("Total rows after melt:", len(long_df))
print("Unique states:", long_df['state'].nunique())
print(sorted(long_df['state'].unique()))
print()
print(long_df.head(10))

# ---- 7. SAVE cleaned file ----
long_df.to_csv(output_path, index=False)
print(f"\nSaved cleaned file to: {output_path}")
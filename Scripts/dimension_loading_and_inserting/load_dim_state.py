import pandas as pd
import glob

# ---- 1. Find all cleaned CSV files ----
cleaned_folder = r"D:\Downloads\DataSetu\Cleaned"
all_files = glob.glob(f"{cleaned_folder}\\*.csv")

print(f"Found {len(all_files)} cleaned files:")
for f in all_files:
    print(" -", f)
print()

# ---- 2. Collect all unique state names across every file ----
all_states = set()

for file in all_files:
    df = pd.read_csv(file)
    if 'state' in df.columns:
        all_states.update(df['state'].unique())
    else:
        print(f"NOTE: no 'state' column in {file} (this is expected for some files)")

all_states = sorted(all_states)

print(f"\nTotal unique states found across all files: {len(all_states)}")
for s in all_states:
    print(" -", s)

# ---- 3. Save this master list to a CSV for review before inserting into Postgres ----
state_df = pd.DataFrame({'state_name': all_states})
state_df.to_csv(r"D:\Downloads\DataSetu\Cleaned\dim_state_master_list.csv", index=False)
print("\nSaved master state list to: dim_state_master_list.csv")
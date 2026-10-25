import pandas as pd
import glob

cleaned_folder = r"D:\Downloads\DataSetu\Cleaned"
all_files = glob.glob(f"{cleaned_folder}\\*.csv")

all_qualifications = set()

for file in all_files:
    df = pd.read_csv(file)
    if 'qualification' in df.columns:
        all_qualifications.update(df['qualification'].unique())

all_qualifications = sorted(all_qualifications)

print(f"Total unique qualification values found: {len(all_qualifications)}")
print(all_qualifications)

qual_df = pd.DataFrame({'qualification_name': all_qualifications})
qual_df.to_csv(r"D:\Downloads\DataSetu\Cleaned\dim_qualification_master_list.csv", index=False)
print("\nSaved master qualification list to: dim_qualification_master_list.csv")
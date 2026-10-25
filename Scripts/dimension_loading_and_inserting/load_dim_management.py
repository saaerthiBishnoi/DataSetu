import pandas as pd
import glob

cleaned_folder = r"D:\Downloads\DataSetu\Cleaned"
all_files = glob.glob(f"{cleaned_folder}\\*.csv")

all_management = set()

for file in all_files:
    df = pd.read_csv(file)
    if 'management' in df.columns:
        all_management.update(df['management'].unique())

all_management = sorted(all_management)

print(f"Total unique management values found: {len(all_management)}")
print(all_management)

management_df = pd.DataFrame({'management_name': all_management})
management_df.to_csv(r"D:\Downloads\DataSetu\Cleaned\dim_management_master_list.csv", index=False)
print("\nSaved master management list to: dim_management_master_list.csv")
import pandas as pd
import glob

cleaned_folder = r"D:\Downloads\DataSetu\Cleaned"
all_files = glob.glob(f"{cleaned_folder}\\*.csv")

all_genders = set()

for file in all_files:
    df = pd.read_csv(file)
    if 'gender' in df.columns:
        all_genders.update(df['gender'].unique())

all_genders = sorted(all_genders)

print(f"Total unique gender values found: {len(all_genders)}")
print(all_genders)

gender_df = pd.DataFrame({'gender_name': all_genders})
gender_df.to_csv(r"D:\Downloads\DataSetu\Cleaned\dim_gender_master_list.csv", index=False)
print("\nSaved master gender list to: dim_gender_master_list.csv")
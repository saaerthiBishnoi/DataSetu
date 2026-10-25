import pandas as pd
import glob

cleaned_folder = r"D:\Downloads\DataSetu\Cleaned"
all_files = glob.glob(f"{cleaned_folder}\\*.csv")

all_years = set()

for file in all_files:
    df = pd.read_csv(file)
    if 'year' in df.columns:
        all_years.update(df['year'].unique())

all_years = sorted(all_years)

print(f"Total unique years found: {len(all_years)}")
print(all_years)

year_df = pd.DataFrame({'year_value': all_years})
year_df.to_csv(r"D:\Downloads\DataSetu\Cleaned\dim_year_master_list.csv", index=False)
print("\nSaved master year list to: dim_year_master_list.csv")
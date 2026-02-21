from datasets import load_dataset
import pandas as pd

dataset_name = "gouthxm07/kerala-crop-fertilizer-disease-qa"
print(f"Loading dataset: {dataset_name}")
try:
    ds = load_dataset(dataset_name)
    split_name = list(ds.keys())[0]
    df = ds[split_name].to_pandas()
    print("\nColumns found:", df.columns.tolist())
    print("\nFirst 2 rows:")
    print(df.head(2).to_string())
except Exception as e:
    print(f"Error: {e}")

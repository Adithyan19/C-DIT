from datasets import load_dataset
dataset_name = "gouthxm07/kerala-crop-fertilizer-disease-qa"
try:
    ds = load_dataset(dataset_name)
    print("Keys in dataset:", ds.keys())
    for split in ds.keys():
        print(f"Split {split} columns:", ds[split].column_names)
except Exception as e:
    print(f"Error: {e}")

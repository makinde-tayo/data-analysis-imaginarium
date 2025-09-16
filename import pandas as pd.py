import pandas as pd
from pathlib import Path

# Define your folder path
root_folder = Path("/Users/tayosmacbook/Desktop/Imaginarium Data Analysis/L_E Dataset")

# Participants to include
filenames = ['1', '2', '3', '4']

# Dictionary to store top 5 viewed objects per participant
top_5_viewed_dict = {}

for name in filenames:
    participant_file = root_folder / f"P{name}_L_E.csv"  # Adjust filename pattern as needed
    try:
        df = pd.read_csv(participant_file)
        if "ObjectName" in df.columns:
            top_5 = df["ObjectName"].value_counts().head(5)
            top_5_viewed_dict[f"P{name}"] = top_5
        else:
            print(f"Column 'ObjectName' not found in {participant_file}")
    except FileNotFoundError:
        print(f"File {participant_file} not found.")
    except pd.errors.EmptyDataError:
        print(f"File {participant_file} is empty.")

# Print results
for participant, top_objects in top_5_viewed_dict.items():
    print(f"\n{participant} - Top 5 Most Viewed Objects:")
    print(top_objects.to_string())

import pandas as pd
from pathlib import Path
from collections import Counter

# Define the root folder path
root_folder = Path("/Users/tayosmacbook/Desktop/Imaginarium Data Analysis /L_E Dataset")

# Participants 1–4
filenames = ['1', '2', '3', '4']

# Group into odd and even
odd_files = ['1', '3']
even_files = ['2', '4']

# Store per-participant top 5 results
top_5_per_participant = {}

# Store all object names for group-level counting
odd_objects = []
even_objects = []

for name in filenames:
    participant_file = root_folder / f"P{name}_DY_LE.csv"
    try:
        df = pd.read_csv(participant_file)
        if "ObjectName" in df.columns:
            object_series = df["ObjectName"].dropna()
            # Get top 5 for individual
            top_5 = object_series.value_counts().head(5)
            top_5_per_participant[f"P{name}"] = top_5
            # Add to group list
            if int(name) % 2 == 0:
                even_objects.extend(object_series.tolist())
            else:
                odd_objects.extend(object_series.tolist())
        else:
            print(f"Column 'ObjectName' not found in {participant_file}")
    except FileNotFoundError:
        print(f"File {participant_file} not found.")
    except pd.errors.EmptyDataError:
        print(f"File {participant_file} is empty.")

# Print top 5 per participant
for participant, top_items in top_5_per_participant.items():
    print(f"\n{participant} - Top 5 Most Viewed Objects:")
    print(top_items.to_string())

# Top 1 overall for odd and even groups
odd_counter = Counter(odd_objects)
even_counter = Counter(even_objects)

print("\nTop Viewed Object Among Odd-Numbered Participants:")
if odd_counter:
    item, count = odd_counter.most_common(1)[0]
    print(f"{item} (Viewed {count} times)")
else:
    print("No data found for odd-numbered participants.")

print("\nTop Viewed Object Among Even-Numbered Participants:")
if even_counter:
    item, count = even_counter.most_common(1)[0]
    print(f"{item} (Viewed {count} times)")
else:
    print("No data found for even-numbered participants.")

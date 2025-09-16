import pandas as pd
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
import numpy as np
import seaborn as sns
# KEY ISSUES( NEED TO FIGURE OUT HOW TO RESOLVE)
# #1: MEN AND WOMEN ARE DIFFERENT WITH PALM DATA: palms are for women, hands are for men 


# Define paths
root_folder = Path("/Users/tayosmacbook/Desktop/Imaginarium Data Analysis /L_E Dataset")
gender_file = Path("/Users/tayosmacbook/Desktop/Imaginarium Data Analysis /RawData.csv")

# Define participant IDs to process
participant_ids = [f"P{i}" for i in list(range(0, 7)) + [8, 11, 12, 13, 14, 17, 18, 19, 20, 21, 22, 23, 24, 27, 28, 29] + list(range(30, 44))]

# Load the raw gender data
raw_df = pd.read_csv(gender_file)

# Filter the DataFrame to include only the rows for the specified participants
filtered_df = raw_df[raw_df['Participant ID'].isin(participant_ids)]

# Create a gender map for only the filtered participants
gender_map = dict(zip(filtered_df['Participant ID'], filtered_df['Post_Dem_Gender']))

# Store object names by gender
male_objects = []
female_objects = []

# Optional: top 5 per participant
top_5_per_participant = {}

# List of substrings to exclude 
exclude_keywords = ["wall", "floor", "ceiling", "mat", "instructor", "hand", "palm"]

for pid in participant_ids:
    participant_file = root_folder / f"{pid}_DY_LE.csv"
    try:
        df = pd.read_csv(participant_file)
        if "ObjectName" in df.columns:
            # Filter out excluded objects
            object_series = df["ObjectName"].dropna()
            object_series_filtered = object_series[~object_series.str.contains('|'.join(exclude_keywords), case=False)]

            # Get the top 5 objects (filtered)
            top_5 = object_series_filtered.value_counts().head(5)
            top_5_per_participant[pid] = top_5

            # Get gender from the gender_map
            gender = gender_map.get(pid)
            if gender == "1":
                male_objects.extend(object_series_filtered.tolist())
            elif gender == "2":
                female_objects.extend(object_series_filtered.tolist())
            else:
                print(f"Unknown or missing gender for {pid}")
        else:
            print(f"Column 'ObjectName' not found in {participant_file}")
    except FileNotFoundError:
        print(f"File {participant_file} not found.")
    except pd.errors.EmptyDataError:
        print(f"File {participant_file} is empty.")

# Compute top 5 for each gender
male_counter = Counter(male_objects)
female_counter = Counter(female_objects)

print("\nTop 5 Most Viewed Objects by Male Participants:")
for item, count in male_counter.most_common(5):
    print(f"{item}: {count} views")

print("\nTop 5 Most Viewed Objects by Female Participants:")
for item, count in female_counter.most_common(5):
    print(f"{item}: {count} views")

# --------- GRAPHING TOP 20 OBJECTS ---------
total_counter = male_counter + female_counter
top_20_objects = [item for item, _ in total_counter.most_common(20)]
male_counts = [male_counter.get(k, 0) for k in top_20_objects]
female_counts = [female_counter.get(k, 0) for k in top_20_objects]

df_plot = pd.DataFrame({
    'ObjectName': top_20_objects,
    'Male': male_counts,
    'Female': female_counts
})

plt.figure(figsize=(12, 6))
x = range(len(df_plot))
bar_width = 0.4

plt.bar([i - bar_width/2 for i in x], df_plot['Male'], width=bar_width, label='Male')
plt.bar([i + bar_width/2 for i in x], df_plot['Female'], width=bar_width, label='Female')

plt.xticks(ticks=x, labels=df_plot['ObjectName'], rotation=45, ha='right')
plt.xlabel("Object Name")
plt.ylabel("View Count")
plt.title("Top 20 Object View Counts: Male vs Female Participants")
plt.legend()
plt.tight_layout()
plt.show()

# --------- T-TEST ANALYSIS AND VISUALIZATION ---------

# Group object counts by participant and gender
participant_objects = {pid: Counter() for pid in participant_ids}

for pid in participant_ids:
    participant_file = root_folder / f"{pid}_DY_LE.csv"
    try:
        df = pd.read_csv(participant_file)
        if "ObjectName" in df.columns:
            object_series = df["ObjectName"].dropna()
            object_series_filtered = object_series[~object_series.str.contains('|'.join(exclude_keywords), case=False)]
            counts = Counter(object_series_filtered.tolist())
            participant_objects[pid] = counts
    except:
        continue

# Create a DataFrame: rows = participants, cols = objects
all_objects = list(set(obj for counts in participant_objects.values() for obj in counts))
data = pd.DataFrame(0, index=participant_ids, columns=all_objects)

for pid in participant_ids:
    for obj, count in participant_objects[pid].items():
        data.loc[pid, obj] = count

# Create gender labels
genders = filtered_df.set_index("Participant ID")["Post_Dem_Gender"].to_dict()
male_ids = [pid for pid in participant_ids if genders.get(pid) == "1"]
female_ids = [pid for pid in participant_ids if genders.get(pid) == "2"]

# Run t-tests
ttest_results = {}
male_means = {}
female_means = {}

for obj in data.columns:
    male_vals = data.loc[male_ids, obj]
    female_vals = data.loc[female_ids, obj]
    t_stat, p_val = ttest_ind(male_vals, female_vals, equal_var=False)
    ttest_results[obj] = p_val
    male_means[obj] = male_vals.mean()
    female_means[obj] = female_vals.mean()

# Select top 10 objects with lowest p-values
top_tested = sorted(ttest_results, key=ttest_results.get)[:10]

# Prepare data for heatmap: average views per gender per object (only top 10 significant)
heatmap_data = pd.DataFrame({
    'Male': male_means,
    'Female': female_means
})

# Reorder by descending difference or p-value
heatmap_data = heatmap_data.loc[top_tested]

# Create annotation matrix with asterisks
annotations = []
for obj in top_tested:
    p = ttest_results[obj]
    if p < 0.001:
        annotations.append(['***', '***'])
    elif p < 0.01:
        annotations.append(['**', '**'])
    elif p < 0.05:
        annotations.append(['*', '*'])
    else:
        annotations.append(['', ''])
annotation_df = pd.DataFrame(annotations, index=top_tested, columns=['Male', 'Female'])

# Plot heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(heatmap_data, annot=annotation_df, fmt='', cmap="YlGnBu", linewidths=0.5, cbar_kws={'label': 'Avg View Count'})
plt.title("Heatmap of Object Views by Gender (Significant Differences)")
plt.xlabel("Gender")
plt.ylabel("Object Name")
plt.tight_layout()
plt.show()
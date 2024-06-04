import pandas as pd
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Generate base data
def generate_data(num_records):
    data = {
        "name": [fake.first_name() for _ in range(num_records)],
        "surname": [fake.last_name() for _ in range(num_records)],
        "date_of_birth": [fake.date_of_birth(minimum_age=18, maximum_age=50) for _ in range(num_records)],
        "email": [fake.email() for _ in range(num_records)],
        "address": [fake.address() for _ in range(num_records)]
    }
    return pd.DataFrame(data)

# Introduce related players and generate summary
def introduce_relationships(df, num_related=10000):
    # Define relationship types
    attributes = ["surname", "email", "address"]
    # Summary dictionary to store related counts
    summary = {attr: {} for attr in attributes}
    # Sample records to be related
    for _ in range(num_related):
        idx = random.randint(0, len(df) - 1)
        attribute = random.choice(attributes)
        related_indices = random.sample(range(len(df)), min(5, len(df)))
        for r_idx in related_indices:
            related_attribute_value = df.at[idx, attribute]
            df.at[r_idx, attribute] = related_attribute_value
            # Update summary
            if related_attribute_value not in summary[attribute]:
                summary[attribute][related_attribute_value] = 1
            else:
                summary[attribute][related_attribute_value] += 1
    return df, summary

# Main function to generate, relate data, and print summary
def main():
    num_records = 100000
    df = generate_data(num_records)
    df, summary = introduce_relationships(df)
    # Print summary
    print("Summary of Related Data:")
    for attribute, counts in summary.items():
        print(f"{attribute.capitalize()}:")
        for value, count in counts.items():
            print(f"  {value}: {count}")
        print()
    # Optionally, you can save the DataFrame to a CSV or JSON file
    df.to_csv("player_data.csv", index=False)

if __name__ == "__main__":
    main()

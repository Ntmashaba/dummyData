from confluent_kafka import Producer
import pandas as pd
from faker import Faker
import random
import json

# Initialize Faker
fake = Faker()

# Generate base data
def generate_data(num_records):
    data = {
        "name": [fake.first_name() for _ in range(num_records)],
        "surname": [fake.last_name() for _ in range(num_records)],
        "date_of_birth": [fake.date_of_birth(minimum_age=18, maximum_age=50) for _ in range(num_records)],
        "email": [fake.unique.email() for _ in range(num_records)],
        "address": [fake.address() for _ in range(num_records)]
    }
    return pd.DataFrame(data)

# Introduce related players and generate summary
def introduce_relationships(df, num_related=10000):
    modified_indices = set()
    for _ in range(num_related):
        idx = random.randint(0, len(df) - 1)
        surname = df.at[idx, "surname"]
        address = df.at[idx, "address"]
        
        modified_indices.add(idx)
        
        for _ in range(4):
            other_idx = random.choice([i for i in range(len(df)) if i != idx and i not in modified_indices])
            df.at[other_idx, "surname"] = surname
            df.at[other_idx, "address"] = address
            modified_indices.add(other_idx)
    
    return df

# Kafka Producer configuration
conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'data-generator'
}
producer = Producer(conf)

def send_to_kafka(df, topic):
    for _, row in df.iterrows():
        producer.produce(topic, key=row["email"], value=json.dumps(row.to_dict()))
    producer.flush()

def main():
    num_records = 100000
    df = generate_data(num_records)
    df = introduce_relationships(df)
    
    # Send DataFrame to Kafka
    send_to_kafka(df, 'player_data')

if __name__ == "__main__":
    main()

# Install necessary packages
# pip install pandas pymongo

import os
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# MongoDB connection setup
client = MongoClient('mongodb+srv://200541808:IqqPvMpTys2uLQWa@cluster1111.p6rdc1z.mongodb.net/')  # Replace with your MongoDB connection string
db = client['sales_database']  # Replace 'sales_database' with your MongoDB database name

# Directory containing CSV files
csv_directory = os.getcwd() + "\output_files"

def upload_csv_to_mongodb(csv_file_path, collection_name):
    # Read CSV file into a Pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Convert DataFrame to a list of dictionaries for MongoDB insertion
    data_to_insert = df.to_dict(orient='records')

    # Get the MongoDB collection
    collection = db[collection_name]

    # Insert data into MongoDB collection
    collection.insert_many(data_to_insert)

    print(f"Data from {csv_file_path} uploaded to MongoDB collection {collection_name}")

# Iterate over CSV files in the specified directory
for file_name in os.listdir(csv_directory):
    if file_name.endswith('.csv'):
        file_path = os.path.join(csv_directory, file_name)
        collection_name = os.path.splitext(file_name)[0]  # Use file name (excluding extension) as the collection name

        # Upload CSV data to MongoDB
        upload_csv_to_mongodb(file_path, collection_name)

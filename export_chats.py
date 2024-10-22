import os
import csv
from sqlalchemy import create_engine, text

# Database connection details
db_url = os.environ['DATABASE_URL']

# Create SQLAlchemy engine
engine = create_engine(db_url)

# SQL query
query = "SELECT * FROM chats ORDER BY time DESC"

# Execute query and fetch results
with engine.connect() as connection:
    result = connection.execute(text(query))
    rows = result.fetchall()

# Write results to CSV file
with open('output.test', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([col for col in result.keys()])  # Write header
    writer.writerows(rows)  # Write data

# Print summary
print(f"File 'output.test' created successfully.")
print(f"Number of rows: {len(rows)}")
print(f"Column names: {', '.join(result.keys())}")

import csv
import random

# Generate random data
val = random.uniform(0, 2)
data = [(round(time * 0.1, 1), val := val + random.uniform(-0.25, 0.30)) for time in range(100)]

# Write data to CSV file
with open("testing/test_files/random5.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["TIME", "ENERGY"])  # Write headers
    writer.writerows(data)  # Write data

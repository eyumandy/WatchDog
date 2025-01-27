import os

all_files = os.listdir('../faces')
all_files.remove("false_positives")

for file in all_files:
    os.remove(f"../faces/{file}")

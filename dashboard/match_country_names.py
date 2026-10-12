import csv
from pathlib import Path

from babel import Locale

csv_path = Path(__file__).with_name("country_names.csv")

arabic = Locale.parse("ar")
english = Locale.parse("en")

# Build a lookup using Babel's Arabic and English territory names
translations = {
    arabic_name: english.territories[code]
    for code, arabic_name in arabic.territories.items()
    if code in english.territories
}

with csv_path.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    columns = reader.fieldnames

matched = 0
unmatched = []

for row in rows:
    name = row["arabic_name"].strip()
    translation = translations.get(name)

    if translation:
        row["english_name"] = translation
        row["verification_status"] = "babel_matched"
        matched += 1
    else:
        unmatched.append(name)

with csv_path.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"Total categories: {len(rows)}")
print(f"Matched: {matched}")
print(f"Needs review: {len(unmatched)}")

print("\nUnmatched names:")
for name in unmatched:
    print(name)
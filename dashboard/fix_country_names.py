import csv
from pathlib import Path

csv_path = Path(__file__).with_name("country_names.csv")

corrections = {
    "آيرلندا": "Ireland",
    "إكوادور": "Ecuador",
    "إيران (جمهورية الإسلامية)": "Iran (Islamic Republic of)",
    "الأرض الخضراء": "Greenland",
    "الاتحاد الروسي": "Russian Federation",
    "الجمهورية التشيكية": "Czech Republic",
    "الجمهورية الدومينيكية": "Dominican Republic",
    "الجمهورية العربية السورية": "Syrian Arab Republic",
    "الكونغو": "Congo",
    "المجر": "Hungary",
    "المملكة المتحدة لبريطانيا العظمى وآيرلندا الشمالية": "United Kingdom",
    "الولايات المتحدة الأمريكية": "United States of America",
    "بروني دار السلام": "Brunei Darussalam",
    "بنن": "Benin",
    "بوليفيا (دولة - المتعددة القوميات)": "Bolivia (Plurinational State of)",
    "تايلند": "Thailand",
    "ترينداد وتوباغو": "Trinidad and Tobago",
    "جمهورية الكونغو الديموقراطية": "Democratic Republic of the Congo",
    "جمهورية تنزانيا المتحدة": "United Republic of Tanzania",
    "جمهورية كوريا": "Republic of Korea",
    "جمهورية لاو الديمقراطية الشعبية": "Lao People's Democratic Republic",
    "جمهورية مقدونيا اليوغوسلافية السابقة": "The former Yugoslav Republic of Macedonia",
    "جمهورية مولدوفا": "Republic of Moldova",
    "دول متعددة": "Multiple Countries",
    "زمبابوي": "Zimbabwe",
    "سان تومي وبرينسيبي": "Sao Tome and Principe",
    "سري لانكا": "Sri Lanka",
    "سيرا ليون": "Sierra Leone",
    "سيشيل": "Seychelles",
    "شيلي": "Chile",
    "عمان": "Oman",
    "غابون": "Gabon",
    "غينيا - بيساو": "Guinea-Bissau",
    "فلسطين": "Palestine",
    "فنزويلا (جمهورية البوليفارية)": "Venezuela (Bolivarian Republic of)",
    "فييت نام": "Viet Nam",
    "كابو فيردي": "Cabo Verde",
    "كوت ديفوار": "Côte d'Ivoire",
    "لكسمبرغ": "Luxembourg",
    "ليبريا": "Liberia",
    "مالطة": "Malta",
    "ملديف": "Maldives",
    "موزامبيق": "Mozambique",
    "ميانمار": "Myanmar",
    "نيوزلندا": "New Zealand",
}

with csv_path.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    columns = reader.fieldnames

if not columns:
    raise ValueError("Country CSV is empty.")

unmatched = [
    row["arabic_name"]
    for row in rows
    if not row["english_name"]
]

missing = set(unmatched) - set(corrections)

if missing:
    raise ValueError(f"Missing corrections: {sorted(missing)}")

for row in rows:
    if not row["english_name"]:
        row["english_name"] = corrections[row["arabic_name"]]
        row["verification_status"] = "manual_review_pending"

with csv_path.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"Total country categories: {len(rows)}")
print(f"English names completed: {sum(bool(r['english_name']) for r in rows)}")
print(f"Missing English names: {sum(not r['english_name'] for r in rows)}")
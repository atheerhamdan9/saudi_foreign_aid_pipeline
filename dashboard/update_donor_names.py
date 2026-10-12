import csv
from pathlib import Path

csv_path = Path(__file__).with_name("donor_names.csv")

names = {
    "وزارة المالية": "Ministry of Finance",
    "وزارة الطاقة": "Ministry of Energy",
    "الصندوق السعودي للتنمية": "The Saudi Fund for Development",
    "مركز الملك سلمان للإغاثة و الأعمال الإنسانية": "King Salman Humanitarian Aid and Relief Centre",
    "البرنامج السعودي لتنمية وإعمار اليمن": "The Saudi Development and Reconstruction Program for Yemen",
    "وزارة الخارجية": "Ministry of Foreign Affairs",
    "وزارة التعليم": "Ministry of Education",
    "جهات أخرى": "Other Agencies",
    "مؤسسة الملك عبدالله بن عبدالعزيز العالمية للأعمال الانسانية": "King Abdullah Bin Abdulaziz International Foundation for Humanitarian Work",
    "الهيئة السعودية العليا لمساعدة شعب البوسنة والهرسك": "Saudi High Commission Relief for Bosnia & Herzegovina",
    "الهلال الأحمر السعودي": "Saudi Red Crescent Authority",
    "وزارة البيئة والمياه والزراعة - المؤسسة العامة للري": "General Establishment for Irrigation",
    "مستشفى الملك فيصل التخصصي ومركز الأبحاث": "KFSH&RC",
    "برنامج استدامة الطلب على البترول": "Oil Sustainability Program",
    "وزارة الصحة": "Ministry of Health",
    "وزارة الحرس الوطني - الشؤون الصحية": "Ministry of National Guard - Health Affairs",
    "وزارة الإعلام": "Ministry of Media",
    "وزارة الشؤون الإسلامية والدعوة والإرشاد": "Ministry of Islamic Affairs, Dawah and Guidance",
    "وزارة النقل": "Ministry of Transportation",
    "هيئة الزكاة والضريبة والجمارك": "Zakat, Tax and Customs Authority",
    "الهيئة العامة للطيران المدني": "General Authority of Civil Aviation",
        "وزارة الثقافة": "Ministry of Culture",
}

with csv_path.open(encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    columns = reader.fieldnames

if not columns:
    raise ValueError("CSV file is empty.")

existing_names = [row["arabic_name"] for row in rows]

if len(existing_names) != len(set(existing_names)):
    raise ValueError("Duplicate Arabic names found.")

if set(existing_names) != set(names):
    raise ValueError("CSV names do not match the expected 22 donors.")

for row in rows:
    row["official_english_name"] = names[row["arabic_name"]]
    row["verification_status"] = "source_alignment_pending"

with csv_path.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=columns)
    writer.writeheader()
    writer.writerows(rows)

print(f"Successfully updated {len(rows)} donor names.")
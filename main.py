from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
import pytesseract
import re
from collections import defaultdict


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_name(line: str) -> str:
    line = line.upper()
    line = re.sub(r'[^A-Z0-9\s]', ' ', line)
    line = re.sub(r'\b(CREW|CCREWTRNR|CREWTRNR|CREWTTRNR|CREWTIAN|REWTRER|MAINT|REWTRNR)\b', '', line, flags=re.I)
    line = re.sub(r'\s+', ' ', line).strip()

    replacements = {
        "MARKHARVY": "MARK HARVY",
        "MARKHARY": "MARK HARY",
        "MARIELJANE": "MARIEL JANE",
        "DIONEILBENRED": "DIONEL BENREO",
        "HANZSEADRICK": "HANZ SEADRICK",
        "ROORIGO": "RODRIGO",
        "ROO RIGO": "RODRIGO",
        "ROSEMARY": "ROSEMARY",
        "JEANMAYER": "JEAN MAYER",
        "CIARACOLLIN": "CIARA COLLIN",
        "MELARISTEO": "MEL ARISTEO",
        "FREWENREI": "FREWEN REI",
        "ERORICH": "ERORICH",
        "JANINE": "JANINE",
    }

    compact = line.replace(" ", "")
    return replacements.get(compact, line)


def extract_matches(text: str):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    matches = []

    for line in lines:
        if "19/02" in line or "1902" in line:
            name_part = re.split(r'19/02|1902', line, maxsplit=1)[0]
            name = normalize_name(name_part)

            hours = None
            after_date_match = re.split(r'19/02|1902', line, maxsplit=1)
            after_date = after_date_match[1] if len(after_date_match) > 1 else ""
            m = re.search(r'\b(50|60|70|80|5|6|7|8|5\.0|6\.0|7\.0|8\.0)\b', after_date)
            if m:
                val = m.group(1)
                if val in {"60", "6", "6.0"}:
                    hours = "6.0"
                elif val in {"70", "7", "7.0"}:
                    hours = "7.0"
                elif val in {"80", "8", "8.0"}:
                    hours = "8.0"
                elif val in {"50", "5", "5.0"}:
                    hours = "5.0"
                else:
                    hours = val

            matches.append((name, hours))

    return matches


@app.post("/upload")
async def upload_images(images: list[UploadFile] = File(...)):
    combined = defaultdict(lambda: {"schedule_count": 0, "hours": 0.0})

    for image_file in images:
        contents = await image_file.read()
        img = Image.open(BytesIO(contents))
        text = pytesseract.image_to_string(img, config="--oem 3 --psm 6")
        matches = extract_matches(text)

        for name, hours in matches:
            combined[name]["schedule_count"] += 1
            if hours:
                try:
                    combined[name]["hours"] += float(hours)
                except:
                    pass

    table = []
    for name, data in combined.items():
        table.append({
            "name": name,
            "schedule_count": data["schedule_count"],
            "hours": round(data["hours"], 1)
        })

    table.sort(key=lambda x: x["name"])
    return {"results": table}
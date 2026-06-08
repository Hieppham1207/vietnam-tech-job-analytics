import json


def extract_jobs():

    with open(
        "data/raw/job_details.json",
        "r",
        encoding="utf-8"
    ) as f:

        jobs = json.load(f)

    return jobs

def extract_city(location):
    location = location.lower()

    if "hồ chí minh" in location or "ho chi minh" in location:
        return "Hồ Chí Minh"

    if "hà nội" in location or "ha noi" in location:
        return "Hà Nội"

    if "đà nẵng" in location or "da nang" in location:
        return "Đà Nẵng"

    if "cần thơ" in location or "can tho" in location:
        return "Cần Thơ"

    if "hải phòng" in location or "hai phong" in location:
        return "Hải Phòng"

    return "Khác"
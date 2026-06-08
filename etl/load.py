import json
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from extract import extract_city
load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL not found")

engine = create_engine(database_url)

# Đọc JSON
with open(
    "data/raw/jobs_detail.json",
    "r",
    encoding="utf-8"
) as f:

    jobs = json.load(f)

print(f"Loaded {len(jobs)} jobs")

def get_or_create(
    conn,
    table_name,
    value
):

    conn.execute(
        text(f"""
            INSERT INTO {table_name}(name)
            VALUES (:value)
            ON CONFLICT (name)
            DO NOTHING
        """),
        {
            "value": value
        }
    )

    result = conn.execute(
        text(f"""
            SELECT id
            FROM {table_name}
            WHERE name = :value
        """),
        {
            "value": value
        }
    )

    return result.fetchone()[0]

def get_or_create_job(
    conn,
    job
):

    result = conn.execute(
        text("""
            INSERT INTO jobs(
                url,
                title,
                company,
                working_mode,
                posted_at,
                job_description,
                requirements,
                benefits,
                source
            )
            VALUES(
                :url,
                :title,
                :company,
                :working_mode,
                :posted_at,
                :job_description,
                :requirements,
                :benefits,
                :source
            )
            ON CONFLICT(url)
            DO NOTHING
            RETURNING id
        """),
        {
            "url": job["url"],
            "title": job["title"],
            "company": job["company"],
            "working_mode": job["working_mode"],
            "posted_at": job["posted_at"],
            "job_description": job["job_description"],
            "requirements": job["requirements"],
            "benefits": job["benefits"],
            "source": "itviec"
        }
    )

    row = result.fetchone()

    if row:
        return row[0]

    result = conn.execute(
        text("""
            SELECT id
            FROM jobs
            WHERE url = :url
        """),
        {
            "url": job["url"]
        }
    )

    return result.fetchone()[0]

def insert_job_skill(
    conn,
    job_id,
    skill_id
):

    conn.execute(
        text("""
            INSERT INTO job_skills(
                job_id,
                skill_id
            )
            VALUES(
                :job_id,
                :skill_id
            )
            ON CONFLICT DO NOTHING
        """),
        {
            "job_id": job_id,
            "skill_id": skill_id
        }
    )

def insert_job_industry(
    conn,
    job_id,
    industry_id
):

    conn.execute(
        text("""
            INSERT INTO job_industries(
                job_id,
                industry_id
            )
            VALUES(
                :job_id,
                :industry_id
            )
            ON CONFLICT DO NOTHING
        """),
        {
            "job_id": job_id,
            "industry_id": industry_id
        }
    )

def insert_job_specialization(
    conn,
    job_id,
    specialization_id
):

    conn.execute(
        text("""
            INSERT INTO job_specializations(
                job_id,
                specialization_id
            )
            VALUES(
                :job_id,
                :specialization_id
            )
            ON CONFLICT DO NOTHING
        """),
        {
            "job_id": job_id,
            "specialization_id": specialization_id
        }
    )


def insert_job_location(conn,job_id,location):

    if not location:
        return
    city = extract_city(location)

    conn.execute(
        text("""
            INSERT INTO job_locations(
                job_id,
                location,
                city
            )
            VALUES(
                :job_id,
                :location,
                :city
            )
            ON CONFLICT DO NOTHING
        """),
        {
            "job_id": job_id,
            "location": location,
            "city": city
        }
    )



with engine.begin() as conn:

    for job in jobs:

        job_id = get_or_create_job(
            conn,
            job
        )

        # Skills
        for skill in job.get("skills", []):

            skill_id = get_or_create(
                conn,
                "skills",
                skill
            )

            insert_job_skill(
                conn,
                job_id,
                skill_id
            )

        # Industries
        for industry in job.get("industries", []):

            industry_id = get_or_create(
                conn,
                "industries",
                industry
            )

            insert_job_industry(
                conn,
                job_id,
                industry_id
            )

        # Specializations
        for specialization in job.get(
            "specializations",
            []
        ):

            specialization_id = get_or_create(
                conn,
                "specializations",
                specialization
            )

            insert_job_specialization(
                conn,
                job_id,
                specialization_id
            )

        # Locations
        for location in job.get(
            "locations",
            []
        ):

            insert_job_location(
                conn,
                job_id,
                location
            )

print("Done!")
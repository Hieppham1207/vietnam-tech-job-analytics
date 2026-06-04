CREATE TABLE IF NOT EXISTS jobs (
    job_id SERIAL PRIMARY KEY,

    title TEXT NOT NULL,

    company_name TEXT,

    salary_min INTEGER,

    salary_max INTEGER,

    location TEXT,

    source TEXT,

    job_url TEXT UNIQUE,

    description TEXT,

    posted_date DATE,

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id SERIAL PRIMARY KEY,

    skill_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id INTEGER REFERENCES jobs(job_id) ON DELETE CASCADE,

    skill_id INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,

    PRIMARY KEY(job_id, skill_id)
);
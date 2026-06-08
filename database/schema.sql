CREATE TABLE jobs (
    id BIGSERIAL PRIMARY KEY,

    url TEXT UNIQUE,

    title TEXT,
    company TEXT,

    working_mode TEXT,

    posted_at TIMESTAMP,
    crawl_time TIMESTAMP,

    job_description TEXT,
    requirements TEXT,
    benefits TEXT,

    source TEXT
);

CREATE TABLE skills (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE job_skills (
    job_id BIGINT REFERENCES jobs(id),
    skill_id BIGINT REFERENCES skills(id),

    PRIMARY KEY(job_id, skill_id)
);

CREATE TABLE industries (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE job_industries (
    job_id BIGINT REFERENCES jobs(id),
    industry_id BIGINT REFERENCES industries(id),

    PRIMARY KEY(job_id, industry_id)
);

CREATE TABLE job_locations (
    id BIGSERIAL PRIMARY KEY,

    job_id BIGINT REFERENCES jobs(id),

    location TEXT
);

CREATE TABLE specializations (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE job_specializations (
    job_id BIGINT REFERENCES jobs(id),
    specialization_id BIGINT REFERENCES specializations(id),

    PRIMARY KEY(job_id, specialization_id)
);
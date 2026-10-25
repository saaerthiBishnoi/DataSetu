-- ============================================================
-- DataSetu - India Public Data Analytics Platform
-- Education Module (v1.0) - Database Schema
-- ============================================================
-- This script creates the full star schema: 5 dimension tables
-- and 8 fact tables, following the design finalized in our 
-- ER diagram.
-- ============================================================


-- ============================================================
-- SECTION 1: DIMENSION TABLES
-- These hold descriptive, reusable reference data (states, 
-- years, gender, management type, teacher qualification).
-- ============================================================

-- Dim_State: master list of all Indian states/UTs used across the project
CREATE TABLE Dim_State (
    state_id SERIAL PRIMARY KEY,     -- auto-incrementing unique ID
    state_name VARCHAR(100) UNIQUE NOT NULL  -- e.g. "Kerala", "Bihar"
);

-- Dim_Year: master list of years covered by our datasets
CREATE TABLE Dim_Year (
    year_id SERIAL PRIMARY KEY,
    year_value INT UNIQUE NOT NULL   -- e.g. 2017, 2018
);

-- Dim_Gender: master list of gender categories used in some datasets
CREATE TABLE Dim_Gender (
    gender_id SERIAL PRIMARY KEY,
    gender_name VARCHAR(20) UNIQUE NOT NULL  -- e.g. "Boys", "Girls", "Total"
);

-- Dim_Management: master list of school management types
CREATE TABLE Dim_Management (
    management_id SERIAL PRIMARY KEY,
    management_name VARCHAR(50) UNIQUE NOT NULL  
    -- e.g. "Government", "Government Aided", "Private Unaided", "Other"
);

-- Dim_Qualification: master list of teacher qualification levels
CREATE TABLE Dim_Qualification (
    qualification_id SERIAL PRIMARY KEY,
    qualification_name VARCHAR(50) UNIQUE NOT NULL
    -- e.g. "Below Secondary", "Graduate", "PhD/Post Doctoral"
);


-- ============================================================
-- SECTION 2: FACT TABLES
-- These hold the actual measured data (counts, percentages),
-- with foreign keys linking back to the dimension tables above.
-- ============================================================

-- Fact_Schools_Total: total school count by state, year, management type
-- Source: Number of Schools by School Management.csv
CREATE TABLE Fact_Schools_Total (
    fact_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES Dim_State(state_id),
    year_id INT REFERENCES Dim_Year(year_id),
    management_id INT REFERENCES Dim_Management(management_id),
    school_count INT
);

-- Fact_Schools_ByCategory: school count by state, year, management, 
-- AND school category (Primary/Secondary/etc.)
-- Source: Number of Schools by Management and School Category.csv
CREATE TABLE Fact_Schools_ByCategory (
    fact_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES Dim_State(state_id),
    year_id INT REFERENCES Dim_Year(year_id),
    management_id INT REFERENCES Dim_Management(management_id),
    school_category VARCHAR(50),   -- e.g. "Primary (I-V)"
    school_count INT
);

-- Fact_Teachers_Management: % of teachers by state, year, gender, management
-- Source: Distribution of Teachers by Management.csv
CREATE TABLE Fact_Teachers_Management (
    fact_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES Dim_State(state_id),
    year_id INT REFERENCES Dim_Year(year_id),
    gender_id INT REFERENCES Dim_Gender(gender_id),
    management_id INT REFERENCES Dim_Management(management_id),
    teacher_pct FLOAT
);

-- Fact_Teachers_Qualification: % of teachers by state, year, qualification level
-- Source: Distribution of Teachers by Academic Qualification.csv
CREATE TABLE Fact_Teachers_Qualification (
    fact_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES Dim_State(state_id),
    year_id INT REFERENCES Dim_Year(year_id),
    qualification_id INT REFERENCES Dim_Qualification(qualification_id),
    teacher_pct FLOAT
);

-- Fact_ExamResults: exam appeared count + pass percentage, by state, year, 
-- management, AND grade (X or XII) - combines 2 original CSV files
-- Source: Examination Results Grade X + Grade XII (unioned)
CREATE TABLE Fact_ExamResults (
    fact_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES Dim_State(state_id),
    year_id INT REFERENCES Dim_Year(year_id),
    management_id INT REFERENCES Dim_Management(management_id),
    grade VARCHAR(5),        -- "X" or "XII"
    appeared INT,
    pass_pct FLOAT
);

-- Fact_Retention: retention rate by state, year, gender, educational stage
-- Source: Retention Rate by Educational Stage.csv
CREATE TABLE Fact_Retention (
    fact_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES Dim_State(state_id),
    year_id INT REFERENCES Dim_Year(year_id),
    gender_id INT REFERENCES Dim_Gender(gender_id),
    stage VARCHAR(50),       -- e.g. "Primary (I-V)"
    retention_rate FLOAT
);

-- Fact_Schools_PTR_Range: % of schools falling into each Pupil-Teacher-Ratio 
-- range, by state, year, school category, and management SCOPE 
-- (note: only 2 scopes here - "All Management" / "Government" - 
-- NOT the standard 4-category Dim_Management, so no FK to that table)
-- Source: Distribution of Schools by School Category and Range of PTR.csv
CREATE TABLE Fact_Schools_PTR_Range (
    fact_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES Dim_State(state_id),
    year_id INT REFERENCES Dim_Year(year_id),
    school_category VARCHAR(50),
    ptr_range VARCHAR(20),        -- e.g. "<=30", "30-35"
    management_scope VARCHAR(20), -- "All Management" or "Government"
    pct_schools FLOAT
);

-- Fact_Infrastructure: school facility availability (internet, computer, 
-- drinking water, boys/girls toilet), by state, year, management, 
-- AND facility type - combines 5 original CSV files
-- Source: Internet, Computer, Drinking Water, Boys Toilet, Girls Toilet (unioned)
CREATE TABLE Fact_Infrastructure (
    fact_id SERIAL PRIMARY KEY,
    state_id INT REFERENCES Dim_State(state_id),
    year_id INT REFERENCES Dim_Year(year_id),
    management_id INT REFERENCES Dim_Management(management_id),
    facility_type VARCHAR(30),    -- "Internet", "Computer", "Drinking Water", 
                                    -- "Boys Toilet", "Girls Toilet"
    total_schools INT,
    schools_with_facility INT,
    pct_with_facility FLOAT
);


-- ============================================================
-- END OF SCHEMA CREATION
-- Next step: populate Dim tables first (state, year, gender, 
-- management, qualification lookup values), THEN load Fact 
-- tables (which require valid foreign keys to already exist).
-- ============================================================








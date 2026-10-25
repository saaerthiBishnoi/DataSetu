-- ============================================================
-- VIEW 1: Infrastructure Gap by Management Type
-- ============================================================
-- Business question: What % of Government vs Private vs Aided 
-- schools have internet, computers, drinking water, and toilets 
-- - by state?
--
-- Tables used: Fact_Infrastructure, Dim_State, Dim_Year, 
-- Dim_Management
-- ============================================================

CREATE VIEW vw_infrastructure_gap_by_management AS
SELECT
    ds.state_name,
    dy.year_value,
    dm.management_name,
    fi.facility_type,
    fi.total_schools,
    fi.schools_with_facility,
    fi.pct_with_facility
FROM Fact_Infrastructure fi
JOIN Dim_State ds ON fi.state_id = ds.state_id
JOIN Dim_Year dy ON fi.year_id = dy.year_id
JOIN Dim_Management dm ON fi.management_id = dm.management_id;



-- ============================================================
-- VIEW 2: Teacher Qualification vs Exam Performance
-- ============================================================
-- Business question: Do states with more highly-qualified teachers 
-- (Graduate and above) show better Grade X/XII pass percentages?
--
-- Tables used: Fact_Teachers_Qualification, Fact_ExamResults, 
-- Dim_State, Dim_Year
--
-- Note: Exam results are aggregated to state+year level (weighted 
-- average pass % across all management types and both grades), 
-- since qualification data has no management/grade split to join on.
-- ============================================================

CREATE VIEW vw_teacher_qualification_vs_exam_performance AS
WITH exam_summary AS (
    -- Aggregate exam results to one weighted-average pass % per state+year
    SELECT
        state_id,
        year_id,
        SUM(pass_pct * appeared) / NULLIF(SUM(appeared), 0) AS weighted_avg_pass_pct
    FROM Fact_ExamResults
    GROUP BY state_id, year_id
)
SELECT
    ds.state_name,
    dy.year_value,
    dq.qualification_name,
    ftq.teacher_pct,
    es.weighted_avg_pass_pct
FROM Fact_Teachers_Qualification ftq
JOIN Dim_State ds ON ftq.state_id = ds.state_id
JOIN Dim_Year dy ON ftq.year_id = dy.year_id
JOIN Dim_Qualification dq ON ftq.qualification_id = dq.qualification_id
JOIN exam_summary es ON ftq.state_id = es.state_id AND ftq.year_id = es.year_id;




-- ============================================================
-- VIEW 3: Schools PTR (Pupil-Teacher Ratio) Health
-- ============================================================
-- Business question: Which states have the highest % of schools 
-- with an unhealthy Pupil-Teacher Ratio (over 40 students per 
-- teacher)?
--
-- Tables used: Fact_Schools_PTR_Range, Dim_State, Dim_Year
--
-- Note: "Unhealthy" PTR is defined here as ranges 40-45 or >50 
-- (i.e., excludes the healthier bands <=30, 30-35, 35-40, 45-50).
-- This threshold is a reasonable simplification for v1.0 - can be 
-- adjusted later based on education policy standards if needed.
-- ============================================================

CREATE VIEW vw_schools_ptr_health AS
SELECT
    ds.state_name,
    dy.year_value,
    f.school_category,
    f.ptr_range,
    f.management_scope,
    f.pct_schools,
    CASE 
        WHEN f.ptr_range IN ('40-45', '>50') THEN 'Unhealthy'
        ELSE 'Healthy'
    END AS ptr_health_flag
FROM Fact_Schools_PTR_Range f
JOIN Dim_State ds ON f.state_id = ds.state_id
JOIN Dim_Year dy ON f.year_id = dy.year_id;



-- ============================================================
-- VIEW 4: School Ownership Distribution
-- ============================================================
-- Business question: How is school ownership (Govt/Aided/Private/
-- Other) distributed across states and school categories 
-- (Primary/Secondary/etc)?
--
-- Tables used: Fact_Schools_Total, Fact_Schools_ByCategory, 
-- Dim_State, Dim_Year, Dim_Management
--
-- Note: Combines two fact tables with different grains using 
-- UNION ALL - "school_category" is NULL for rows from 
-- Fact_Schools_Total (which has no category breakdown), and 
-- populated for rows from Fact_Schools_ByCategory.
-- ============================================================

CREATE VIEW vw_school_ownership_distribution AS
SELECT
    ds.state_name,
    dy.year_value,
    dm.management_name,
    NULL AS school_category,
    fst.school_count,
    'Total' AS source_level
FROM Fact_Schools_Total fst
JOIN Dim_State ds ON fst.state_id = ds.state_id
JOIN Dim_Year dy ON fst.year_id = dy.year_id
JOIN Dim_Management dm ON fst.management_id = dm.management_id

UNION ALL

SELECT
    ds.state_name,
    dy.year_value,
    dm.management_name,
    fsc.school_category,
    fsc.school_count,
    'ByCategory' AS source_level
FROM Fact_Schools_ByCategory fsc
JOIN Dim_State ds ON fsc.state_id = ds.state_id
JOIN Dim_Year dy ON fsc.year_id = dy.year_id
JOIN Dim_Management dm ON fsc.management_id = dm.management_id;






-- ============================================================
-- VIEW 5: Gender Gap in Retention
-- ============================================================
-- Business question: Which states show the largest gap between 
-- Boys' and Girls' retention rates, by educational stage?
--
-- Tables used: Fact_Retention, Dim_State, Dim_Year, Dim_Gender
--
-- Note: Uses a self-join pattern - pulls Boys and Girls retention 
-- rates side by side in the same row (rather than separate rows), 
-- and calculates the gap directly, making it easy to sort/filter 
-- by "biggest gap" in Power BI.
-- ============================================================

CREATE VIEW vw_gender_gap_in_retention AS
SELECT
    ds.state_name,
    dy.year_value,
    boys.stage,
    boys.retention_rate AS boys_retention_rate,
    girls.retention_rate AS girls_retention_rate,
    boys.retention_rate - girls.retention_rate AS retention_gap
FROM Fact_Retention boys
JOIN Dim_State ds ON boys.state_id = ds.state_id
JOIN Dim_Year dy ON boys.year_id = dy.year_id
JOIN Dim_Gender dg_boys ON boys.gender_id = dg_boys.gender_id AND dg_boys.gender_name = 'Boys'
JOIN Fact_Retention girls 
    ON boys.state_id = girls.state_id 
    AND boys.year_id = girls.year_id 
    AND boys.stage = girls.stage
JOIN Dim_Gender dg_girls ON girls.gender_id = dg_girls.gender_id AND dg_girls.gender_name = 'Girls';





-- ============================================================
-- VIEW 6 (REPLACEMENT): School Category Distribution vs PTR Health
-- ============================================================
-- Business question: In states with a higher share of Secondary/
-- Higher-Secondary schools relative to Primary schools, do we see 
-- worse Pupil-Teacher Ratios - suggesting resource strain as 
-- schooling scales up?
--
-- Tables used: Fact_Schools_ByCategory, Fact_Schools_PTR_Range, 
-- Dim_State, Dim_Year
--
-- Note: Joined on state+year only (school_category values differ 
-- in naming/granularity between the two source tables, so they 
-- are NOT joined on category directly - this view lets Power BI 
-- compare school-category counts against PTR-range percentages 
-- side by side, at the state+year level).
-- ============================================================

CREATE VIEW vw_school_category_vs_ptr_health AS
SELECT
    ds.state_name,
    dy.year_value,
    fsc.school_category,
    fsc.school_count,
    ptr.ptr_range,
    ptr.management_scope,
    ptr.pct_schools
FROM Fact_Schools_ByCategory fsc
JOIN Dim_State ds ON fsc.state_id = ds.state_id
JOIN Dim_Year dy ON fsc.year_id = dy.year_id
JOIN Fact_Schools_PTR_Range ptr 
    ON fsc.state_id = ptr.state_id 
    AND fsc.year_id = ptr.year_id;


SELECT * FROM vw_school_category_vs_ptr_health
WHERE state_name = 'Kerala'
ORDER BY year_value, school_category, ptr_range;



-- ============================================================
-- VIEW 7: Exam Performance by Management Type
-- ============================================================
-- Business question: Do Government schools have lower pass 
-- percentages than Private schools, and does the gap widen at 
-- Grade XII vs Grade X?
--
-- Tables used: Fact_ExamResults, Dim_State, Dim_Year, Dim_Management
-- ============================================================

CREATE VIEW vw_exam_performance_by_management AS
SELECT
    ds.state_name,
    dy.year_value,
    dm.management_name,
    fe.grade,
    fe.appeared,
    fe.pass_pct
FROM Fact_ExamResults fe
JOIN Dim_State ds ON fe.state_id = ds.state_id
JOIN Dim_Year dy ON fe.year_id = dy.year_id
JOIN Dim_Management dm ON fe.management_id = dm.management_id;


SELECT * FROM vw_exam_performance_by_management
WHERE state_name = 'Kerala'
ORDER BY year_value, grade, management_name;



-- ============================================================
-- VIEW 8: Infrastructure Trend Over Time
-- ============================================================
-- Business question: Has internet/computer access in schools 
-- improved year-over-year, and is improvement equal across 
-- management types?
--
-- Tables used: Fact_Infrastructure, Dim_State, Dim_Year, 
-- Dim_Management
-- ============================================================

CREATE VIEW vw_infrastructure_trend_over_time AS
SELECT
    ds.state_name,
    dy.year_value,
    dm.management_name,
    fi.facility_type,
    fi.pct_with_facility
FROM Fact_Infrastructure fi
JOIN Dim_State ds ON fi.state_id = ds.state_id
JOIN Dim_Year dy ON fi.year_id = dy.year_id
JOIN Dim_Management dm ON fi.management_id = dm.management_id
ORDER BY ds.state_name, dm.management_name, fi.facility_type, dy.year_value;


SELECT * FROM vw_infrastructure_trend_over_time
WHERE state_name = 'Kerala' AND facility_type = 'Internet'
ORDER BY year_value, management_name;



-- ============================================================
-- VIEW 9: Teacher Distribution by Management Type
-- ============================================================
-- Business question: How is the teaching workforce distributed 
-- across Government, Aided, and Private schools, by state and year?
--
-- Tables used: Fact_Teachers_Management, Dim_State, Dim_Year, 
-- Dim_Gender, Dim_Management
-- ============================================================

CREATE VIEW vw_teacher_distribution_by_management AS
SELECT
    ds.state_name,
    dy.year_value,
    dg.gender_name,
    dm.management_name,
    ftm.teacher_pct
FROM Fact_Teachers_Management ftm
JOIN Dim_State ds ON ftm.state_id = ds.state_id
JOIN Dim_Year dy ON ftm.year_id = dy.year_id
JOIN Dim_Gender dg ON ftm.gender_id = dg.gender_id
JOIN Dim_Management dm ON ftm.management_id = dm.management_id;


SELECT * FROM vw_teacher_distribution_by_management
WHERE state_name = 'Kerala'
ORDER BY year_value, gender_name, management_name;



SELECT 'vw_infrastructure_gap_by_management' AS view_name, COUNT(*) AS row_count FROM vw_infrastructure_gap_by_management
UNION ALL
SELECT 'vw_teacher_qualification_vs_exam_performance', COUNT(*) FROM vw_teacher_qualification_vs_exam_performance
UNION ALL
SELECT 'vw_schools_ptr_health', COUNT(*) FROM vw_schools_ptr_health
UNION ALL
SELECT 'vw_school_ownership_distribution', COUNT(*) FROM vw_school_ownership_distribution
UNION ALL
SELECT 'vw_gender_gap_in_retention', COUNT(*) FROM vw_gender_gap_in_retention
UNION ALL
SELECT 'vw_school_category_vs_ptr_health', COUNT(*) FROM vw_school_category_vs_ptr_health
UNION ALL
SELECT 'vw_exam_performance_by_management', COUNT(*) FROM vw_exam_performance_by_management
UNION ALL
SELECT 'vw_infrastructure_trend_over_time', COUNT(*) FROM vw_infrastructure_trend_over_time
UNION ALL
SELECT 'vw_teacher_distribution_by_management', COUNT(*) FROM vw_teacher_distribution_by_management;




SELECT source_level, COUNT(*) as row_count, SUM(school_count) as total
FROM vw_school_ownership_distribution
GROUP BY source_level;


SELECT MIN(pct_with_facility), MAX(pct_with_facility), AVG(pct_with_facility)
FROM vw_infrastructure_gap_by_management
WHERE total_schools > 0;


SELECT facility_type, management_name, MIN(pct_with_facility), MAX(pct_with_facility)
FROM vw_infrastructure_gap_by_management
GROUP BY facility_type, management_name
ORDER BY MAX(pct_with_facility) DESC
LIMIT 10;


CREATE OR REPLACE VIEW vw_infrastructure_gap_by_management AS
SELECT
    ds.state_name,
    dy.year_value,
    dm.management_name,
    fi.facility_type,
    fi.total_schools,
    fi.schools_with_facility,
    fi.pct_with_facility
FROM Fact_Infrastructure fi
JOIN Dim_State ds ON fi.state_id = ds.state_id
JOIN Dim_Year dy ON fi.year_id = dy.year_id
JOIN Dim_Management dm ON fi.management_id = dm.management_id
WHERE fi.total_schools > 0;


SELECT MIN(pct_with_facility), MAX(pct_with_facility), MIN(total_schools)
FROM vw_infrastructure_gap_by_management;


CREATE OR REPLACE VIEW vw_infrastructure_gap_by_management AS
SELECT
    ds.state_name,
    dy.year_value,
    dm.management_name,
    fi.facility_type,
    fi.total_schools,
    fi.schools_with_facility,
    fi.pct_with_facility
FROM Fact_Infrastructure fi
JOIN Dim_State ds ON fi.state_id = ds.state_id
JOIN Dim_Year dy ON fi.year_id = dy.year_id
JOIN Dim_Management dm ON fi.management_id = dm.management_id
WHERE fi.total_schools > 0 AND fi.pct_with_facility <= 100;


SELECT MIN(pct_with_facility), MAX(pct_with_facility), COUNT(*)
FROM vw_infrastructure_gap_by_management;


CREATE OR REPLACE VIEW vw_infrastructure_trend_over_time AS
SELECT
    ds.state_name,
    dy.year_value,
    dm.management_name,
    fi.facility_type,
    fi.pct_with_facility
FROM Fact_Infrastructure fi
JOIN Dim_State ds ON fi.state_id = ds.state_id
JOIN Dim_Year dy ON fi.year_id = dy.year_id
JOIN Dim_Management dm ON fi.management_id = dm.management_id
WHERE fi.total_schools > 0 AND fi.pct_with_facility <= 100
ORDER BY ds.state_name, dm.management_name, fi.facility_type, dy.year_value;
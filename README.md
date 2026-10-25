# DataSetu — India Public Data Analytics Platform

**DataSetu** is an education-data analytics project that transforms Indian government school-education datasets into clean CSVs, a PostgreSQL database, SQL views, and a Power BI dashboard.

**Current module:** Education Intelligence  
**Primary data sources:** UDISE Flash Statistics and UDISE+ via NDAP (NITI Aayog)  
**Core stack:** Python, pandas, PostgreSQL, SQLAlchemy, Power BI, HTML, CSS, and JavaScript

## Overview

Government education data is useful for understanding school infrastructure, teacher distribution, retention, pupil–teacher ratios, and examination outcomes, but the source files can be difficult to compare directly. DataSetu provides a repeatable workflow for cleaning the selected datasets, organizing them in a relational database, and exposing analysis-ready views for visualization.

### What the project includes

- 13 selected source datasets and their cleaned CSV outputs.
- Python scripts for cleaning, dimension loading, and fact-table loading.
- A PostgreSQL dimensional model with 5 dimension tables and 8 fact tables.
- 9 SQL views designed around education-analysis questions.
- A Power BI report with Overview, Infrastructure, and Academic Performance pages.
- A website front end in the `Website/` folder.

## Data workflow

```text
UDISE / UDISE+ source data
          ↓
Python + pandas cleaning
          ↓
Cleaned CSV files
          ↓
PostgreSQL star schema
          ↓
9 SQL analysis views
          ↓
Power BI dashboard and website
```

## Data sources

The current version uses 13 datasets from two collections:

- **UDISE Flash Statistics** — 8 datasets covering school counts, school categories, teacher distribution, teacher qualifications, pupil–teacher-ratio ranges, retention, and Grade X/XII examination results.
- **UDISE+** — 5 datasets covering school access to internet, computers, drinking water, boys' toilets, and girls' toilets.

The raw source files are stored in `DataSet/`. The cleaned outputs are stored in `Cleaned/`. The `DATASET FOR LATER ADV VERSION/` folder contains data reserved for possible future expansion and is not part of the current 13-dataset module.

## Data preparation

The cleaning workflow uses pandas to standardize column names and categories, reshape wide source files into analysis-friendly rows, and address inconsistencies found during validation. Important considerations include:

- Standardizing state and Union Territory names across files.
- Mapping detailed management categories to a common set where appropriate.
- Handling percentage values carefully when aggregating data; percentages should not be summed like counts.
- Checking for missing dimension lookups and implausible percentage values before loading.

Source datasets differ in their available years and levels of detail. As a result, not every analysis can compare every indicator over the same period. Refer to the source files and SQL views when interpreting results.

## Database design

The PostgreSQL model uses a dimensional, star-schema-style design.

### Dimension tables

| Table | Purpose |
|---|---|
| `Dim_State` | State and Union Territory names |
| `Dim_Year` | Year values |
| `Dim_Gender` | Gender categories |
| `Dim_Management` | School management categories |
| `Dim_Qualification` | Teacher qualification categories |

### Fact tables

| Table | Purpose |
|---|---|
| `Fact_Schools_Total` | School counts by state, year, and management |
| `Fact_Schools_ByCategory` | School counts by school category |
| `Fact_Teachers_Management` | Teacher distribution by management and gender |
| `Fact_Teachers_Qualification` | Teacher distribution by qualification |
| `Fact_ExamResults` | Examination outcomes by grade and management |
| `Fact_Retention` | Retention indicators by stage and gender |
| `Fact_Schools_PTR_Range` | School distribution by pupil–teacher-ratio range |
| `Fact_Infrastructure` | Facility availability, consolidated by facility type |

The recorded load documented for this version contains **19,682 fact rows** and **65 dimension rows**. These counts describe the snapshot used while documenting the project; they may differ if the data is cleaned or loaded again.

## SQL analysis views

The SQL views provide a readable analysis layer for Power BI without requiring each visual to recreate the underlying joins.

| View | Analysis question |
|---|---|
| `vw_infrastructure_gap_by_management` | How does reported facility access differ by management and state? |
| `vw_teacher_qualification_vs_exam_performance` | How do teacher qualifications compare with examination outcomes? |
| `vw_schools_ptr_health` | How are schools distributed across pupil–teacher-ratio ranges? |
| `vw_school_ownership_distribution` | How are schools distributed by management and category? |
| `vw_gender_gap_in_retention` | What is the difference between boys' and girls' retention indicators? |
| `vw_school_category_vs_ptr_health` | How do school categories compare with pupil–teacher-ratio patterns? |
| `vw_exam_performance_by_management` | How do examination outcomes vary by grade and management? |
| `vw_infrastructure_trend_over_time` | How does reported facility access change over time? |
| `vw_teacher_distribution_by_management` | How is the teaching workforce distributed by management? |

## Power BI dashboard

The Power BI report is available at `DashBoard/DataSetu_dashboard.pbix`.

The report contains three pages:

1. **Overview** — headline indicators and state-level comparisons.
2. **Infrastructure** — facility access and trends by management.
3. **Academic Performance** — examination outcomes, teacher qualifications, retention, and pupil–teacher-ratio indicators.

The report was designed to use SQL views as its analysis layer. To refresh data from a local PostgreSQL database, the database must be available and the Power BI connection configured for that environment.

## Repository structure

```text
DataSetu/
├── Cleaned/                                  # Cleaned CSV outputs
├── DATASET FOR LATER ADV VERSION/             # Candidate data for future versions
├── DashBoard/
│   └── DataSetu_dashboard.pbix                # Power BI report
├── DataSet/                                  # Raw source datasets
├── Scripts/
│   ├── Cleaning/                              # Data-cleaning scripts
│   ├── dimension_loading_and_inserting/       # Dimension loading scripts
│   └── fact_loading/                          # Fact loading scripts
├── SQL Script for Creating dim and fact tables/
│   ├── Sql_Script.sql                         # Table/schema creation
│   └── views.sql                              # SQL analysis views
├── Website/                                  # Website source files
├── DataSetu_Review1.pdf                       # Project review document
├── Dataset collection INFO.pdf                # Dataset research notes
└── README.md
```

## Setup and run

These steps describe the local workflow. The dashboard requires Power BI Desktop, and the database scripts require a local PostgreSQL instance.

### Prerequisites

- Python 3 and `pip`
- PostgreSQL and pgAdmin (or another PostgreSQL client)
- Power BI Desktop to open the `.pbix` report

### 1. Clone the repository

```bash
git clone https://github.com/saaerthiBishnoi/DataSetu.git
cd DataSetu
```

### 2. Install Python dependencies

```bash
pip install pandas sqlalchemy psycopg2-binary python-dotenv openpyxl
```

### 3. Configure the database connection

Create a `.env` file in the repository root. Use your own local PostgreSQL credentials; do not commit this file.

```dotenv
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/DataSetu
```

Replace `YOUR_PASSWORD` with your PostgreSQL password. If you use a script that downloads data directly from NDAP, configure its API key as required by that script. The included raw CSV files can be used as the starting point for the cleaning workflow.

### 4. Create the database and tables

1. Create a PostgreSQL database named `DataSetu`.
2. Open the Query Tool for that database in pgAdmin.
3. Open and execute `SQL Script for Creating dim and fact tables/Sql_Script.sql` to create the tables.

### 5. Clean the source datasets

Run the required Python scripts from `Scripts/Cleaning/`. Run them from the repository root and check their output in `Cleaned/`. The exact script to run depends on the source file being prepared.

### 6. Load dimensions, then facts

Run the scripts in `Scripts/dimension_loading_and_inserting/` first. After the dimension tables are populated, run the required scripts in `Scripts/fact_loading/` to populate the fact tables. Check the console output and database row counts after each stage.

### 7. Create the SQL views

After the tables exist, execute `SQL Script for Creating dim and fact tables/views.sql` in pgAdmin. Verify that the nine views are present before connecting Power BI.

### 8. Open the dashboard

Open `DashBoard/DataSetu_dashboard.pbix` in Power BI Desktop. If connecting it to your local database, use the PostgreSQL server and database configured for your environment, then refresh the model as needed.

> **Note:** The steps above describe the intended pipeline, but the project has not been packaged as a one-command installer. Review the scripts and local PostgreSQL setup before running the workflow on a new machine.

## Tech stack

| Technology | Role |
|---|---|
| Python, pandas | Data cleaning and transformation |
| PostgreSQL | Relational storage and dimensional model |
| SQLAlchemy, psycopg2 | Python-to-PostgreSQL loading |
| SQL views | Reusable analysis layer |
| Power BI Desktop | Dashboard and report authoring |
| HTML, CSS, JavaScript | Website front end |
| python-dotenv | Loading local environment variables |

## DBMS concepts demonstrated

- Primary keys and foreign keys
- Referential integrity
- Dimension and fact table design
- Data normalization and surrogate keys
- Joins, aggregations, filtering, and `CASE` expressions
- SQL views as an abstraction layer for analytics
- ETL: extract, transform, and load

## Limitations and interpretation

- The repository represents a project snapshot; data does not automatically refresh unless a refresh process is configured.
- Source files do not always cover identical years or levels of geographic detail, so comparisons should be made only across compatible periods and categories.
- Some source values may be anomalous or require interpretation. Check the original source and cleaning logic before using a value for policy or research claims.
- Power BI refresh from a local database requires a working connection; cloud refresh would need appropriate hosting and credentials.

## Future improvements

- Automate dataset updates and validation.
- Host the database in a managed environment and configure scheduled refresh.
- Improve website deployment and accessibility.
- Expand the platform to other public-data domains when compatible sources are available.

## Author

**Saarthi Bishnoi**  
VIT Vellore — Computer Science and Engineering (Information Security)  
Registration number: `24BCI0092`

## Data attribution

DataSetu uses school-education datasets from NDAP (NITI Aayog) and UDISE/UDISE+ (Ministry of Education, Government of India). Please consult the original dataset metadata and terms when reusing the underlying data.

---

*DataSetu — Education Intelligence Module*


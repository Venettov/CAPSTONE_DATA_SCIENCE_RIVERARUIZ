# Population & Migration Forecasting in Puerto Rico

**Predictive Modeling of Population Decline, Economic Resilience, and Demographic Momentum in Puerto Rico**

**Capstone Project – Spring 2026**  
**Course:** 56:219:603:91 – Master’s Project  
**Program:** M.S. in Data Science  
**Institution:** Rutgers University  
**Student:** Jose Andres RiveraRuiz  

This repository contains an end-to-end data science project for forecasting population change in Puerto Rico and evaluating disaster and policy-response scenarios. The project uses detailed local-level data as the foundation for regional and islandwide population analysis. It combines data integration, feature engineering, predictive modeling, disaster scenario forecasting, and policy stress testing into one workflow.

The main modeling work is located in the `model_population_analysis/` folder. The data preparation workflow is located in the `data/` folder. The remaining folders and HTML files support the public dashboard and website used to present the results.

Live dashboard / website:  
https://venettov.github.io/CAPSTONE_DATA_SCIENCE_RIVERARUIZ/index.html

---

## Project Overview

Puerto Rico has experienced sustained population decline driven by a complex interaction of migration, economic stress, low fertility, population aging, fiscal pressure, and exposure to natural hazards. While descriptive dashboards help visualize these patterns, planners and decision-makers also need predictive, interpretable, and policy-relevant analytics that can support long-term resilience planning.

This capstone develops a predictive modeling and scenario-analysis framework that integrates demographic, economic, fertility, social vulnerability, public safety, business activity, and hazard-exposure data to forecast population change and evaluate future outcomes. A core contribution of the project is the explicit modeling of demographic momentum: the structural effect of low birth rates, aging, and previous population trends that can continue to drive population decline even when short-term migration or disaster shocks are not the only explanation.

The project originally began as a study of population decline, but it evolved into a broader analysis of population change. This shift allows the framework to capture localized resilience, stabilization, and recovery-rebound scenarios rather than assuming that all regions follow the same downward trajectory.

---

## What It Is

This project analyzes Puerto Rico's population change after 2010, a period shaped by economic stress, outward migration, natural population decrease, Hurricane Maria, and the 2020 seismic sequence. Rather than treating population decline as a simple islandwide trend, the project studies population change as a structured, spatial, and persistent process.

The analysis shows that population decline in Puerto Rico is:

- **Structured**: shaped by economic, demographic, social vulnerability, public safety, business activity, and recovery-capacity conditions.
- **Spatial**: distributed differently across Puerto Rico's regions instead of occurring evenly across the island.
- **Persistent**: strongly influenced by previous population trends, lagged population change, and rolling demographic momentum.

The final modeling workflow uses a tuned Lasso regression model as the predictive backbone. The model was selected because it provides strong out-of-sample performance while remaining interpretable in a high-dimensional feature space. The model supports population forecasting, disaster scenario analysis, and policy-response simulations through 2030.

The project is designed as a forecasting and strategic planning framework. It does not claim that disaster or policy scenarios are causal treatment-effect estimates. Instead, the scenarios are model-based counterfactual stress tests that show how projected population outcomes may shift under different assumptions.

---

## Objectives

The main objectives of this project are to:

- Forecast short- and medium-term population change using a reproducible modeling workflow.
- Quantify the relative influence of demographic momentum, fertility, age structure, economic conditions, social vulnerability, public safety, business activity, and disaster exposure.
- Identify patterns of vulnerability, resilience, and recovery capacity across Puerto Rico.
- Evaluate baseline, disaster, and policy-response scenarios through 2030.
- Translate model outputs into interpretable metrics, figures, maps, and dashboard visualizations for planners, policymakers, and public-sector stakeholders.
- Distinguish between structural demographic decline and shock-driven or policy-sensitive population change.

---

## Repository Structure

```text
CAPSTONE_DATA_SCIENCE_RIVERARUIZ/
│
├── model_population_analysis/
│   ├── Phase1_Data_Integration_and_Feature_Engineering.ipynb
│   ├── Phase2_Modeling_Interpretability_and_Temporal_Dynamics.ipynb
│   ├── Phase3_Forecasting_Scenario_Simulation_and_Model_Validation.ipynb
│   └── Phase4_Policy_Response_and_Population_Retention_Strategies.ipynb
│
├── data/
│   ├── Python scripts for collecting, cleaning, and formatting raw data
│   └── Prepared data outputs used by the modeling notebooks
│
├── project_reports/
│   └── Final report and related written deliverables
│
├── dashboards/
│   └── Dashboard assets and visual outputs
│
├── metrics/
│   └── Metrics and analysis outputs used by the website
│
├── tools/
│   └── Supporting scripts and utilities
│
├── index.html
├── dashboard.html
├── dashboards.html
├── metrics.html
├── literature.html
├── about.html
├── strategy.html
├── README.md
└── requirements.txt
```

---

## Main Workflow

The project follows a structured modeling workflow:

1. **Data Integration and Feature Engineering**  
   Local-level demographic, economic, vulnerability, public safety, business activity, vital-rate, and disaster exposure data are collected and transformed into a modeling-ready panel.

2. **Predictive Modeling and Interpretability**  
   A chronological train-validation-test design is used to preserve temporal ordering and avoid leakage. Several models are evaluated, and a tuned Lasso regression model is selected as the final forecasting backbone. Interpretability tools are used to understand which feature groups contribute most to predictions.

3. **Forecasting, Scenario Simulation, and Model Validation**  
   The validated model is extended into baseline and disaster scenario forecasts through 2030. Hurricane and earthquake scenarios are used to test how shocks may amplify existing population trends.

4. **Policy Response and Population Retention Strategies**  
   Policy simulations modify policy-relevant input features such as income growth, establishment growth, public-safety conditions, vulnerability, demographic support, and population momentum. These counterfactual scenarios estimate how projected outcomes may shift under different recovery and retention strategies.

---

## Data Requirements

All data used by the notebooks is stored in the `data/` folder.

The `data/` folder includes Python scripts that automatically pull data from the relevant resources, clean it, and format it so the modeling notebooks can use it directly. These scripts are responsible for preparing the data structure required by the population forecasting workflow.

All data are harmonized into standardized, reproducible formats for use in the modeling notebooks and dashboard outputs.

Key data sources include:

- U.S. Census Population Estimates Program data
- Puerto Rico vital statistics and Census-derived fertility measures
- American Community Survey labor market and socioeconomic indicators
- County Business Patterns data for employment, establishments, and payroll
- Social vulnerability and housing-related indicators
- Public safety and crime-related indicators
- NOAA hurricane track data
- USGS earthquake catalogs
- Regional and islandwide aggregation outputs

The project uses data related to:

- Population counts and population-change measures
- Birth, death, and natural-change indicators
- Income, employment, payroll, and establishment activity
- Social vulnerability indicators
- Public safety and crime-related indicators
- Hurricane and earthquake exposure measures
- Regional and islandwide population summaries

Before running the notebooks, make sure the data preparation scripts have been executed and that the processed datasets are available in the expected locations inside the `data/` directory.

Because some raw datasets may come from external public sources, availability and file formats may change over time. If a data pull fails, check the source URL, file naming convention, and any local paths referenced in the data scripts.

---

## Analytical Approach

The project combines supervised learning, interpretability, scenario analysis, and policy stress testing.

### 1. Population Forecasting

The predictive modeling component estimates future population change using demographic, economic, social, and hazard-related features. The project evaluates multiple model types, including linear regression, Ridge, Lasso, Random Forest, Extra Trees, and gradient-boosting approaches. The final selected model is a tuned Lasso regression because it combines strong temporal generalization with interpretability.

The target focuses on forward-looking population change, allowing the model to capture short- and medium-term demographic movement rather than only one-year noise.

### 2. Feature Importance and Explainability

The project uses coefficient analysis, feature-importance diagnostics, and SHAP-based interpretability to understand which factors most strongly influence the model's predictions. This helps compare the roles of lagged population dynamics, fertility and natural-change context, economic conditions, vulnerability, and disaster exposure.

### 3. Pattern Identification and Regional Interpretation

The workflow uses local-level data to identify shared demographic and economic patterns across Puerto Rico. While the modeling begins from detailed local data, the project emphasizes regional and islandwide population trajectories because these scales are most useful for scenario forecasting, policy interpretation, and long-term planning.

### 4. Scenario Analysis and Risk Testing

The scenario component evaluates baseline forecasts, hurricane intensity scenarios, earthquake magnitude scenarios, and Maria-like stress tests. The goal is to understand how disasters may amplify existing decline patterns rather than treating them as simple one-period drivers.

### 5. Policy Simulation and Recovery-Rebound Testing

The policy component tests counterfactual recovery strategies by modifying policy-relevant feature groups. These include economic opportunity, public safety, vulnerability reduction, demographic support, business activity, and population momentum. Recovery-rebound scenarios add an optimistic return-migration or recovery-momentum layer to estimate what may be required to stabilize or temporarily increase population.

---

## Evaluation Metrics

The project evaluates model performance and scenario reliability using:

- Root Mean Squared Error (RMSE)
- R-squared on validation and held-out test periods
- Chronological train-validation-test performance
- Temporal generalization across later years
- Scenario sensitivity testing
- Interpretability and feature-stability diagnostics
- Qualitative validation against known disaster, migration, and demographic events

The final tuned Lasso model achieves strong held-out test performance, with test R-squared of approximately `0.9092` and RMSE of approximately `0.4531`.

---

## Model Folder

The core analysis is in:

```text
model_population_analysis/
```

This folder contains the four main Jupyter notebooks used to build the forecasting and policy analysis workflow:

```text
Phase1_Data_Integration_and_Feature_Engineering.ipynb
Phase2_Modeling_Interpretability_and_Temporal_Dynamics.ipynb
Phase3_Forecasting_Scenario_Simulation_and_Model_Validation.ipynb
Phase4_Policy_Response_and_Population_Retention_Strategies.ipynb
```

Although the notebooks are separated for organization and coding purposes, together they represent one integrated modeling workflow.

---

## How to Run It

### 1. Clone the repository

```bash
git clone https://github.com/venettov/CAPSTONE_DATA_SCIENCE_RIVERARUIZ.git
cd CAPSTONE_DATA_SCIENCE_RIVERARUIZ
```

### 2. Create and activate a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare the data

Run the Python scripts inside the `data/` folder to pull, clean, and format the required datasets.

Example:

```bash
cd data
python your_data_script_name.py
cd ..
```

Replace `your_data_script_name.py` with the actual data preparation script you want to run. If the data folder contains multiple scripts, run them in the order required by the project workflow.

### 5. Run the modeling notebooks

Open Jupyter Notebook or JupyterLab:

```bash
jupyter lab
```

Then open the notebooks inside `model_population_analysis/` and run them in order:

```text
1. Phase1_Data_Integration_and_Feature_Engineering.ipynb
2. Phase2_Modeling_Interpretability_and_Temporal_Dynamics.ipynb
3. Phase3_Forecasting_Scenario_Simulation_and_Model_Validation.ipynb
4. Phase4_Policy_Response_and_Population_Retention_Strategies.ipynb
```

Running the notebooks in order is recommended because later notebooks depend on processed datasets, model artifacts, and outputs generated earlier in the workflow.

---

## Outputs

The workflow produces:

- Cleaned and integrated modeling datasets
- Trained model artifacts
- Model performance metrics
- Feature-importance and interpretability outputs
- Baseline population forecasts
- Hurricane and earthquake scenario forecasts
- Regional and islandwide population summaries
- Policy-response and recovery-rebound simulation outputs
- Figures and tables used in the final report and dashboard

---

## Dashboard and Website

The dashboard and website files are included in the root folder and supporting dashboard folders. They visualize the data, modeling outputs, and population analysis results.

Main website:

```text
index.html
```

Live version:

https://venettov.github.io/CAPSTONE_DATA_SCIENCE_RIVERARUIZ/index.html

The website includes pages for dashboards, metrics, project background, literature, and strategy outputs.

---

## Key Findings

The analysis found that Puerto Rico's population change is not random. It is shaped by long-term demographic momentum, economic and social conditions, spatial differences across regions, and recovery capacity.

Major findings include:

- Lagged and rolling population dynamics are among the strongest predictors of future population change.
- Natural vital-rate conditions provide important context for understanding long-term decline.
- Economic conditions and business activity influence resilience, but they do not fully override demographic momentum.
- Disaster shocks amplify existing population trajectories rather than acting as simple one-period drivers.
- Regional impacts are uneven, meaning population risk and recovery capacity differ across the island.
- Policy bundles can slow projected decline, but reversal requires stronger recovery momentum.
- Recovery-rebound scenarios suggest that stabilization or growth likely requires coordinated structural improvements and return migration.

---

## Expected Outcomes and Capstone Alignment

This project is designed to produce:

- A reproducible end-to-end data science pipeline
- A quantitative distinction between structural demographic decline and migration- or shock-driven change
- Interpretable population forecasting outputs
- Scenario-based planning tools for disaster and policy analysis
- Regional and islandwide insights for resilience planning
- Dashboard-ready metrics and visualizations for public-facing communication

The project aligns with Rutgers M.S. in Data Science capstone goals by:

- Leveraging complex real-world public datasets
- Applying supervised and unsupervised machine learning concepts
- Emphasizing interpretability and responsible data use
- Producing outputs relevant to public-sector decision-making
- Connecting technical modeling results to applied policy and planning questions

---

## Notes on Interpretation

The project should be interpreted as a predictive and scenario-testing framework, not as a causal policy evaluation.

The disaster and policy simulations are counterfactual stress tests. They show how the fitted forecasting model responds when selected conditions are changed, but they do not prove that real-world interventions would produce the exact modeled shifts.

By incorporating fertility dynamics, natural-change context, and demographic momentum into predictive modeling, this capstone advances beyond migration-only explanations. The framework provides a forward-looking, policy-relevant understanding of Puerto Rico's population trajectories and demonstrates the applied value of data science in complex demographic systems.

---

## Requirements

The required Python packages are listed in:

```text
requirements.txt
```

Install them with:

```bash
pip install -r requirements.txt
```

Common package groups used by this project include:

- Data processing: `pandas`, `numpy`, `openpyxl`
- Modeling: `scikit-learn`, `joblib`
- Visualization: `matplotlib`, `seaborn`
- Interpretability: `shap`
- Geospatial analysis and mapping: `geopandas`, `shapely`
- Notebook execution: `jupyter`, `ipykernel`

---

## Author

**Jose Andres RiveraRuiz**  
Rutgers, The State University of New Jersey  
M.S. in Data Science  
Capstone Data Science Project  
Spring 2026

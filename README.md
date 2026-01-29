# DATA_SCIENCE_MASTERS_PROJECT_RIVERARUIZ
Predictive Modeling of Population Decline, Economic Resilience, and Demographic Momentum in Puerto Rico

Capstone Project – Spring 2026
Course: 56:219:603:91 – Master’s Project
Program: M.S. in Data Science
Institution: Rutgers University
Student: Andres Ruiz

------------------------------------------------------------
PROJECT OVERVIEW
------------------------------------------------------------
Puerto Rico is experiencing sustained population decline driven by a complex interaction of migration, economic stress, low fertility, population aging, and exposure to natural hazards. While descriptive dashboards help visualize these trends, decision-makers increasingly need predictive, interpretable, and policy-relevant analytics.

This capstone develops a municipal-level predictive modeling framework that integrates demographic, economic, fertility, and hazard data to forecast population change, identify vulnerable municipalities, and support long-term resilience planning. A core contribution of the project is the explicit modeling of demographic momentum—the structural effects of low birth rates and aging that continue to drive population decline even in the absence of migration shocks.

------------------------------------------------------------
OBJECTIVES
------------------------------------------------------------
• Forecast short- and medium-term population change at the municipal level  
• Quantify the relative influence of fertility, age structure, economic conditions, and hazard exposure  
• Identify clusters of municipalities with shared demographic and economic trajectories  
• Translate model outputs into interpretable metrics and visualizations for planners and policymakers  

------------------------------------------------------------
DATA SOURCES
------------------------------------------------------------
All data are harmonized at the Puerto Rico municipal level and stored in standardized, reproducible formats.

Key sources include:
• U.S. Census Population Estimates Program (2010–2024)
• Puerto Rico vital statistics and Census-derived fertility measures
• American Community Survey labor market indicators
• County Business Patterns (employment, establishments, payroll)
• ACS socioeconomic indicators (income, poverty, housing, education)
• NOAA hurricane track data
• USGS earthquake catalogs

------------------------------------------------------------
ANALYTICAL APPROACH
------------------------------------------------------------
1. Population Forecasting (Supervised Learning)
   - Target: Percent population change over 3–5 year horizons
   - Features: fertility, age structure, economic trends, hazard exposure
   - Models: Linear regression, Ridge, Lasso, Random Forest, Gradient Boosting

2. Feature Importance and Explainability
   - Permutation importance and interpretable diagnostics
   - Comparison of fertility, aging, economic, and hazard effects

3. Municipal Typologies (Unsupervised Learning)
   - K-means and hierarchical clustering
   - Identification of shared demographic and economic profiles

4. Scenario Analysis and Risk Scoring
   - Municipal Demographic Vulnerability Score
   - Scenario-based comparisons for planning support

------------------------------------------------------------
EVALUATION METRICS
------------------------------------------------------------
• Mean Absolute Error (MAE)
• Root Mean Squared Error (RMSE)
• Cross-validation stability
• Sensitivity testing of clustering solutions
• Qualitative validation against known disaster and migration events

------------------------------------------------------------
EXPECTED OUTCOMES
------------------------------------------------------------
• Reproducible end-to-end data science pipeline
• Quantitative distinction between structural demographic decline and migration-driven change
• Actionable municipal-level insights for planning and resilience strategies
• Interpretable outputs suitable for public-sector stakeholders

------------------------------------------------------------
CAPSTONE ALIGNMENT
------------------------------------------------------------
This project aligns with Rutgers MS in Data Science capstone goals by:
• Leveraging complex real-world public datasets
• Applying supervised and unsupervised machine learning methods
• Emphasizing interpretability and responsible data use
• Producing outputs relevant to public-sector decision-making

------------------------------------------------------------
CONCLUSION
------------------------------------------------------------
By incorporating fertility dynamics and demographic momentum into predictive modeling, this capstone advances beyond migration-only analyses. The framework provides a forward-looking, policy-relevant understanding of Puerto Rico’s municipal population trajectories and demonstrates the applied value of data science in complex demographic systems.

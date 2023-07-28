import streamlit as st
import pandas as pd
from pandas_profiling import ProfileReport
from scipy.stats import chi2_contingency

# Function to generate the Descriptive Statistics report
def generate_descriptive_statistics(data):
    profile = ProfileReport(data, title='Descriptive Statistics of the Data', explorative=True)
    return profile.to_html()

# Function to calculate odds ratio and perform chi-square test
def calculate_odds_ratio_and_chi2(data, food_type):
    contingency_table = pd.crosstab(data['case_or_control'], data[food_type].map({'eat': 'eat', 'not eat': 'not eat'}))

    if 'Control' in contingency_table.index and 'Case' in contingency_table.index:
        # Calculate chi-square statistic, p-value, and degrees of freedom
        chi2_stat, p_value, dof, expected = chi2_contingency(contingency_table)

        # Calculate odds ratio
        odds_ratio = (contingency_table.loc['Control', 'eat'] * contingency_table.loc['Case', 'not eat']) / (contingency_table.loc['Control', 'not eat'] * contingency_table.loc['Case', 'eat'])

    else:
        odds_ratio = chi2_stat = p_value = None

    return odds_ratio, chi2_stat, p_value, contingency_table

# Function to generate a report displaying chi-square results and odds ratios for each food type
def generate_chi_square_report(data):
    food_types = ['foodA', 'foodB', 'foodC', 'foodD', 'foodE']
    results = []

    for food in food_types:
        odds_ratio, chi2_stat, p_value, contingency_table = calculate_odds_ratio_and_chi2(data, food)
        results.append({
            'Food Type': food,
            'Odds Ratio': odds_ratio,
            'Chi-square': chi2_stat,
            'P-value': p_value,
            'Contingency Table': contingency_table
        })

    report_df = pd.DataFrame(results)
    return report_df

def main():
    st.title("Epidemiology Data Analysis App")

    # Upload CSV file
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

    if uploaded_file is not None:
        # Read the CSV file into a DataFrame
        data = pd.read_csv(uploaded_file)

        # Display the raw data
        st.subheader("Raw Data")
        st.write(data)

        # Generate and display the Descriptive Statistics report
        if st.sidebar.checkbox("Show Descriptive Statistics"):
            st.subheader("Descriptive Statistics of the Data")
            profile_html = generate_descriptive_statistics(data)
            st.components.v1.html(profile_html, height=600, scrolling=True)

        # Show menu to select a specific food type for analysis
        st.subheader("Food Type Analysis")
        food_types = ['foodA', 'foodB', 'foodC', 'foodD', 'foodE']
        selected_food = st.selectbox("Select a food type", food_types)

        # Calculate odds ratio and perform chi-square test for the selected food type
        odds_ratio, chi2_stat, p_value, contingency_table = calculate_odds_ratio_and_chi2(data, selected_food)

        # Generate and display the contingency table for the selected food type
        if st.sidebar.checkbox("Show Contingency Table"):
            st.subheader(f"Contingency Table for Food Type '{selected_food}'")
            contingency_table = contingency_table[['eat', 'not eat']].T
            contingency_table.index = ['Eat', 'Not Eat']
            contingency_table.columns = ['Case', 'Control']
            st.dataframe(contingency_table)

            st.write("Chi-square statistic:", chi2_stat)
            st.write("P-value:", p_value)
            st.write("Odds Ratio:", odds_ratio)

        # Generate and display the simple report with chi-square results and odds ratios
        if st.sidebar.checkbox("Show Overall Result"):
            report_df = generate_chi_square_report(data)
            st.subheader("Chi-square Results and Odds Ratios")
            st.dataframe(report_df)

if __name__ == "__main__":
    main()

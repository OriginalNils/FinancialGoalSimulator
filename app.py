import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def run_monte_carlo_simulation(initial_capital, monthly_contribution, years, 
                               expected_return, volatility, num_simulations):
    """
    Performs a Monte Carlo simulation for an investment portfolio.
    """
    # Convert annual payments into monthly instalments
    monthly_return = expected_return / 12
    monthly_volatility = volatility / np.sqrt(12)
    num_months = years * 12
    
    # An array for storing all simulation paths
    all_simulation_paths = np.zeros((num_months + 1, num_simulations))
    all_simulation_paths[0] = initial_capital

    for i in range(num_simulations):
        capital = initial_capital
        for month in range(num_months):
            # Draw random monthly returns from a normal distribution
            random_return = np.random.normal(monthly_return, monthly_volatility)
            
            # Capital growth through returns
            capital *= (1 + random_return)
            
            # Add monthly savings rate
            capital += monthly_contribution
            
            all_simulation_paths[month + 1, i] = capital

    return all_simulation_paths


# --- Streamlit App ---
st.set_page_config(page_title="Financial Goal Simulator", layout="wide")
st.title("Monte-Carlo-Simulator for your financial goals")

# --- Sidebar---
st.sidebar.header("Parameters")

initial_capital = st.sidebar.number_input("Seed capital (€)", min_value=0, value=10000, step=1000)
monthly_contribution = st.sidebar.number_input("Monthly savings rate (€)", min_value=0, value=500, step=50)
years = st.sidebar.slider("Investment horizon (years)", min_value=1, max_value=50, value=30, step=1)

st.sidebar.markdown("---")

expected_return = st.sidebar.slider("Expected annual return (%)", min_value=0.0, max_value=20.0, value=7.0, step=0.5) / 100
volatility = st.sidebar.slider("Expected annual volatility (%)", min_value=0.0, max_value=40.0, value=15.0, step=0.5) / 100

# NEW: Add inflation checkbox
st.sidebar.markdown("---")
adjust_for_inflation = st.sidebar.checkbox("Adjust for inflation (2% p.a.)")

st.sidebar.markdown("---")
num_simulations = st.sidebar.select_slider("Number of simulations", options=[100, 500, 1000, 5000], value=1000)

if st.sidebar.button("Start simulation"):
    
    with st.spinner("Simulations are running... This may take a moment."):
        simulation_results = run_monte_carlo_simulation(
            initial_capital, monthly_contribution, years, 
            expected_return, volatility, num_simulations
        )
        
        # --- NEW: Adjust results for inflation if checkbox is ticked ---
        title_suffix = ""
        y_axis_label = "Portfolio value (€)"
        if adjust_for_inflation:
            inflation_rate = 0.02
            # Create a discount factor for each month
            months = np.arange(years * 12 + 1)
            discount_factors = (1 + inflation_rate / 12) ** months
            # Divide the simulation results by the discount factors
            simulation_results = simulation_results / discount_factors[:, np.newaxis]
            
            title_suffix = " (inflation-adjusted, in today's money)"
            y_axis_label = "Portfolio value (€, in today's money)"

        final_values = simulation_results[-1]
        
        st.header(f"Simulation results{title_suffix}")

        # --- NEW: Calculate and display total invested capital ---
        total_invested = initial_capital + (monthly_contribution * years * 12)
        
        # Metriken
        median_final = np.median(final_values)
        worst_case = np.percentile(final_values, 10)
        best_case = np.percentile(final_values, 90)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Most probable final value (median)", f"€ {median_final:,.0f}")
        col2.metric("Worst-case scenario (10%)", f"€ {worst_case:,.0f}")
        col3.metric("Better scenario (90%)", f"€ {best_case:,.0f}")
        col4.metric("Total Invested", f"€ {total_invested:,.0f}")
        
        # 1. All simulation paths (‘funnel’ chart)
        fig_paths = go.Figure()
        # Create an array of years for the x-axis
        x_axis_years = np.arange(0, years + 1, 1)
        
        # Plot each simulation path (showing only the value at the end of each year)
        for i in range(num_simulations):
            fig_paths.add_trace(go.Scatter(
                x=x_axis_years, 
                y=simulation_results[::12, i],
                mode='lines', 
                line=dict(width=0.5, color='lightblue'),
                showlegend=False
            ))
            
        fig_paths.update_layout(title=f"Possible portfolio developments{title_suffix}",
                              xaxis_title="Years", yaxis_title=y_axis_label)
        st.plotly_chart(fig_paths, use_container_width=True)
        
        # 2. Histogram of final values
        fig_hist = go.Figure(data=[go.Histogram(x=final_values, nbinsx=100, name="Frequency")])
        fig_hist.update_layout(title=f"Distribution of possible final values{title_suffix}",
                               xaxis_title=f"Final value{title_suffix}", yaxis_title="Number of simulations")
        st.plotly_chart(fig_hist, use_container_width=True)
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def run_monte_carlo_simulation(initial_capital, monthly_contribution, years, 
                               expected_return, volatility, num_simulations, annual_fee, contribution_increase_rate):
    """
    Performs a Monte Carlo simulation for an investment portfolio.
    """
    monthly_return = expected_return / 12
    monthly_volatility = volatility / np.sqrt(12)
    num_months = years * 12
    
    all_simulation_paths = np.zeros((num_months + 1, num_simulations))
    all_simulation_paths[0] = initial_capital

    invested_capital_path = np.zeros(num_months + 1)
    invested_capital_path[0] = initial_capital

    for i in range(num_simulations):
        capital = initial_capital
        current_monthly_contribution = monthly_contribution
        total_invested = initial_capital

        for month in range(num_months):
            random_return = np.random.normal(monthly_return, monthly_volatility)
            capital *= (1 + random_return)
            
            capital += current_monthly_contribution
            if i == 0:
                total_invested += current_monthly_contribution
                invested_capital_path[month + 1] = total_invested
            
            if (month + 1) % 12 == 0:
                capital *= (1 - annual_fee)
                current_monthly_contribution *= (1 + contribution_increase_rate)

            all_simulation_paths[month + 1, i] = capital

    return all_simulation_paths, invested_capital_path


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
contribution_increase_rate = st.sidebar.slider("Annual contribution increase (%)", min_value = 0.0, max_value=10.0, step=0.25)/100

st.sidebar.markdown("---")
inflation_rate = st.sidebar.slider("Average inflation (%)", min_value = 0.0, max_value = 7.5, step=0.1, value=2.0)/100
annual_fee = st.sidebar.number_input("Annual fees (%)", min_value = 0.0, max_value = 5.0, step = 0.01, value=5.0)/100

st.sidebar.markdown("---")
num_simulations = st.sidebar.select_slider("Number of simulations", options=[100, 500, 1000, 5000], value=1000)

if st.sidebar.button("Start simulation"):
    
    with st.spinner("Simulations are running... This may take a moment."):
        simulation_results, invested_capital_path = run_monte_carlo_simulation(
            initial_capital, monthly_contribution, years, 
            expected_return, volatility, num_simulations, annual_fee, contribution_increase_rate
        )
        
        title_suffix = ""
        y_axis_label = "Portfolio value (€)"

        if inflation_rate > 0:
            months = np.arange(years * 12 + 1)
            discount_factors = (1 + inflation_rate / 12) ** months
            simulation_results = simulation_results / discount_factors[:, np.newaxis]
            invested_capital_path = invested_capital_path / discount_factors
            title_suffix = " (inflation-adjusted, in today's money)"
            y_axis_label = "Portfolio value (€, in today's money)"

        final_values = simulation_results[-1]
        
        st.header(f"Simulation results{title_suffix}")
        
        total_invested = invested_capital_path[-1]
        
        median_final = np.median(final_values)
        worst_case = np.percentile(final_values, 10)
        best_case = np.percentile(final_values, 90)

        # --- HINZUGEFÜGT: Berechnung der letzten Rate ---
        # Berechnet die Rate für das letzte Jahr der Einzahlung
        last_rate = monthly_contribution * ((1 + contribution_increase_rate) ** (years - 1))

        # --- HINZUGEFÜGT: Fünf Spalten für die Metriken ---
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Most probable final value (median)", f"€ {median_final:,.0f}")
        col2.metric("Worst-case scenario (10%)", f"€ {worst_case:,.0f}")
        col3.metric("Better scenario (90%)", f"€ {best_case:,.0f}")
        col4.metric("Total Invested", f"€ {total_invested:,.0f}")
        # --- HINZUGEFÜGT: Anzeige der letzten Rate ---
        col5.metric("Last monthly rate", f"€ {last_rate:,.0f}")
        
        # --- Chart 1: Simulation Paths ---
        fig_paths = go.Figure()
        x_axis_years = np.arange(0, years + 1, 1)
        
        for i in range(num_simulations):
            fig_paths.add_trace(go.Scatter(
                x=x_axis_years, 
                y=simulation_results[::12, i],
                mode='lines', 
                line=dict(width=0.5, color='lightblue'),
                showlegend=False
            ))
            
        fig_paths.add_trace(go.Scatter(
            x=x_axis_years,
            y=invested_capital_path[::12],
            mode='lines',
            line=dict(width=2, color='black', dash='dash'),
            name='Total Invested'
        ))
            
        fig_paths.update_layout(title=f"Possible portfolio developments{title_suffix}",
                              xaxis_title="Years", yaxis_title=y_axis_label)
        st.plotly_chart(fig_paths, use_container_width=True)
        
        # --- Chart 2: Histogram ---
        fig_hist = go.Figure(data=[go.Histogram(x=final_values, nbinsx=100, name="Frequency")])
        fig_hist.update_layout(title=f"Distribution of possible final values{title_suffix}",
                               xaxis_title=f"Final value{title_suffix}", yaxis_title="Number of simulations")
        st.plotly_chart(fig_hist, use_container_width=True)
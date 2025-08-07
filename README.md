# 💰 Monte Carlo Financial Goal Simulator

An interactive web application built with Python and Streamlit to simulate the long-term development of an investment portfolio using the Monte Carlo method. This tool helps visualize a wide range of potential future outcomes for financial goals, accounting for variables like inflation, fees, and dynamic contributions.



## ✨ Key Features

- **Interactive Simulation:** All parameters can be adjusted in real-time via a simple sidebar.

- **Customizable Parameters:**

    - Initial Capital & Monthly Contribution

    - Investment Horizon (in years)

    - Expected Annual Return & Volatility

- **Realistic Scenarios:**

    - **Dynamic Contributions:** Option to automatically increase the monthly contribution rate annually.

    - **Inflation Adjustment:** A slider to set the expected inflation rate and view all results in today's purchasing power.

    - **Fees:** Ability to factor in annual management fees (e.g., ETF TER).

- **Comprehensive Visualization:**

    - A "funnel" chart showing thousands of possible portfolio paths over time.

    - An interactive histogram of the distribution of final portfolio values.

    - A clear comparison line for the total capital invested.

- **Key Metrics:** Get an instant overview of the most likely outcome (median), along with worst-case (10th percentile) and best-case (90th percentile) scenarios.




## 🚀 Installation

To run this application locally, please follow these steps.

#### 1. Clone the repository:

```bash
git clone https://github.com/OriginalNils/FinancialGoalSimulator.git
cd FinancialGoalSimulator
```

#### 2. Install dependencies:
Then, run the installation command:
```bash
pip install -r requirements.txt
```

## ▶️ Running the App

Once the setup is complete, launch the Streamlit application from your terminal:

```bash
streamlit run app.py
```

Your web browser will automatically open with the running application.


## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.


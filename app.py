# KENYA DEBT GUARDIAN - ULTIMATE EDITION (EXTENDED)
# Features: Revenue vs Expenditure Analysis + Economic Health Prediction

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from prophet import Prophet
import os
from datetime import datetime

st.set_page_config(page_title="Kenya Debt Guardian", layout="wide", page_icon="🇰🇪")

# --- CSS STYLING ---
st.markdown("""
<style>
    .main-header {
        font-size: 3.5rem !important;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #006600, #B00020);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        padding: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        text-align: center;
        height: 100%;
        color: white !important;
    }
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        text-align: center;
        height: 100%;
        color: white !important;
    }
    .section-header {
        font-size: 2rem;
        font-weight: 800;
        color: #2C3E50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #006600;
        background: linear-gradient(90deg, #006600, #B00020);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .recommendation-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #006600;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        color: #333333;
    }
    .graph-explanation {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #006600;
        margin-top: 1rem;
        font-size: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        color: #000000 !important;
    }
    .highlight {
        background: linear-gradient(120deg, #ffe6e6, #ffcccc);
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-weight: 700;
        color: #B00020 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>KENYA DEBT GUARDIAN</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Comprehensive Analysis of Kenya's National Debt Situation</p>", unsafe_allow_html=True)
st.markdown("---")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('kenya_master_data.csv')
        # Unit correction: Source is in Millions, convert to Ones for consistent calculation
        df['Amount_KSh'] = df['Amount'] * 1_000_000 
        df['Time'] = pd.to_datetime(df['Time'])
        df['Year'] = df['Time'].dt.year
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

full_df = load_data()
st.success(f"✅ Successfully loaded {len(full_df):,} records from official sources")

# --- PREPARE METRICS DATA ---

# 1. Total Debt
debt_series = full_df[full_df['Indicator'] == 'Total Debt'].sort_values('Time').copy()
# Fallback if Total Debt is missing: Sum Domestic + External
if debt_series.empty:
    temp_dom = full_df[full_df['Indicator'] == 'Domestic Debt'].groupby('Time')['Amount_KSh'].sum()
    temp_ext = full_df[full_df['Indicator'] == 'External Debt'].groupby('Time')['Amount_KSh'].sum()
    debt_series = pd.DataFrame({'Amount_KSh': temp_dom + temp_ext}).reset_index()
    debt_series['Year'] = debt_series['Time'].dt.year

# Latest Values
if not debt_series.empty:
    latest_record = debt_series.iloc[-1]
    latest_debt_tn = latest_record['Amount_KSh'] / 1e12
    latest_year_val = latest_record['Year']
    
    # Growth Calculation
    yearly_totals = debt_series.groupby('Year')['Amount_KSh'].mean().reset_index().sort_values('Year')
    growth_rates = yearly_totals['Amount_KSh'].pct_change() * 100
    avg_growth_rate = growth_rates.mean()
    
    # Per Capita (55M pop)
    debt_per_citizen = (latest_debt_tn * 1e12) / 55e6
else:
    latest_debt_tn = 0
    latest_year_val = 2024
    avg_growth_rate = 0
    debt_per_citizen = 0

# --- METRICS DASHBOARD ---
st.markdown("<div class='section-header'>📊 Key Debt Indicators Dashboard</div>", unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <h3 style='color: white; margin-bottom: 1rem;'>🏛️ Current Debt Stock</h3>
        <h2 style='color: white; font-size: 2.2rem; margin: 0.5rem 0;'>{latest_debt_tn:.2f} Trillion KSh</h2>
        <p style='color: rgba(255,255,255,0.9); font-size: 0.9rem;'>Accumulated sovereign debt burden</p>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <h3 style='color: white; margin-bottom: 1rem;'>📅 Latest Year</h3>
        <h2 style='color: white; font-size: 2.2rem; margin: 0.5rem 0;'>{latest_year_val}</h2>
        <p style='color: rgba(255,255,255,0.9); font-size: 0.9rem;'>Most recent data point</p>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <h3 style='color: white; margin-bottom: 1rem;'>📈 Annual Growth Rate</h3>
        <h2 style='color: white; font-size: 2.2rem; margin: 0.5rem 0;'>{avg_growth_rate:.1f}%</h2>
        <p style='color: rgba(255,255,255,0.9); font-size: 0.9rem;'>Average YoY increase</p>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <h3 style='color: white; margin-bottom: 1rem;'>👥 Debt Per Citizen</h3>
        <h2 style='color: white; font-size: 2.2rem; margin: 0.5rem 0;'>{debt_per_citizen:,.0f} KSh</h2>
        <p style='color: rgba(255,255,255,0.9); font-size: 0.9rem;'>Per person burden</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# --- HISTORICAL TREND ---
st.markdown("<div class='section-header'>📈 Historical Debt Trend Analysis</div>", unsafe_allow_html=True)

if not yearly_totals.empty:
    yearly_totals['Amount_Trillion'] = yearly_totals['Amount_KSh'] / 1e12
    yearly_totals['Growth_Rate'] = yearly_totals['Amount_Trillion'].pct_change() * 100

    fig_historical = go.Figure()

    # Bar Chart (Left Y-Axis)
    fig_historical.add_trace(go.Bar(
        x=yearly_totals['Year'],
        y=yearly_totals['Amount_Trillion'],
        name='National Debt',
        marker=dict(color=yearly_totals['Amount_Trillion'], colorscale='RdYlGn_r'),
        hovertemplate='<b>Year: %{x}</b><br>Debt: <b>%{y:.2f}T KSh</b><extra></extra>'
    ))

    # Line Chart (Right Y-Axis)
    fig_historical.add_trace(go.Scatter(
        x=yearly_totals['Year'],
        y=yearly_totals['Growth_Rate'],
        name='Growth Rate (%)',
        yaxis='y2',
        line=dict(color='#006600', width=6, dash='dot'),
        marker=dict(size=10, symbol='diamond', line=dict(width=2, color='white')),
        hovertemplate='<b>Year: %{x}</b><br>Growth: <b>%{y:.1f}%</b><extra></extra>'
    ))

    fig_historical.update_layout(
        title=dict(text="<b>Kenya National Debt Evolution (2000-2025)</b>", x=0.5, xanchor='center', font=dict(size=22)),
        xaxis=dict(title="<b>Year</b>", gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        yaxis=dict(title="<b>Debt Stock (Trillions KSh)</b>", gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        yaxis2=dict(title="<b>Annual Growth Rate (%)</b>", overlaying='y', side='right', showgrid=False),
        height=600,
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
        template="plotly_white",
        plot_bgcolor='rgba(240, 244, 249, 1)'
    )

    st.plotly_chart(fig_historical, use_container_width=True)

    st.markdown("""
    <div class='graph-explanation'>
        <strong>🔍 Understanding the Trend:</strong>
        This chart tracks Kenya's total debt accumulation over time alongside its annual growth rate.
        <ul>
            <li><strong>Bars (Left Axis):</strong> The colored bars represent the total amount of debt in Trillions of Kenyan Shillings for each year. A rising bar means the total debt stock is increasing.</li>
            <li><strong>Dotted Line (Right Axis):</strong> The green dotted line shows the percentage growth of debt from one year to the next. High peaks indicate periods of rapid borrowing.</li>
        </ul>
        <strong>Key Takeaway:</strong> Observing both the total amount and the rate of growth helps identify periods of aggressive borrowing versus stabilization.
    </div>
    """, unsafe_allow_html=True)

# --- DEBT COMPOSITION ---
st.markdown("<div class='section-header'>🔄 Debt Composition Analysis</div>", unsafe_allow_html=True)

try:
    dom_series = full_df[full_df['Indicator'] == 'Domestic Debt'].sort_values('Time')
    if not dom_series.empty:
        latest_dom_rec = dom_series.iloc[-1]
        latest_dom_val = latest_dom_rec['Amount_KSh']
        latest_dom_year = latest_dom_rec['Year']
    else:
        latest_dom_val = 0
        latest_dom_year = 0

    ext_series = full_df[full_df['Indicator'] == 'External Debt'].sort_values('Time')
    if not ext_series.empty:
        latest_ext_rec = ext_series.iloc[-1]
        latest_ext_val = latest_ext_rec['Amount_KSh']
        latest_ext_year = latest_ext_rec['Year']
    else:
        latest_ext_val = 0
        latest_ext_year = 0

    if latest_dom_val > 0 or latest_ext_val > 0:
        comp_year = max(latest_dom_year, latest_ext_year)
        comp_year_str = str(comp_year)
        
        comp_values = [latest_dom_val, latest_ext_val]
        comp_labels = ['Domestic Debt', 'External Debt']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig_pie = px.pie(
                values=comp_values,
                names=comp_labels,
                color=comp_labels,
                color_discrete_map={'Domestic Debt':'#006600', 'External Debt':'#B00020'},
                title=f"<b>Debt Split (As of {comp_year_str})</b>"
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label+value', texttemplate='%{label}<br>%{percent:.1%}<br>(%{value:.2s} KSh)')
            fig_pie.update_layout(
                title_x=0.5, 
                height=500,
                xaxis_title="<b>Category</b>",
                yaxis_title="<b>Share</b>"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col2:
             st.write("") 
            
    else:
        st.warning("Insufficient data for composition analysis.")
        
    st.markdown("""
    <div class='graph-explanation'>
        <strong>🔍 Understanding Debt Composition:</strong>
        This chart breaks down the total debt into two main categories:
        <ul>
            <li><strong>Domestic Debt:</strong> Money borrowed from within Kenya (e.g., from local banks and investors). This debt is denominated in Kenyan Shillings.</li>
            <li><strong>External Debt:</strong> Money borrowed from foreign sources (e.g., other countries, international organizations). This debt is often in foreign currencies like USD or Euro.</li>
        </ul>
        <strong>Key Takeaway:</strong> The balance between domestic and external debt is crucial. High external debt exposes the economy to exchange rate risks, while high domestic debt can limit credit available to the private sector.
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error in composition chart: {e}")

# --- AI FORECAST ---
st.markdown("<div class='section-header'>🔮 AI-Powered Debt Forecast</div>", unsafe_allow_html=True)

if not debt_series.empty:
    prophet_df = debt_series[['Time', 'Amount_KSh']].rename(columns={'Time': 'ds', 'Amount_KSh': 'y'})
    
    m = Prophet(changepoint_prior_scale=0.15)
    m.fit(prophet_df)
    future = m.make_future_dataframe(periods=4 * 365)
    forecast = m.predict(future)
    
    prophet_df['y_T'] = prophet_df['y'] / 1e12
    forecast['yhat_T'] = forecast['yhat'] / 1e12
    forecast['yhat_lower_T'] = forecast['yhat_lower'] / 1e12
    forecast['yhat_upper_T'] = forecast['yhat_upper'] / 1e12
    
    fig_forecast = go.Figure()
    
    fig_forecast.add_trace(go.Scatter(
        x=prophet_df['ds'], y=prophet_df['y_T'],
        mode='lines', name='Historical Data',
        line=dict(color='#006600', width=5)
    ))
    
    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_T'],
        mode='lines', name='AI Projection',
        line=dict(color='#B00020', width=5, dash='dash')
    ))
    
    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_upper_T'],
        mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'
    ))
    fig_forecast.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat_lower_T'],
        fill='tonexty', fillcolor='rgba(176, 0, 32, 0.1)',
        mode='lines', line=dict(width=0), name='Confidence Range', hoverinfo='skip'
    ))
    
    fig_forecast.update_layout(
        title=dict(text="<b>Projected Debt Trajectory (2025-2028)</b>", x=0.5, font=dict(size=22)),
        xaxis=dict(title="<b>Year</b>", gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        yaxis=dict(title="<b>Debt Amount (Trillions KSh)</b>", gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        height=600,
        template="plotly_white"
    )
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    st.markdown("""
    <div class='graph-explanation'>
        <strong>🔍 Understanding the Forecast:</strong>
        This chart uses historical data to predict future debt levels using an AI model (Prophet).
        <ul>
            <li><strong>Solid Green Line:</strong> Represents the actual historical debt data.</li>
            <li><strong>Dashed Red Line:</strong> Shows the predicted debt trajectory for the next 4 years.</li>
            <li><strong>Shaded Area:</strong> Indicates the confidence interval, representing the range of possible outcomes. A wider shaded area means higher uncertainty.</li>
        </ul>
        <strong>Key Takeaway:</strong> This forecast helps visualize the potential future burden of debt if current trends continue without intervention.
    </div>
    """, unsafe_allow_html=True)
    
    forecast_end_val = forecast['yhat_T'].iloc[-1]
    increase = forecast_end_val - latest_debt_tn
    
    st.markdown(f"""
    <div class='alert-card'>
        <h3>🚨 PROJECTION ALERT</h3>
        <p>If trends continue, debt could reach <b>{forecast_end_val:.2f} Trillion KSh</b> by 2028.</p>
        <p>An increase of <b>{increase:.2f} Trillion</b> from today.</p>
    </div>
    """, unsafe_allow_html=True)

# --- REVENUE VS EXPENDITURE ANALYSIS (NEW SECTION) ---
st.markdown("<div class='section-header'>⚖️ Fiscal Health: Revenue vs Expenditure & Economic Prediction</div>", unsafe_allow_html=True)

# 1. Prepare Data
# Handle naming conventions (old vs new) if necessary, though 'kenya_master_data.csv' has consistent names generally.
rev_df = full_df[full_df['Indicator'] == 'Revenue'].sort_values('Time').copy()
exp_df = full_df[full_df['Indicator'] == 'Expenditure'].sort_values('Time').copy()

if not rev_df.empty and not exp_df.empty:
    # 2. AI Forecasting for Revenue
    m_rev = Prophet()
    m_rev.fit(rev_df[['Time', 'Amount_KSh']].rename(columns={'Time': 'ds', 'Amount_KSh': 'y'}))
    future_rev = m_rev.make_future_dataframe(periods=5*365)
    forecast_rev = m_rev.predict(future_rev)

    # 3. AI Forecasting for Expenditure
    m_exp = Prophet()
    m_exp.fit(exp_df[['Time', 'Amount_KSh']].rename(columns={'Time': 'ds', 'Amount_KSh': 'y'}))
    future_exp = m_exp.make_future_dataframe(periods=5*365)
    forecast_exp = m_exp.predict(future_exp)

    # 4. Create Combined Graph
    fig_fiscal = go.Figure()

    # Historical
    fig_fiscal.add_trace(go.Scatter(
        x=rev_df['Time'], y=rev_df['Amount_KSh']/1e12,
        name='Revenue Collected (Actual)', line=dict(color='green', width=3)
    ))
    fig_fiscal.add_trace(go.Scatter(
        x=exp_df['Time'], y=exp_df['Amount_KSh']/1e12,
        name='Government Expenditure (Actual)', line=dict(color='red', width=3)
    ))

    # Forecasts
    fig_fiscal.add_trace(go.Scatter(
        x=forecast_rev['ds'], y=forecast_rev['yhat']/1e12,
        name='Revenue (Projected)', line=dict(color='lightgreen', width=3, dash='dash')
    ))
    fig_fiscal.add_trace(go.Scatter(
        x=forecast_exp['ds'], y=forecast_exp['yhat']/1e12,
        name='Expenditure (Projected)', line=dict(color='lightcoral', width=3, dash='dash')
    ))

    fig_fiscal.update_layout(
        title=dict(text="<b>Revenue vs. Expenditure: Historical & Forecast (Trillions KSh)</b>", x=0.5, font=dict(size=22)),
        xaxis=dict(title="<b>Year</b>", gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        yaxis=dict(title="<b>Amount (Trillions KSh)</b>", gridcolor='rgba(0,0,0,0.1)', showgrid=True),
        height=600,
        template="plotly_white",
        legend=dict(orientation="h", y=1.1, x=0.5, xanchor="center"),
    )
    st.plotly_chart(fig_fiscal, use_container_width=True)

    # Calculate Future Deficit
    last_forecast_rev = forecast_rev.iloc[-1]['yhat']
    last_forecast_exp = forecast_exp.iloc[-1]['yhat']
    deficit_2028 = (last_forecast_exp - last_forecast_rev) / 1e12
    status = "Deficit (Loss)" if deficit_2028 > 0 else "Surplus (Gain)"
    status_color = "red" if deficit_2028 > 0 else "green"

    st.markdown("""
    <div class='graph-explanation'>
        <strong>🔍 Understanding the Fiscal Health Graph:</strong>
        This chart compares how much money the government collects (Revenue) vs. how much it spends (Expenditure).
        <ul>
            <li><strong>Green Lines:</strong> Represent Revenue. Solid is past data, dashed is the AI prediction.</li>
            <li><strong>Red Lines:</strong> Represent Expenditure. Solid is past data, dashed is the AI prediction.</li>
            <li><strong>The Gap:</strong> The space between the Red and Green lines represents the <strong>Fiscal Deficit</strong>. If the Red line is above the Green, the government is spending more than it earns, leading to more borrowing.</li>
        </ul>
        <strong>Key Takeaway:</strong> The forecast predicts whether this gap will widen (bad for economy) or narrow (good for economy) in the coming years.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid {status_color}; box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-top: 20px;'>
        <h3 style='color: #2C3E50; margin-top: 0;'>🔮 Economic Health Prediction (2028)</h3>
        <p style='font-size: 1.2rem; color: #333;'>
            Based on current trends, by 2028, the projected annual <strong>Fiscal Gap</strong> will be:
        </p>
        <h2 style='color: {status_color}; font-size: 2.5rem; margin: 10px 0;'>
            {deficit_2028:.2f} Trillion KSh {status}
        </h2>
        <p style='color: #555;'>
            {'This implies continued heavy reliance on borrowing to fund the budget shortfall.' if deficit_2028 > 0 else 'This indicates a move towards fiscal independence.'}
        </p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.warning("Insufficient Revenue/Expenditure data to generate predictions.")

# --- SUSTAINABILITY ANALYSIS ---
st.markdown("<div class='section-header'>⚖️ Debt Sustainability (Debt-to-GDP)</div>", unsafe_allow_html=True)

gdp_df = full_df[full_df['Indicator'] == 'Nominal GDP'].copy()
gdp_df = gdp_df.sort_values('Time')

if not gdp_df.empty and not debt_series.empty:
    ann_debt = debt_series.groupby('Year')['Amount_KSh'].mean().reset_index(name='Total_Debt')
    ann_gdp = gdp_df.groupby('Year')['Amount_KSh'].mean().reset_index(name='Nominal_GDP')
    
    sus_df = pd.merge(ann_debt, ann_gdp, on='Year')
    sus_df['Debt_to_GDP'] = (sus_df['Total_Debt'] / sus_df['Nominal_GDP']) * 100
    
    latest_ratio = sus_df['Debt_to_GDP'].iloc[-1]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        fig_sus = go.Figure()
        
        fig_sus.add_trace(go.Scatter(
            x=sus_df['Year'], y=sus_df['Debt_to_GDP'],
            mode='lines+markers+text',
            name='Debt % of GDP',
            line=dict(color='#B00020', width=6),
            marker=dict(size=12, color='white', line=dict(width=2, color='#B00020')),
            text=[f"{val:.1f}%" for val in sus_df['Debt_to_GDP']], 
            textposition="top center",
            hovertemplate='<b>Year: %{x}</b><br>Ratio: <b>%{y:.2f}%</b><extra></extra>'
        ))
        
        fig_sus.add_hline(y=55, line_dash="dash", line_color="green", annotation_text="IMF Limit (55%)")
        fig_sus.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Critical (70%)")
        
        fig_sus.update_layout(
            title=dict(text="<b>Debt-to-GDP Ratio Evolution</b>", x=0.5, font=dict(size=22)),
            xaxis=dict(title="<b>Year</b>", showgrid=True),
            yaxis=dict(title="<b>Percentage of GDP (%)</b>", showgrid=True),
            height=550,
            template="plotly_white"
        )
        st.plotly_chart(fig_sus, use_container_width=True)
        
    with col2:
        status_color = "#dc3545" if latest_ratio > 55 else "#28a745"
        status_text = "CRITICAL" if latest_ratio > 55 else "SUSTAINABLE"
        
        st.markdown(f"""
        <div style='background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>
            <h4 style='color: #333;'>Current Ratio</h4>
            <h1 style='color: {status_color}; font-size: 3.5rem; margin: 0;'>{latest_ratio:.1f}%</h1>
            <p style='color: #666;'>Status: <strong>{status_text}</strong></p>
            <hr>
            <p style='font-size: 0.9rem; color: #333;'>This means for every 100 Shillings Kenya produces in value, it owes <b>{latest_ratio:.0f} Shillings</b> in debt.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class='graph-explanation'>
        <strong>🔍 Understanding Debt Sustainability:</strong>
        This chart tracks the Debt-to-GDP ratio, a key indicator of a country's ability to pay back its debts.
        <ul>
            <li><strong>Debt % of GDP Line:</strong> Shows the percentage of the country's GDP that is owed in debt.</li>
            <li><strong>IMF Limit (Green Line):</strong> Represents the recommended debt limit (55%) for developing economies to maintain fiscal health.</li>
            <li><strong>Critical Limit (Red Line):</strong> Indicates a danger zone (70%) where the risk of debt distress significantly increases.</li>
        </ul>
        <strong>Key Takeaway:</strong> Comparing the current ratio to these benchmarks shows whether the country's debt burden is manageable or becoming critical.
    </div>
    """, unsafe_allow_html=True)

# RECOMMENDATIONS
st.markdown("---")
st.markdown("<div class='section-header'>💡 Strategic Recommendations</div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🔄 Immediate Actions", "📊 Revenue Strategy", "🏛️ Structural Reform"])

with tab1:
    st.markdown("""
    <div class='recommendation-box'>
        <h4>Short Term (0-12 Months)</h4>
        <ul>
            <li><strong>Fiscal Consolidation:</strong> Reduce non-essential recurrent expenditure by 10%.</li>
            <li><strong>Debt Re-profiling:</strong> Negotiate longer repayment periods for commercial loans to reduce immediate cash crunch.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class='recommendation-box'>
        <h4>Medium Term (1-3 Years)</h4>
        <ul>
            <li><strong>Tax Base Expansion:</strong> Focus on compliance in the informal sector rather than increasing rates on existing taxpayers.</li>
            <li><strong>Digital Systems:</strong> Full automation of revenue collection to seal leakages.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.markdown("""
    <div class='recommendation-box'>
        <h4>Long Term (3+ Years)</h4>
        <ul>
            <li><strong>Legislative Caps:</strong> Enforce strict legal limits on debt ceilings relative to GDP.</li>
            <li><strong>Export Promotion:</strong> Boost manufacturing to earn foreign exchange for external debt servicing.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# FOOTER
st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>Generated by Kenya Debt Guardian AI Analysis Tool</p>", unsafe_allow_html=True)
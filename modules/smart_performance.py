import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render():
    """Render the SMART Performance page"""
    
    st.title("🚀 SMART Performance")
    st.markdown("**Operational Excellence for AMP 8 Programme Delivery**")
    
    # Create tabs for different performance features
    tab1, tab2 = st.tabs([
        "📊 Contract Delivery Status",
        "⚠️ Delivery Risk Overview"
    ])
    
    with tab1:
        render_contract_delivery_tab()
    
    with tab2:
        render_delivery_risk_tab()

def render_contract_delivery_tab():
    """Render the contract delivery status tab"""
    
    st.subheader("📊 Contract Delivery Status")
    st.markdown("**Track completion rates and delivery performance against AMP 8 commitments**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view contract delivery status.")
        return
    
    df = st.session_state.df_sourcing_pipeline
    
    if df.empty:
        st.error("No contract delivery data available.")
        return
    
    # Contract delivery overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        completed_contracts = len(df[df['current_stage'] == 'Contract'])
        st.metric("Completed Contracts", f"{completed_contracts}/{len(df)}")
    
    with col2:
        on_time_rate = (completed_contracts / len(df) * 100) if len(df) > 0 else 0
        st.metric("On-Time Completion", f"{on_time_rate:.1f}%")
    
    with col3:
        total_spend = df['total_value_gbp'].sum() / 1_000_000
        st.metric("Total Programme Spend", f"£{total_spend:.1f}M")
    
    with col4:
        delayed_contracts = len(df[df['risk_level'] == 'High'])
        st.metric("Delayed Contracts", delayed_contracts)
    
    # Contract delivery performance charts
    st.markdown("### Contract Delivery Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract completion dates vs planned dates from project management records\n\n**Insights:** Shows delivery performance across contract categories. Identifies which types of contracts are consistently delivered on time and which require process improvements.")
        
        with chart_col:
            st.markdown("#### Contract Value Distribution by Performance")
            
            # Create violin plot showing value distribution across risk levels
            df_expanded = []
            for _, row in df.iterrows():
                df_expanded.append({
                    'risk_level': row['risk_level'],
                    'value_m': row['total_value_gbp'] / 1_000_000,
                    'category': row['procurement_category']
                })
            
            df_violin = pd.DataFrame(df_expanded)
            
            fig_violin = px.violin(
                df_violin,
                x='risk_level',
                y='value_m',
                color='risk_level',
                box=True,
                title="Contract Value Distribution by Risk Level",
                color_discrete_map={'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}
            )
            
            fig_violin.update_layout(
                height=500,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Risk Level",
                yaxis_title="Contract Value (£M)",
                showlegend=False
            )
            
            st.plotly_chart(fig_violin, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract values and current delivery status from financial management systems\n\n**Insights:** Shows value concentration by delivery status. Helps identify financial exposure from delayed contracts and value delivered to date.")
        
        with chart_col:
            st.markdown("#### Value Delivered vs At Risk")
            
            # Calculate value by delivery status
            delivered_value = df[df['current_stage'] == 'Contract']['total_value_gbp'].sum() / 1_000_000
            at_risk_value = df[df['risk_level'] == 'High']['total_value_gbp'].sum() / 1_000_000
            in_progress_value = df[~df['current_stage'].isin(['Contract']) & (df['risk_level'] != 'High')]['total_value_gbp'].sum() / 1_000_000
            
            value_data = pd.DataFrame({
                'Status': ['Delivered', 'In Progress', 'At Risk'],
                'Value': [delivered_value, in_progress_value, at_risk_value]
            })
            
            fig_value = px.bar(
                value_data,
                x='Status',
                y='Value',
                title="Contract Value by Delivery Status (£M)",
                color='Status',
                color_discrete_map={'Delivered': '#28a745', 'In Progress': '#ffc107', 'At Risk': '#dc3545'}
            )
            
            fig_value.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Delivery Status",
                yaxis_title="Value (£M)",
                showlegend=False
            )
            
            st.plotly_chart(fig_value, use_container_width=True)

def render_delivery_risk_tab():
    """Render the delivery risk overview tab"""
    
    st.subheader("⚠️ Delivery Risk Overview")
    st.markdown("**Identify and monitor delivery risks that could impact AMP 8 regulatory commitments**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view delivery risks.")
        return
    
    # Use supply chain risks data
    df_risks = st.session_state.df_supply_chain_risks
    df_contracts = st.session_state.df_sourcing_pipeline
    
    if df_risks.empty:
        st.error("No delivery risk data available.")
        return
    
    # Risk overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        high_risks = len(df_risks[df_risks['impact'] == 'High'])
        st.metric("High Risk Items", high_risks)
    
    with col2:
        financial_exposure = df_risks[df_risks['impact'] == 'High']['estimated_cost_impact_gbp_m'].sum()
        st.metric("Financial Exposure", f"£{financial_exposure:.1f}M")
    
    with col3:
        regulatory_risks = len(df_risks[df_risks['risk_category'].str.contains('Regulatory|Compliance', case=False, na=False)])
        st.metric("Regulatory Risks", regulatory_risks)
    
    with col4:
        avg_response_time = df_risks['timeline_to_impact_days'].mean()
        st.metric("Avg. Timeline to Impact", f"{avg_response_time:.0f} days")
    
    # Risk analysis charts
    st.markdown("### Delivery Risk Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Risk register with categories and severity levels from project risk assessments\n\n**Insights:** Shows risk distribution across different categories. Helps prioritize risk management efforts and identify systemic issues that could impact multiple contracts.")
        
        with chart_col:
            st.markdown("#### Risk Category Hierarchy")
            
            # Create heatmap for risk distribution across categories and impacts
            risk_pivot = df_risks.pivot_table(
                values='estimated_cost_impact_gbp_m', 
                index='risk_category', 
                columns='impact', 
                aggfunc='sum', 
                fill_value=0
            )
            
            fig_heatmap = px.imshow(
                risk_pivot.values,
                x=risk_pivot.columns,
                y=risk_pivot.index,
                color_continuous_scale='Reds',
                title="Risk Impact Heatmap (£M by Category & Severity)",
                text_auto=True
            )
            
            fig_heatmap.update_layout(
                height=500,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Risk Impact Level",
                yaxis_title="Risk Category"
            )
            
            fig_heatmap.update_traces(textfont_color='white')
            
            st.plotly_chart(fig_heatmap, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Financial impact estimates from risk assessments and mitigation cost tracking\n\n**Insights:** Shows potential financial exposure from delivery risks. Helps prioritize mitigation investments and understand the cost-benefit of risk management actions.")
        
        with chart_col:
            st.markdown("#### Risk Impact Waterfall Analysis")
            
            # Create waterfall chart showing cumulative risk impact
            impact_analysis = df_risks.groupby('impact').agg({
                'estimated_cost_impact_gbp_m': 'sum'
            }).reset_index()
            impact_analysis = impact_analysis.sort_values('estimated_cost_impact_gbp_m')
            
            # Create waterfall chart
            x_labels = ['Baseline'] + list(impact_analysis['impact']) + ['Total Risk']
            y_values = [0] + list(impact_analysis['estimated_cost_impact_gbp_m']) + [impact_analysis['estimated_cost_impact_gbp_m'].sum()]
            
            fig_waterfall = go.Figure(go.Waterfall(
                name="Risk Impact",
                orientation="v",
                measure=["absolute"] + ["relative"] * len(impact_analysis) + ["total"],
                x=x_labels,
                y=y_values,
                text=[f"£{v:.1f}M" for v in y_values],
                textposition="outside",
                connector={"line":{"color":"rgb(63, 63, 63)"}},
                increasing={"marker":{"color":"#dc3545"}},
                decreasing={"marker":{"color":"#28a745"}},
                totals={"marker":{"color":"#00C5E7"}}
            ))
            
            fig_waterfall.update_layout(
                title="Cumulative Financial Risk Impact (£M)",
                height=500,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Risk Category",
                yaxis_title="Financial Impact (£M)"
            )
            
            st.plotly_chart(fig_waterfall, use_container_width=True)

def render_customer_impact_tab():
    """Render the customer impact dashboard tab"""
    
    st.subheader("👥 Customer Impact Dashboard")
    st.markdown("**Track how contract delivery affects customer service levels and affordability**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view customer impact analysis.")
        return
    
    df_contracts = st.session_state.df_sourcing_pipeline
    
    if df_contracts.empty:
        st.error("No contract data available for customer impact analysis.")
        return
    
    # Customer impact overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_investment = df_contracts['total_value_gbp'].sum() / 1_000_000
        customer_investment = total_investment / 15  # Thames Water customer base (millions)
        st.metric("Investment per Customer", f"£{customer_investment:.0f}")
    
    with col2:
        service_affecting = len(df_contracts[df_contracts['procurement_category'].str.contains('Construction|Design', case=False, na=False)])
        st.metric("Service-Affecting Contracts", service_affecting)
    
    with col3:
        delayed_impact = len(df_contracts[df_contracts['risk_level'] == 'High'])
        st.metric("Delayed Service Improvements", delayed_impact)
    
    with col4:
        completion_rate = len(df_contracts[df_contracts['current_stage'] == 'Contract']) / len(df_contracts) * 100
        st.metric("Service Delivery Rate", f"{completion_rate:.1f}%")
    
    # Customer impact analysis
    st.markdown("### Customer Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract values divided by customer base to show per-customer investment impact\n\n**Insights:** Shows which contracts have the highest impact on customer bills. Helps prioritize contracts based on customer affordability and value delivery.")
        
        with chart_col:
            st.markdown("#### Customer Bill Impact by Contract")
            
            # Calculate customer bill impact
            df_contracts['customer_bill_impact'] = df_contracts['total_value_gbp'] / 15_000_000  # Customer base
            top_impact = df_contracts.nlargest(10, 'customer_bill_impact')[['package_name', 'customer_bill_impact', 'current_stage']]
            
            fig_bill_impact = px.bar(
                top_impact,
                x='customer_bill_impact',
                y='package_name',
                orientation='h',
                color='current_stage',
                title="Top 10 Contracts by Customer Bill Impact (£ per customer)",
                color_discrete_sequence=['#dc3545', '#ffc107', '#28a745', '#00C5E7', '#6f42c1']
            )
            
            fig_bill_impact.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Customer Bill Impact (£)",
                yaxis_title="Contract"
            )
            
            st.plotly_chart(fig_bill_impact, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract delivery status mapped to service improvement categories\n\n**Insights:** Shows progress on delivering service improvements to customers. Helps communicate delivery progress and identify areas where customer service could be enhanced.")
        
        with chart_col:
            st.markdown("#### Service Improvement Delivery Progress")
            
            # Map contracts to service categories
            def categorize_service_impact(category):
                if 'Construction' in category or 'Design' in category:
                    return 'Infrastructure Improvements'
                elif 'Technology' in category:
                    return 'Digital Services'
                elif 'Testing' in category:
                    return 'Quality Assurance'
                else:
                    return 'Operational Support'
            
            df_contracts['service_category'] = df_contracts['procurement_category'].apply(categorize_service_impact)
            
            service_progress = df_contracts.groupby(['service_category', 'current_stage']).size().reset_index(name='count')
            
            fig_service = px.bar(
                service_progress,
                x='service_category',
                y='count',
                color='current_stage',
                title="Service Improvement Progress by Category",
                color_discrete_sequence=['#dc3545', '#ffc107', '#28a745', '#00C5E7', '#6f42c1']
            )
            
            fig_service.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Service Category",
                yaxis_title="Number of Contracts",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_service, use_container_width=True)
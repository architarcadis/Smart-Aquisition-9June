import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render():
    """Render the SMART Sourcing page"""
    
    st.title("💼 SMART Sourcing")
    st.markdown("**Contract Delivery Management for AMP 8 Programme**")
    
    # Create tabs for different sourcing features
    tab1, tab2, tab3 = st.tabs([
        "📊 Project Delivery Tracker", 
        "🏢 Supplier Market Health",
        "📋 Contract Pipeline Planning"
    ])
    
    with tab1:
        render_project_delivery_tab()
    
    with tab2:
        render_supplier_market_tab()
    
    with tab3:
        render_contract_pipeline_tab()

def render_project_delivery_tab():
    """Render the project delivery tracker tab"""
    
    st.subheader("📊 Project Delivery Tracker")
    st.markdown("**Real-time visibility of Thames Water AMP 8 contract delivery against regulatory deadlines**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view project delivery status.")
        return
    
    df = st.session_state.df_sourcing_pipeline
    
    if df.empty:
        st.error("No project delivery data available.")
        return
    
    # AMP 8 delivery overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_value = df['total_value_gbp'].sum() / 1_000_000
        st.metric("Total AMP 8 Value", f"£{total_value:.1f}M")
    
    with col2:
        on_track = len(df[df['current_stage'].isin(['Contract', 'Award'])])
        st.metric("Contracts Delivered", f"{on_track}/{len(df)}")
    
    with col3:
        delayed = len(df[df['risk_level'] == 'High'])
        st.metric("At Risk Projects", delayed)
    
    with col4:
        budget_variance = 0.0  # Simplified for now
        st.metric("Budget Variance", f"{budget_variance:.1f}%")
    
    # Contract delivery status timeline
    st.markdown("### AMP 8 Contract Delivery Status")
    
    # Create RAG status based on procurement stage and risk level
    def get_rag_status(row):
        if row['current_stage'] in ['Contract', 'Award']:
            return 'Green'
        elif row['risk_level'] == 'High':
            return 'Red'
        elif row['current_stage'] in ['Evaluation', 'Tender Process']:
            return 'Amber'
        else:
            return 'Green'
    
    df['rag_status'] = df.apply(get_rag_status, axis=1)
    
    # Contract status distribution
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract register with current procurement stages and risk assessments\n\n**Insights:** Shows overall delivery health - green indicates on-track contracts, amber shows contracts in active procurement, red flags high-risk contracts requiring immediate attention.")
        
        with chart_col:
            st.markdown("#### Contract Delivery Status (RAG)")
            status_counts = df['rag_status'].value_counts()
            fig_rag = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                color_discrete_map={'Green': '#28a745', 'Amber': '#ffc107', 'Red': '#dc3545'}
            )
            fig_rag.update_traces(textposition='inside', textinfo='percent+label')
            fig_rag.update_layout(
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_rag, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract values aggregated by current procurement stage\n\n**Insights:** Identifies where the most value is concentrated in the procurement pipeline. Helps prioritize resource allocation and identify potential delivery bottlenecks by value.")
        
        with chart_col:
            st.markdown("#### Contract Value by Delivery Stage (£M)")
            stage_values = df.groupby('current_stage')['total_value_gbp'].sum().sort_values(ascending=True) / 1_000_000
            fig_stages = px.bar(
                x=stage_values.values,
                y=stage_values.index,
                orientation='h',
                color_discrete_sequence=['#00C5E7']
            )
            fig_stages.update_layout(
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=400,
                xaxis_title="Value (£M)",
                yaxis_title="Delivery Stage"
            )
            st.plotly_chart(fig_stages, use_container_width=True)

def render_supplier_market_tab():
    """Render the supplier market health tab"""
    
    st.subheader("🏢 Supplier Market Health")
    st.markdown("**Supplier capacity and market readiness for Thames Water AMP 8 delivery**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view supplier market health.")
        return
    
    # Use sourcing pipeline data to analyze supplier responses and market health
    df = st.session_state.df_sourcing_pipeline
    
    if df.empty:
        st.error("No supplier market data available.")
        return
    
    # Market health overview
    st.markdown("### Supplier Market Readiness")
    
    # Market health metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_bidders = df['supplier_responses'].mean()
        st.metric("Avg. Bidders per Contract", f"{avg_bidders:.1f}")
    
    with col2:
        healthy_competition = len(df[df['supplier_responses'] >= 3])
        st.metric("Healthy Competition", f"{healthy_competition}/{len(df)}")
    
    with col3:
        infrastructure_contracts = len(df[df['procurement_category'].str.contains('Construction|Design', case=False, na=False)])
        st.metric("Infrastructure Contracts", infrastructure_contracts)
    
    with col4:
        market_capacity = "Available" if avg_bidders >= 3 else "Constrained"
        st.metric("Market Capacity Status", market_capacity)
    
    # Market health analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Number of supplier responses received per tender by procurement category\n\n**Insights:** Shows market capacity and competition levels across different contract types. Low response rates indicate market constraints or barriers to entry that may require strategy adjustments.")
        
        with chart_col:
            st.markdown("#### Supplier Response Rates")
            response_analysis = df.groupby('procurement_category')['supplier_responses'].agg(['mean', 'count']).round(1)
            
            fig_responses = px.bar(
                x=response_analysis.index,
                y=response_analysis['mean'],
                title="Average Supplier Responses by Category",
                color_discrete_sequence=['#00C5E7']
            )
            
            fig_responses.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Contract Category",
                yaxis_title="Avg. Bidders",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_responses, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Supplier response rates segmented by contract value bands\n\n**Insights:** Reveals market capacity constraints at different value levels. Higher value contracts typically attract fewer bidders due to capability requirements and risk appetite.")
        
        with chart_col:
            st.markdown("#### Market Capacity by Value")
            df['value_band'] = pd.cut(df['total_value_gbp']/1_000_000, 
                                     bins=[0, 1, 5, 20, 100, float('inf')], 
                                     labels=['<£1M', '£1-5M', '£5-20M', '£20-100M', '>£100M'])
            
            capacity_analysis = df.groupby('value_band')['supplier_responses'].mean()
            
            fig_capacity = px.bar(
                x=capacity_analysis.index,
                y=capacity_analysis.values,
                title="Market Capacity by Contract Value",
                color_discrete_sequence=['#28a745']
            )
            
            fig_capacity.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Contract Value Band",
                yaxis_title="Avg. Bidders"
            )
            
            st.plotly_chart(fig_capacity, use_container_width=True)

def render_contract_pipeline_tab():
    """Render the contract pipeline planning tab"""
    
    st.subheader("📋 Contract Pipeline Planning")
    st.markdown("**Strategic planning for upcoming Thames Water AMP 8 contract awards**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view contract pipeline planning.")
        return
    
    df = st.session_state.df_sourcing_pipeline
    
    if df.empty:
        st.error("No contract pipeline data available.")
        return
    
    # Contract pipeline planning overview
    st.markdown("### Upcoming Contract Awards & Renewals")
    
    # Pipeline planning metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        upcoming_awards = len(df[df['current_stage'].isin(['Tender Process', 'Evaluation'])])
        st.metric("Upcoming Awards", upcoming_awards)
    
    with col2:
        pending_value = df[df['current_stage'].isin(['Tender Process', 'Evaluation'])]['total_value_gbp'].sum() / 1_000_000
        st.metric("Pending Award Value", f"£{pending_value:.1f}M")
    
    with col3:
        high_priority = len(df[df['risk_level'] == 'High'])
        st.metric("High Priority Contracts", high_priority)
    
    with col4:
        regulatory_critical = len(df[df['procurement_category'].str.contains('Construction|Design', case=False, na=False)])
        st.metric("Regulatory Critical", regulatory_critical)
    
    # Contract planning timeline
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract register showing current procurement stage and contract counts\n\n**Insights:** Identifies delivery bottlenecks and procurement capacity planning needs. Shows where contracts are stalling and resource allocation requirements.")
        
        with chart_col:
            st.markdown("#### Contract Award Timeline")
            timeline_data = df.groupby('current_stage').agg({
                'package_name': 'count',
                'total_value_gbp': 'sum'
            }).reset_index()
            
            fig_timeline = px.bar(
                timeline_data,
                x='current_stage',
                y='package_name',
                title="Contracts by Delivery Stage",
                color_discrete_sequence=['#00C5E7']
            )
            
            fig_timeline.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Procurement Stage",
                yaxis_title="Number of Contracts",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract values divided by customer base to calculate per-customer impact\n\n**Insights:** Prioritizes contracts by their potential impact on customer bills. Helps focus on high-value contracts that could significantly affect affordability.")
        
        with chart_col:
            st.markdown("#### Customer Bill Impact Priority")
            df['customer_impact'] = df['total_value_gbp'] / 15_000_000  # Thames Water customer base
            
            impact_priority = df.nlargest(8, 'customer_impact')[['package_name', 'total_value_gbp', 'customer_impact']]
            impact_priority['total_value_gbp'] = impact_priority['total_value_gbp'] / 1_000_000
            
            fig_impact = px.bar(
                impact_priority,
                x='customer_impact',
                y='package_name',
                orientation='h',
                title="Contract Priority by Customer Impact",
                color_discrete_sequence=['#dc3545']
            )
            
            fig_impact.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Customer Impact (£)",
                yaxis_title="Contract"
            )
            
            st.plotly_chart(fig_impact, use_container_width=True)
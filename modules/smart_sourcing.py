import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render():
    """Render the SMART Sourcing page"""
    
    st.title("💼 SMART Sourcing")
    st.markdown("**Contract Delivery Management for AMP 8 Programme**")
    
    # Create tabs for different sourcing features
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Project Delivery Tracker", 
        "🏢 Supplier Market Health",
        "📋 Contract Pipeline Planning",
        "📈 Demand Pipeline"
    ])
    
    with tab1:
        render_project_delivery_tab()
    
    with tab2:
        render_supplier_market_tab()
    
    with tab3:
        render_contract_pipeline_tab()
    
    with tab4:
        render_demand_pipeline_tab()

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
        # Calculate potential regulatory penalties for delayed contracts
        penalty_exposure = delayed * 2.5  # Simplified: £2.5M average penalty per delayed contract
        st.metric("Regulatory Penalty Exposure", f"£{penalty_exposure:.1f}M")
    
    with col4:
        # Calculate critical path dependencies
        critical_path_blocked = len(df[df['risk_level'] == 'High']) // 2
        st.metric("Critical Path Dependencies", f"{critical_path_blocked} blocked")
    
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
    
    # Contract delivery status with balanced chart types
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
                height=500,
                showlegend=True
            )
            st.plotly_chart(fig_rag, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract values aggregated by current procurement stage\n\n**Insights:** Shows procurement flow and identifies bottlenecks. Funnel shape reveals where contracts are stalling and resource allocation needs.")
        
        with chart_col:
            st.markdown("#### Procurement Pipeline Flow")
            
            # Keep funnel chart - it's perfect for showing pipeline flow
            stage_order = ['Market Analysis', 'RFQ Preparation', 'Tender Process', 'Evaluation', 'Award', 'Contract']
            stage_counts = df['current_stage'].value_counts().reindex(stage_order, fill_value=0)
            stage_values = df.groupby('current_stage')['total_value_gbp'].sum().reindex(stage_order, fill_value=0) / 1_000_000
            
            fig_funnel = go.Figure(go.Funnel(
                y = stage_order,
                x = stage_counts.values,
                textinfo = "value+percent initial",
                texttemplate = "%{value} contracts<br>(%{percentInitial})",
                hovertemplate = "<b>Stage:</b> %{y}<br><b>Contracts:</b> %{x}<br><b>Value:</b> £%{customdata:.1f}M<extra></extra>",
                customdata = stage_values.values,
                marker = {"color": ["#dc3545", "#fd7e14", "#ffc107", "#20c997", "#0dcaf0", "#28a745"]}
            ))
            
            fig_funnel.update_layout(
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500
            )
            st.plotly_chart(fig_funnel, use_container_width=True)

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
    
    # Market health analysis with balanced chart types
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Number of supplier responses received per tender by procurement category\n\n**Insights:** Shows market capacity and competition levels across different contract types. Low response rates indicate market constraints or barriers to entry that may require strategy adjustments.")
        
        with chart_col:
            st.markdown("#### Market Capacity Utilization")
            
            # Create gauge chart for market capacity
            response_analysis = df.groupby('procurement_category')['supplier_responses'].mean()
            overall_capacity = min(100, (response_analysis.mean() / 5.0) * 100)  # Scale to 100%
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = overall_capacity,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Market Capacity"},
                delta = {'reference': 80},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#00C5E7"},
                    'steps': [
                        {'range': [0, 50], 'color': "rgba(220, 53, 69, 0.3)"},
                        {'range': [50, 80], 'color': "rgba(255, 193, 7, 0.3)"},
                        {'range': [80, 100], 'color': "rgba(40, 167, 69, 0.3)"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=500,
                font=dict(color='white', size=12),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Used:** Contract value and supplier response data creating market concentration view\n\n**Insights:** Treemap shows market size (area) vs competition level (color). Large red areas indicate high-value, low-competition markets requiring strategic attention.")
        
        with chart_col:
            st.markdown("#### Market Concentration Map")
            
            # Keep treemap - it's perfect for showing market concentration
            market_data = df.groupby('procurement_category').agg({
                'total_value_gbp': 'sum',
                'supplier_responses': 'mean'
            }).reset_index()
            market_data['total_value_gbp'] = market_data['total_value_gbp'] / 1_000_000
            
            fig_treemap = px.treemap(
                market_data,
                path=['procurement_category'],
                values='total_value_gbp',
                color='supplier_responses',
                color_continuous_scale=['#dc3545', '#ffc107', '#28a745']
            )
            
            fig_treemap.update_layout(
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=500
            )
            
            st.plotly_chart(fig_treemap, use_container_width=True)

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
    
    # Contract planning timeline with balanced chart types
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

def render_demand_pipeline_tab():
    """Render the demand pipeline tab"""
    
    st.subheader("📈 Demand Pipeline")
    st.markdown("**Future procurement opportunities and market demand forecasting**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view demand pipeline.")
        return
    
    df = st.session_state.df_demand_pipeline
    
    if df.empty:
        st.error("No demand pipeline data available.")
        return
    
    # Pipeline overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_value = df['estimated_value_gbp_m'].sum()
        st.metric("Total Pipeline Value", f"£{total_value:,.0f}M")
    
    with col2:
        total_projects = len(df)
        st.metric("Total Projects", total_projects)
    
    with col3:
        avg_probability = df['probability_percent'].mean()
        st.metric("Avg. Probability", f"{avg_probability:.1f}%")
    
    with col4:
        weighted_value = (df['estimated_value_gbp_m'] * df['probability_percent'] / 100).sum()
        st.metric("Weighted Value", f"£{weighted_value:,.0f}M")
    
    # Pipeline visualization
    st.markdown("### Pipeline Timeline")
    
    # Convert dates for plotting
    df_plot = df.copy()
    df_plot['start_date'] = pd.to_datetime(df_plot['start_date'])
    df_plot['end_date'] = pd.to_datetime(df_plot['end_date'])
    
    # Create Gantt-like chart
    fig_timeline = px.timeline(
        df_plot,
        x_start="start_date",
        x_end="end_date",
        y="project_name",
        color="estimated_value_gbp_m",
        hover_data=["project_type", "probability_percent", "region"],
        title="Project Timeline and Values"
    )
    
    fig_timeline.update_layout(
        height=600,
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Status and regional analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Required:** Project status from business development pipeline and opportunity management systems\n\n**Insights:** Shows distribution of pipeline value across different project stages. Helps prioritize business development efforts and resource allocation.")
        
        with chart_col:
            st.markdown("#### Pipeline by Status")
            
            status_summary = df.groupby('status').agg({
                'estimated_value_gbp_m': 'sum',
                'project_name': 'count'
            }).reset_index()
            
            fig_status = px.pie(
                status_summary,
                values='estimated_value_gbp_m',
                names='status',
                title="Pipeline Value by Status"
            )
            
            fig_status.update_layout(
                height=500,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Required:** Regional project distribution from geographic opportunity mapping\n\n**Insights:** Shows geographic concentration of pipeline opportunities. Essential for regional resource planning and market expansion strategy.")
        
        with chart_col:
            st.markdown("#### Regional Distribution")
            
            regional_summary = df.groupby('region').agg({
                'estimated_value_gbp_m': 'sum',
                'project_name': 'count'
            }).reset_index()
            
            fig_region = px.bar(
                regional_summary,
                x='region',
                y='estimated_value_gbp_m',
                title="Pipeline Value by Region",
                color_discrete_sequence=['#00C5E7']
            )
            
            fig_region.update_layout(
                height=500,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Region",
                yaxis_title="Pipeline Value (£M)"
            )
            
            st.plotly_chart(fig_region, use_container_width=True)
    
    # Detailed pipeline table
    st.markdown("### Detailed Pipeline View")
    st.dataframe(
        df.sort_values('estimated_value_gbp_m', ascending=False),
        use_container_width=True,
        height=400
    )
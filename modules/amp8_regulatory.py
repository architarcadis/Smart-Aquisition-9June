import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render():
    """Render the AMP 8 Regulatory Dashboard page"""
    
    st.title("📋 AMP 8 Regulatory Dashboard")
    st.markdown("**Real-time tracking of Ofwat Performance Commitments and regulatory compliance**")
    
    # Create tabs for regulatory tracking
    tab1, tab2, tab3 = st.tabs([
        "📊 Performance Commitment RAG Status",
        "💰 ODI Financial Impact", 
        "📈 Business Plan Variance"
    ])
    
    with tab1:
        render_performance_commitments_tab()
    
    with tab2:
        render_odi_financial_tab()
    
    with tab3:
        render_business_plan_variance_tab()

def render_performance_commitments_tab():
    """Render the Performance Commitments tracking tab"""
    
    st.subheader("📊 Performance Commitment RAG Status")
    st.markdown("**Real-time tracking against all Ofwat Performance Commitments for AMP 8**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view Performance Commitment tracking.")
        return
    
    # Generate Performance Commitment data
    pc_categories = [
        'Water Quality Compliance', 'Supply Interruptions', 'Water Treatment Works Performance',
        'Leakage Reduction', 'Per Capita Consumption', 'Business Customer Satisfaction',
        'Household Customer Satisfaction', 'Developer Services Satisfaction', 'C-MeX Score',
        'D-MeX Score', 'Biodiversity Enhancement', 'Operational Carbon', 'Abstraction Reduction',
        'Serious Pollution Incidents', 'Asset Health'
    ]
    
    pc_data = []
    for i, pc in enumerate(pc_categories):
        # Simulate realistic PC performance
        target_performance = 95 if 'Satisfaction' in pc else 100 if 'Quality' in pc else 90
        if 'Leakage' in pc or 'Carbon' in pc:
            target_performance = 85  # Reduction targets are harder
        
        current_performance = target_performance + (hash(pc) % 20 - 10)  # Vary performance
        current_performance = max(0, min(100, current_performance))
        
        if current_performance >= target_performance * 0.95:
            rag_status = 'Green'
        elif current_performance >= target_performance * 0.85:
            rag_status = 'Amber'
        else:
            rag_status = 'Red'
        
        pc_data.append({
            'performance_commitment': pc,
            'target_performance': target_performance,
            'current_performance': current_performance,
            'rag_status': rag_status,
            'variance': current_performance - target_performance,
            'category': 'Service Quality' if 'Quality' in pc or 'Satisfaction' in pc else 
                       'Environmental' if any(x in pc for x in ['Biodiversity', 'Carbon', 'Pollution']) else
                       'Operational'
        })
    
    pc_df = pd.DataFrame(pc_data)
    
    # Performance Commitment overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        green_pcs = len(pc_df[pc_df['rag_status'] == 'Green'])
        st.metric("On Track (Green)", f"{green_pcs}/{len(pc_df)}")
    
    with col2:
        amber_pcs = len(pc_df[pc_df['rag_status'] == 'Amber'])
        st.metric("At Risk (Amber)", amber_pcs)
    
    with col3:
        red_pcs = len(pc_df[pc_df['rag_status'] == 'Red'])
        st.metric("Off Track (Red)", red_pcs)
    
    with col4:
        avg_performance = pc_df['current_performance'].mean()
        st.metric("Average Performance", f"{avg_performance:.1f}%")
    
    # Performance Commitment analysis
    st.markdown("### Performance Commitment Status Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Required:** Performance commitment register, actual vs target performance from regulatory team quarterly submissions\n\n**Insights:** Shows RAG status across all 15+ Ofwat commitments. Essential for regulatory compliance and penalty avoidance.")
        
        with chart_col:
            st.markdown("#### Performance Commitment RAG Overview")
            
            rag_counts = pc_df['rag_status'].value_counts()
            fig_rag = px.pie(
                values=rag_counts.values,
                names=rag_counts.index,
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
            st.markdown("ℹ️", help="**Data Required:** Current performance vs target thresholds by commitment category\n\n**Insights:** Shows performance variance across operational, environmental and service quality commitments. Identifies systematic delivery challenges.")
        
        with chart_col:
            st.markdown("#### Performance Category Radar")
            
            # Create radar chart for performance tracking
            category_performance = pc_df.groupby('category').agg({
                'current_performance': 'mean',
                'target_performance': 'mean'
            }).reset_index()
            
            categories = list(category_performance['category'])
            current_values = list(category_performance['current_performance'])
            target_values = list(category_performance['target_performance'])
            
            fig_radar = go.Figure()
            
            # Add current performance
            fig_radar.add_trace(go.Scatterpolar(
                r=current_values,
                theta=categories,
                fill='toself',
                name='Current Performance',
                line_color='#00C5E7'
            ))
            
            # Add target performance
            fig_radar.add_trace(go.Scatterpolar(
                r=target_values,
                theta=categories,
                fill='toself',
                name='Target Performance',
                line_color='#dc3545',
                opacity=0.6
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        color='white'
                    ),
                    angularaxis=dict(color='white')
                ),
                showlegend=True,
                height=500,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                title="Current vs Target Performance"
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
    
    # Detailed Performance Commitment table
    st.markdown("### Detailed Performance Commitment Status")
    
    # Format data for display
    display_df = pc_df[['performance_commitment', 'current_performance', 'target_performance', 'variance', 'rag_status']].copy()
    display_df['current_performance'] = display_df['current_performance'].round(1)
    display_df['target_performance'] = display_df['target_performance'].round(1)
    display_df['variance'] = display_df['variance'].round(1)
    
    st.dataframe(
        display_df,
        column_config={
            "performance_commitment": "Performance Commitment",
            "current_performance": "Current (%)",
            "target_performance": "Target (%)",
            "variance": "Variance",
            "rag_status": "RAG Status"
        },
        hide_index=True,
        use_container_width=True
    )

def render_odi_financial_tab():
    """Render the ODI Financial Impact tab"""
    
    st.subheader("💰 ODI Financial Impact")
    st.markdown("**Outcome Delivery Incentive rewards and penalties by performance area**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view ODI financial impact.")
        return
    
    # Generate ODI financial impact data
    odi_areas = [
        'Water Quality', 'Customer Satisfaction', 'Leakage', 'Supply Interruptions',
        'Environmental Performance', 'Developer Services', 'Pollution Incidents',
        'Asset Reliability', 'Innovation'
    ]
    
    odi_data = []
    for area in odi_areas:
        # Simulate realistic ODI impacts
        max_reward = 2.5 if 'Innovation' in area else 1.5 if 'Quality' in area else 1.0
        max_penalty = -max_reward * 1.5  # Penalties typically higher
        
        # Current projected impact based on performance
        performance_factor = (hash(area) % 100 - 50) / 50  # -1 to 1
        projected_impact = performance_factor * max_reward
        
        odi_data.append({
            'odi_area': area,
            'max_reward_gbp_m': max_reward,
            'max_penalty_gbp_m': max_penalty,
            'projected_impact_gbp_m': projected_impact,
            'impact_type': 'Reward' if projected_impact > 0 else 'Penalty' if projected_impact < 0 else 'Neutral'
        })
    
    odi_df = pd.DataFrame(odi_data)
    
    # ODI financial overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_projected_rewards = odi_df[odi_df['projected_impact_gbp_m'] > 0]['projected_impact_gbp_m'].sum()
        st.metric("Projected Rewards", f"£{total_projected_rewards:.1f}M")
    
    with col2:
        total_projected_penalties = odi_df[odi_df['projected_impact_gbp_m'] < 0]['projected_impact_gbp_m'].sum()
        st.metric("Projected Penalties", f"£{total_projected_penalties:.1f}M")
    
    with col3:
        net_odi_impact = odi_df['projected_impact_gbp_m'].sum()
        st.metric("Net ODI Impact", f"£{net_odi_impact:.1f}M")
    
    with col4:
        areas_at_risk = len(odi_df[odi_df['projected_impact_gbp_m'] < -0.5])
        st.metric("Areas at Penalty Risk", areas_at_risk)
    
    # ODI financial analysis
    st.markdown("### ODI Financial Impact Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Required:** ODI calculation methodologies, current performance projections from finance team management reporting\n\n**Insights:** Shows potential financial rewards and penalties across performance areas. Critical for financial planning and performance prioritization.")
        
        with chart_col:
            st.markdown("#### ODI Impact by Performance Area")
            
            fig_odi = px.bar(
                odi_df,
                x='odi_area',
                y='projected_impact_gbp_m',
                color='impact_type',
                title="Projected ODI Financial Impact (£M)",
                color_discrete_map={'Reward': '#28a745', 'Penalty': '#dc3545', 'Neutral': '#6c757d'}
            )
            
            fig_odi.add_hline(y=0, line_dash="dash", line_color="white")
            
            fig_odi.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Performance Area",
                yaxis_title="Financial Impact (£M)",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_odi, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Required:** Maximum reward and penalty thresholds vs current projected performance\n\n**Insights:** Shows risk-reward potential across ODI areas. Helps prioritize investment to maximize rewards and minimize penalties.")
        
        with chart_col:
            st.markdown("#### ODI Risk-Reward Analysis")
            
            # Create box plot showing distribution of ODI impacts by area type
            odi_expanded = []
            for _, row in odi_df.iterrows():
                area_type = 'High Value' if row['max_reward_gbp_m'] > 1.5 else 'Standard'
                odi_expanded.extend([
                    {'area': row['odi_area'], 'type': 'Reward Potential', 'value': row['max_reward_gbp_m'], 'area_type': area_type},
                    {'area': row['odi_area'], 'type': 'Penalty Risk', 'value': abs(row['max_penalty_gbp_m']), 'area_type': area_type},
                    {'area': row['odi_area'], 'type': 'Current Projection', 'value': abs(row['projected_impact_gbp_m']), 'area_type': area_type}
                ])
            
            odi_box_df = pd.DataFrame(odi_expanded)
            
            fig_box = px.box(
                odi_box_df,
                x='type',
                y='value',
                color='area_type',
                title="ODI Value Distribution by Impact Type",
                color_discrete_map={'High Value': '#00C5E7', 'Standard': '#6c757d'}
            )
            
            fig_box.update_layout(
                height=500,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="ODI Impact Type",
                yaxis_title="Financial Impact (£M)"
            )
            
            st.plotly_chart(fig_box, use_container_width=True)

def render_business_plan_variance_tab():
    """Render the Business Plan Variance tab"""
    
    st.subheader("📈 Business Plan Variance")
    st.markdown("**Actual vs planned investment and outcomes across AMP 8 programme**")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view business plan variance.")
        return
    
    # Generate business plan variance data
    investment_areas = [
        'Water Treatment Enhancement', 'Network Resilience', 'Digital Transformation',
        'Environmental Compliance', 'Customer Experience', 'Asset Replacement',
        'Innovation Programme', 'Operational Efficiency'
    ]
    
    variance_data = []
    for area in investment_areas:
        planned_investment = 100 + (hash(area) % 200)  # £100-300M range
        actual_investment = planned_investment * (0.8 + (hash(area + 'actual') % 40) / 100)  # 80-120% of planned
        variance_percent = ((actual_investment - planned_investment) / planned_investment) * 100
        
        variance_data.append({
            'investment_area': area,
            'planned_investment_gbp_m': planned_investment,
            'actual_investment_gbp_m': actual_investment,
            'variance_percent': variance_percent,
            'variance_status': 'Over Budget' if variance_percent > 5 else 'Under Budget' if variance_percent < -5 else 'On Track'
        })
    
    variance_df = pd.DataFrame(variance_data)
    
    # Business plan variance overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_planned = variance_df['planned_investment_gbp_m'].sum()
        st.metric("Total Planned Investment", f"£{total_planned:.0f}M")
    
    with col2:
        total_actual = variance_df['actual_investment_gbp_m'].sum()
        st.metric("Actual Investment", f"£{total_actual:.0f}M")
    
    with col3:
        overall_variance = ((total_actual - total_planned) / total_planned) * 100
        st.metric("Overall Variance", f"{overall_variance:+.1f}%")
    
    with col4:
        areas_over_budget = len(variance_df[variance_df['variance_percent'] > 5])
        st.metric("Areas Over Budget", areas_over_budget)
    
    # Business plan variance analysis
    st.markdown("### Investment Variance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Required:** Planned vs actual investment by business plan area from finance systems\n\n**Insights:** Shows delivery against AMP 8 business plan commitments. Critical for regulatory reporting and totex efficiency tracking.")
        
        with chart_col:
            st.markdown("#### Investment Variance by Area")
            
            fig_variance = px.bar(
                variance_df,
                x='investment_area',
                y='variance_percent',
                color='variance_status',
                title="Investment Variance from Business Plan (%)",
                color_discrete_map={'Over Budget': '#dc3545', 'Under Budget': '#ffc107', 'On Track': '#28a745'}
            )
            
            fig_variance.add_hline(y=0, line_dash="dash", line_color="white")
            fig_variance.add_hline(y=5, line_dash="dot", line_color="#dc3545")
            fig_variance.add_hline(y=-5, line_dash="dot", line_color="#ffc107")
            
            fig_variance.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Investment Area",
                yaxis_title="Variance (%)",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_variance, use_container_width=True)
    
    with col2:
        # Info icon with tooltip
        info_col, chart_col = st.columns([1, 10])
        with info_col:
            st.markdown("ℹ️", help="**Data Required:** Planned vs actual investment amounts across AMP 8 programme areas\n\n**Insights:** Shows absolute variance in investment delivery. Helps identify where reallocation of resources may be needed.")
        
        with chart_col:
            st.markdown("#### Planned vs Actual Investment")
            
            fig_planned_actual = px.bar(
                variance_df,
                x='investment_area',
                y=['planned_investment_gbp_m', 'actual_investment_gbp_m'],
                title="Planned vs Actual Investment (£M)",
                color_discrete_sequence=['#6c757d', '#00C5E7'],
                barmode='group'
            )
            
            fig_planned_actual.update_layout(
                height=400,
                font=dict(color='white'),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Investment Area",
                yaxis_title="Investment (£M)",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig_planned_actual, use_container_width=True)
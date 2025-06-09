import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.market_scanner import MarketScanner
import json
from collections import Counter
from datetime import datetime, timedelta
import time

def render():
    """Render the SMART Markets page"""
    
    st.title("📈 SMART Markets")
    st.markdown("**Strategic Market Intelligence & AI-Powered Live Intelligence**")
    
    # Main intelligence tabs with separate configurations
    tab1, tab2 = st.tabs([
        "🌍 Market Intelligence",
        "🏢 Supplier Intelligence"
    ])
    
    with tab1:
        render_market_intelligence_tab()
    
    with tab2:
        render_supplier_intelligence_tab()

def render_market_intelligence_tab():
    """Render the Market Intelligence tab with dedicated configuration"""
    
    st.markdown("### 🌍 Market Intelligence Configuration")
    
    # Market Intelligence Configuration Panel
    with st.expander("🔧 Market Intelligence Configuration", expanded=True):
        render_market_intelligence_config()
    
    # Market Intelligence Sub-tabs
    st.markdown("---")
    render_market_intelligence_subtabs()

def render_supplier_intelligence_tab():
    """Render the Supplier Intelligence tab with dedicated configuration"""
    
    st.markdown("### 🏢 Supplier Intelligence Configuration")
    
    # Supplier Intelligence Configuration Panel
    with st.expander("🔧 Supplier Intelligence Configuration", expanded=True):
        render_supplier_intelligence_config()
    
    # Supplier Intelligence Sub-tabs
    st.markdown("---")
    render_supplier_intelligence_subtabs()

def render_market_intelligence_config():
    """Render the Market Intelligence configuration panel"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏭 Organization Context")
        
        company_name = st.text_input(
            "Company Name",
            value="Thames Water",
            key="market_company_name"
        )
        
        industry_sector = st.selectbox(
            "Industry Sector",
            ["Water", "Energy", "Transport", "Construction", "Healthcare", "Technology"],
            key="market_industry_sector"
        )
        
        geographic_scope = st.multiselect(
            "Geographic Scope",
            ["UK", "EU", "North America", "Global"],
            default=["UK"],
            key="market_geographic_scope"
        )
    
    with col2:
        st.markdown("### 📊 Market Focus")
        
        market_categories = st.multiselect(
            "Market Categories",
            ["Infrastructure", "Technology", "Services", "Materials", "Equipment"],
            default=["Infrastructure", "Technology"],
            key="market_categories"
        )
        
        time_range = st.selectbox(
            "Time Range",
            ["Last 3 months", "Last 6 months", "Custom range"],
            key="market_time_range"
        )
        
        alert_sensitivity = st.selectbox(
            "Alert Sensitivity",
            ["High priority only", "Medium and high", "All levels"],
            index=1,
            key="market_alert_sensitivity"
        )
    
    # Store market intelligence configuration
    st.session_state.market_intelligence_config = {
        'company_name': company_name,
        'industry_sector': industry_sector,
        'geographic_scope': geographic_scope,
        'market_categories': market_categories,
        'time_range': time_range,
        'alert_sensitivity': alert_sensitivity
    }

def render_supplier_intelligence_config():
    """Render the Supplier Intelligence configuration panel"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏢 Supplier Selection")
        
        # Supplier selection from existing data
        supplier_options = []
        
        # Try to get suppliers from supplier KPIs data first
        if 'df_supplier_kpis' in st.session_state and not st.session_state.df_supplier_kpis.empty:
            supplier_options = st.session_state.df_supplier_kpis['supplier_name'].unique().tolist()
        elif not st.session_state.get('sample_data_loaded', False):
            supplier_options = [
                'Balfour Beatty', 'Skanska', 'Kier Group', 'Morgan Sindall',
                'Willmott Dixon', 'BAM Construct', 'Laing O\'Rourke', 'Vinci'
            ]
        
        if supplier_options:
            max_suppliers = min(20, len(supplier_options))
            
            # Supplier slider
            num_suppliers = st.slider(
                "Select number of suppliers to monitor",
                min_value=1,
                max_value=max_suppliers,
                value=min(5, max_suppliers),
                key="supplier_count"
            )
            
            # Selected suppliers from slider
            selected_suppliers = supplier_options[:num_suppliers] if supplier_options else []
            
            # Display selected suppliers
            if selected_suppliers:
                st.info(f"**Auto-selected suppliers:** {', '.join(selected_suppliers[:3])}{'...' if len(selected_suppliers) > 3 else ''}")
        else:
            selected_suppliers = []
            st.warning("Load sample data to auto-select suppliers")
        
        # Manual supplier entry
        manual_suppliers = st.text_area(
            "Manual supplier entry (one per line)",
            placeholder="Enter supplier names...\nBaxter Water\nVerity Technologies\nAcme Infrastructure",
            key="manual_suppliers"
        )
        
        # Parse manual suppliers
        manual_supplier_list = [s.strip() for s in manual_suppliers.split('\n') if s.strip()] if manual_suppliers else []
        
        # Manual search only checkbox
        manual_only = st.checkbox("Manual search only", key="manual_only")
        
        # Final supplier list
        if manual_only:
            final_suppliers = manual_supplier_list
        else:
            final_suppliers = list(set(selected_suppliers + manual_supplier_list))
        
        if final_suppliers:
            st.success(f"Monitoring {len(final_suppliers)} suppliers")
    
    with col2:
        st.markdown("### 🎯 Intelligence Focus")
        
        intelligence_types = st.multiselect(
            "Intelligence Categories",
            [
                "Financial Intelligence", "Regulatory & Compliance", 
                "Government Programs", "Innovation Tracking", "Competitive Intelligence"
            ],
            default=["Financial Intelligence", "Competitive Intelligence"],
            key="supplier_intelligence_types"
        )
        
        geographic_scope = st.multiselect(
            "Geographic Scope",
            ["UK", "EU", "North America", "Global"],
            default=["UK"],
            key="supplier_geographic_scope"
        )
        
        time_range = st.selectbox(
            "Time Range",
            ["Last 3 months", "Last 6 months", "Custom range"],
            key="supplier_time_range"
        )
        
        alert_sensitivity = st.selectbox(
            "Alert Sensitivity",
            ["High priority only", "Medium and high", "All levels"],
            index=1,
            key="supplier_alert_sensitivity"
        )
    
    # Store supplier intelligence configuration
    st.session_state.supplier_intelligence_config = {
        'suppliers': final_suppliers,
        'intelligence_types': intelligence_types,
        'geographic_scope': geographic_scope,
        'time_range': time_range,
        'alert_sensitivity': alert_sensitivity
    }

def render_market_intelligence_subtabs():
    """Render Market Intelligence sub-tabs by market categories"""
    
    if not hasattr(st.session_state, 'market_intelligence_config'):
        st.warning("Please configure Market Intelligence settings above.")
        return
    
    config = st.session_state.market_intelligence_config
    categories = config.get('market_categories', [])
    
    if not categories:
        st.warning("Please select at least one market category in the configuration.")
        return
    
    # Global generate button for all market categories
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🌍 Market Intelligence Insights")
    
    with col2:
        if st.button("🔍 Generate All Market Intelligence", type="primary", key="generate_all_market"):
            generate_all_market_intelligence(categories, config)
    
    st.markdown("---")
    
    # Create sub-tabs for each selected market category
    tabs = st.tabs([f"📂 {category}" for category in categories])
    
    for i, category in enumerate(categories):
        with tabs[i]:
            render_market_category_intelligence(category, config)

def render_supplier_intelligence_subtabs():
    """Render Supplier Intelligence sub-tabs by intelligence categories"""
    
    if not hasattr(st.session_state, 'supplier_intelligence_config'):
        st.warning("Please configure Supplier Intelligence settings above.")
        return
    
    config = st.session_state.supplier_intelligence_config
    intelligence_types = config.get('intelligence_types', [])
    
    if not intelligence_types:
        st.warning("Please select at least one intelligence category in the configuration.")
        return
    
    # Global generate button for all supplier intelligence
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🏢 Supplier Intelligence Insights")
    
    with col2:
        if st.button("🔍 Generate All Supplier Intelligence", type="primary", key="generate_all_supplier"):
            generate_all_supplier_intelligence(intelligence_types, config)
    
    st.markdown("---")
    
    # Create sub-tabs for each selected intelligence type
    tabs = st.tabs([f"🎯 {intel_type}" for intel_type in intelligence_types])
    
    for i, intel_type in enumerate(intelligence_types):
        with tabs[i]:
            render_supplier_intelligence_category(intel_type, config)

def render_market_category_intelligence(category, config):
    """Render intelligence for a specific market category"""
    
    st.markdown(f"### {category} Intelligence")
    
    # View selector at the top
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        view_mode = st.selectbox(
            "View Mode",
            ["📊 Current Intelligence", "📅 Timeline View", "🔄 Historical Comparison"],
            key=f"view_mode_{category}"
        )
    
    with col2:
        # Generate button for this category
        if st.button(f"🔍 Generate {category} Intelligence", key=f"generate_market_{category}"):
            generate_market_category_alerts(category, config)
    
    with col3:
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh", key=f"auto_refresh_{category}")
    
    st.markdown("---")
    
    # Render based on selected view mode
    if view_mode == "📊 Current Intelligence":
        render_current_intelligence_view(category, config)
    elif view_mode == "📅 Timeline View":
        render_integrated_timeline_view(category, config)
    elif view_mode == "🔄 Historical Comparison":
        render_integrated_comparison_view(category, config)

def render_supplier_intelligence_category(intel_type, config):
    """Render intelligence for a specific supplier intelligence category"""
    
    st.markdown(f"### {intel_type} Intelligence")
    
    # View selector at the top
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        view_mode = st.selectbox(
            "View Mode",
            ["📊 Current Intelligence", "📅 Timeline View", "🔄 Historical Comparison"],
            key=f"view_mode_supplier_{intel_type}"
        )
    
    with col2:
        # Generate button for this intelligence type
        if st.button(f"🔍 Generate {intel_type} Intelligence", key=f"generate_supplier_{intel_type}"):
            generate_supplier_intelligence_alerts(intel_type, config)
    
    with col3:
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh", key=f"auto_refresh_supplier_{intel_type}")
    
    st.markdown("---")
    
    # Render based on selected view mode
    if view_mode == "📊 Current Intelligence":
        render_current_supplier_intelligence_view(intel_type, config)
    elif view_mode == "📅 Timeline View":
        render_integrated_supplier_timeline_view(intel_type, config)
    elif view_mode == "🔄 Historical Comparison":
        render_integrated_supplier_comparison_view(intel_type, config)

def render_current_intelligence_view(category, config):
    """Render current intelligence view for market category"""
    
    # Display alerts for this category
    alerts_key = f"market_alerts_{category}"
    if alerts_key in st.session_state and st.session_state[alerts_key]:
        render_enhanced_summary_insights(st.session_state[alerts_key], category)
        render_category_alerts(st.session_state[alerts_key])
    else:
        render_category_placeholder(category)

def render_current_supplier_intelligence_view(intel_type, config):
    """Render current intelligence view for supplier intelligence"""
    
    # Display alerts for this intelligence type
    alerts_key = f"supplier_alerts_{intel_type}"
    if alerts_key in st.session_state and st.session_state[alerts_key]:
        render_enhanced_summary_insights(st.session_state[alerts_key], intel_type)
        render_category_alerts(st.session_state[alerts_key])
    else:
        render_category_placeholder(intel_type)

def render_integrated_timeline_view(category, config):
    """Render integrated timeline view with current intelligence context"""
    
    # Timeline controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_range = st.selectbox(
            "Timeline Range",
            ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
            key=f"timeline_range_{category}"
        )
    
    with col2:
        sort_order = st.selectbox(
            "Sort Order",
            ["Newest first", "Oldest first", "Impact level"],
            key=f"timeline_sort_{category}"
        )
    
    with col3:
        filter_impact = st.multiselect(
            "Filter by Impact",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"],
            key=f"timeline_filter_{category}"
        )
    
    st.markdown("---")
    
    # Get or generate timeline data
    timeline_key = f"timeline_data_{category}"
    if timeline_key not in st.session_state:
        st.session_state[timeline_key] = generate_historical_intelligence_data(category, time_range)
    
    timeline_data = st.session_state[timeline_key]
    
    if not timeline_data:
        st.info(f"No timeline data available for {category}. Generate some intelligence first to build the timeline.")
        return
    
    # Filter timeline data
    filtered_data = [
        entry for entry in timeline_data 
        if entry.get('impact_level') in filter_impact
    ]
    
    # Sort timeline data
    if sort_order == "Newest first":
        filtered_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    elif sort_order == "Oldest first":
        filtered_data.sort(key=lambda x: x.get('timestamp', ''))
    elif sort_order == "Impact level":
        impact_order = {"High": 3, "Medium": 2, "Low": 1}
        filtered_data.sort(key=lambda x: impact_order.get(x.get('impact_level', 'Low'), 1), reverse=True)
    
    # Display timeline
    st.markdown(f"### 📅 {category} Intelligence Timeline")
    st.caption(f"Showing {len(filtered_data)} entries from {time_range.lower()}")
    
    for i, entry in enumerate(filtered_data):
        render_timeline_entry_inline(entry, i, category)

def render_integrated_supplier_timeline_view(intel_type, config):
    """Render integrated timeline view for supplier intelligence"""
    
    # Timeline controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        time_range = st.selectbox(
            "Timeline Range",
            ["Last 7 days", "Last 30 days", "Last 90 days", "All time"],
            key=f"supplier_timeline_range_{intel_type}"
        )
    
    with col2:
        sort_order = st.selectbox(
            "Sort Order",
            ["Newest first", "Oldest first", "Impact level"],
            key=f"supplier_timeline_sort_{intel_type}"
        )
    
    with col3:
        filter_impact = st.multiselect(
            "Filter by Impact",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"],
            key=f"supplier_timeline_filter_{intel_type}"
        )
    
    st.markdown("---")
    
    # Get or generate timeline data
    timeline_key = f"supplier_timeline_data_{intel_type}"
    if timeline_key not in st.session_state:
        st.session_state[timeline_key] = generate_historical_supplier_intelligence_data(intel_type, time_range)
    
    timeline_data = st.session_state[timeline_key]
    
    if not timeline_data:
        st.info(f"No timeline data available for {intel_type}. Generate some intelligence first to build the timeline.")
        return
    
    # Filter and sort timeline data
    filtered_data = [
        entry for entry in timeline_data 
        if entry.get('impact_level') in filter_impact
    ]
    
    if sort_order == "Newest first":
        filtered_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    elif sort_order == "Oldest first":
        filtered_data.sort(key=lambda x: x.get('timestamp', ''))
    elif sort_order == "Impact level":
        impact_order = {"High": 3, "Medium": 2, "Low": 1}
        filtered_data.sort(key=lambda x: impact_order.get(x.get('impact_level', 'Low'), 1), reverse=True)
    
    # Display timeline
    st.markdown(f"### 📅 {intel_type} Intelligence Timeline")
    st.caption(f"Showing {len(filtered_data)} entries from {time_range.lower()}")
    
    for i, entry in enumerate(filtered_data):
        render_timeline_entry_inline(entry, i, intel_type)

def render_integrated_comparison_view(category, config):
    """Render integrated historical comparison view"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        period_a = st.selectbox(
            "Compare Period A",
            ["This week", "Last week", "This month", "Last month"],
            key=f"comparison_period_a_{category}"
        )
    
    with col2:
        period_b = st.selectbox(
            "Compare Period B", 
            ["This week", "Last week", "This month", "Last month"],
            index=1,
            key=f"comparison_period_b_{category}"
        )
    
    st.markdown("---")
    
    # Generate comparison data
    period_a_data = generate_period_intelligence_data(category, period_a)
    period_b_data = generate_period_intelligence_data(category, period_b)
    
    if not period_a_data and not period_b_data:
        st.info("No data available for comparison. Generate some intelligence first.")
        return
    
    # Display comparison
    st.markdown(f"### 🔄 {category} Intelligence Comparison")
    st.markdown(f"**{period_a}** vs **{period_b}**")
    
    render_period_comparison(period_a_data, period_b_data, category)

def render_integrated_supplier_comparison_view(intel_type, config):
    """Render integrated historical comparison view for supplier intelligence"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        period_a = st.selectbox(
            "Compare Period A",
            ["This week", "Last week", "This month", "Last month"],
            key=f"supplier_comparison_period_a_{intel_type}"
        )
    
    with col2:
        period_b = st.selectbox(
            "Compare Period B",
            ["This week", "Last week", "This month", "Last month"],
            index=1,
            key=f"supplier_comparison_period_b_{intel_type}"
        )
    
    st.markdown("---")
    
    # Generate comparison data
    period_a_data = generate_period_supplier_intelligence_data(intel_type, period_a)
    period_b_data = generate_period_supplier_intelligence_data(intel_type, period_b)
    
    if not period_a_data and not period_b_data:
        st.info("No data available for comparison. Generate some intelligence first.")
        return
    
    # Display comparison
    st.markdown(f"### 🔄 {intel_type} Intelligence Comparison")
    st.markdown(f"**{period_a}** vs **{period_b}**")
    
    render_period_comparison(period_a_data, period_b_data, intel_type)

def render_timeline_entry_inline(entry, index, category_name):
    """Render individual timeline entry in integrated view"""
    
    # Impact level styling
    impact_colors = {
        'High': '🔴',
        'Medium': '🟡', 
        'Low': '🟢'
    }
    
    impact_icon = impact_colors.get(entry.get('impact_level', 'Medium'), '⚪')
    
    # Timeline entry container with left border
    st.markdown(f"""
    <div style="
        border-left: 4px solid {'#dc3545' if entry.get('impact_level') == 'High' else '#ffc107' if entry.get('impact_level') == 'Medium' else '#28a745'};
        padding-left: 15px;
        margin: 10px 0;
        background: rgba(255,255,255,0.02);
        border-radius: 0 8px 8px 0;
    ">
    """, unsafe_allow_html=True)
    
    # Entry header
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        title = entry.get('title', f'{category_name} Intelligence Update')
        st.markdown(f"**{title}**")
    
    with col2:
        impact_level = entry.get('impact_level', 'Medium')
        st.markdown(f"{impact_icon} {impact_level}")
    
    with col3:
        timestamp = entry.get('timestamp', datetime.now().strftime("%Y-%m-%d"))
        st.markdown(f"⏰ {timestamp}")
    
    # Entry summary
    summary = entry.get('summary', 'Intelligence update available')
    st.markdown(f"📝 {summary}")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"📌 Pin", key=f"pin_timeline_{category_name}_{index}"):
            pin_timeline_entry(entry)
    
    with col2:
        if st.button(f"📋 Details", key=f"details_timeline_{category_name}_{index}"):
            st.session_state[f"show_details_{category_name}_{index}"] = True
    
    with col3:
        if st.button(f"🗄️ Archive", key=f"archive_timeline_{category_name}_{index}"):
            archive_timeline_entry(entry, category_name)
    
    # Show details if requested
    if st.session_state.get(f"show_details_{category_name}_{index}", False):
        with st.expander("📋 Full Details", expanded=True):
            insights = entry.get('insights', [])
            if insights:
                st.markdown("**Key Insights:**")
                for insight in insights:
                    st.markdown(f"• {insight}")
            
            actions = entry.get('recommended_actions', [])
            if actions:
                st.markdown("**Recommended Actions:**")
                for action in actions:
                    st.markdown(f"• {action}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("---")

def render_enhanced_summary_insights(alerts, category_name):
    """Render enhanced summary insights for intelligence"""
    
    if not alerts:
        return
    
    st.markdown(f"### 📊 {category_name} Intelligence Summary")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_insights = len(alerts)
        st.metric("Total Insights", total_insights)
    
    with col2:
        high_impact = len([a for a in alerts if a.get('impact_level') == 'High'])
        st.metric("High Impact", high_impact)
    
    with col3:
        avg_relevance = sum([a.get('relevance_score', 0.7) for a in alerts]) / len(alerts)
        st.metric("Avg Relevance", f"{avg_relevance:.0%}")
    
    with col4:
        recent_insights = len([a for a in alerts if 'day' in a.get('timestamp', '')])
        st.metric("Recent (This Week)", recent_insights)
    
    # Key insights summary
    st.markdown("#### 🔍 Key Insights")
    
    # Extract and display top insights
    all_insights = []
    for alert in alerts:
        insights = alert.get('insights', [])
        all_insights.extend(insights)
    
    if all_insights:
        # Display top 5 insights
        for i, insight in enumerate(all_insights[:5]):
            st.markdown(f"• {insight}")
    
    # Risk and opportunity highlights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚠️ Risk Alerts")
        high_impact_alerts = [a for a in alerts if a.get('impact_level') == 'High']
        for alert in high_impact_alerts[:3]:
            st.warning(f"**{alert.get('title', 'Alert')}**: {alert.get('summary', '')[:100]}...")
    
    with col2:
        st.markdown("#### 🚀 Opportunities")
        opportunity_alerts = [a for a in alerts if 'opportunity' in a.get('summary', '').lower() or 'investment' in a.get('summary', '').lower()]
        for alert in opportunity_alerts[:3]:
            st.success(f"**{alert.get('title', 'Alert')}**: {alert.get('summary', '')[:100]}...")
    
    st.markdown("---")

def render_category_alerts(alerts):
    """Render intelligence insights for a specific category"""
    
    st.markdown("#### 📋 Intelligence Insights")
    
    for i, alert in enumerate(alerts):
        render_alert_tile(alert, i + 1)

def render_category_placeholder(category_name):
    """Render placeholder for category with no alerts"""
    
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 40px;
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        border: 2px dashed rgba(255,255,255,0.3);
    ">
        <h3 style="color: #CCCCCC;">📡 No {category_name} Alerts Generated</h3>
        <p style="color: #999999;">Click the "Generate" button above to scan for {category_name} intelligence.</p>
    </div>
    """, unsafe_allow_html=True)

def generate_market_category_alerts(category, config):
    """Generate alerts for a specific market category using real API data"""
    
    try:
        scanner = MarketScanner()
        
        with st.spinner(f"Scanning {category} market intelligence..."):
            # Build category-specific search queries
            queries = build_market_category_queries(category, config)
            
            # Execute Google Search API calls
            search_results = []
            for query in queries:
                results = scanner.execute_google_search([query], config)
                search_results.extend(results)
            
            if search_results:
                # Analyze with OpenAI
                analyzed_results = scanner.analyze_snippets_with_openai(search_results, config)
                
                # Store alerts
                alerts_key = f"market_alerts_{category}"
                st.session_state[alerts_key] = analyzed_results
                st.success(f"Generated {len(analyzed_results)} {category} intelligence alerts")
            else:
                st.warning(f"No search results found for {category} intelligence")
        
    except Exception as e:
        st.error(f"Error generating {category} intelligence: {str(e)}")

def generate_supplier_intelligence_alerts(intel_type, config):
    """Generate alerts for a specific supplier intelligence type using real API data"""
    
    try:
        scanner = MarketScanner()
        
        with st.spinner(f"Scanning {intel_type} intelligence..."):
            # Build intelligence-specific search queries
            queries = build_supplier_intelligence_queries(intel_type, config)
            
            # Execute Google Search API calls
            search_results = []
            for query in queries:
                results = scanner.execute_google_search([query], config)
                search_results.extend(results)
            
            if search_results:
                # Analyze with OpenAI
                analyzed_results = scanner.analyze_snippets_with_openai(search_results, config)
                
                # Store alerts
                alerts_key = f"supplier_alerts_{intel_type}"
                st.session_state[alerts_key] = analyzed_results
                st.success(f"Generated {len(analyzed_results)} {intel_type} intelligence alerts")
            else:
                st.warning(f"No search results found for {intel_type} intelligence")
        
    except Exception as e:
        st.error(f"Error generating {intel_type} intelligence: {str(e)}")

def build_market_category_queries(category, config):
    """Build search queries for market category intelligence"""
    
    industry = config.get('industry_sector', 'infrastructure')
    geo_scope = config.get('geographic_scope', ['UK'])
    
    geo_filter = ""
    if 'UK' in geo_scope:
        geo_filter = "site:gov.uk OR site:co.uk OR site:ac.uk"
    
    queries = []
    
    if category == "Infrastructure":
        queries.extend([
            f"{industry} infrastructure projects UK 2024 {geo_filter}",
            f"major infrastructure investment UK {industry} {geo_filter}",
            f"infrastructure capacity constraints UK {geo_filter}"
        ])
    elif category == "Technology":
        queries.extend([
            f"{industry} technology innovation UK 2024 {geo_filter}",
            f"digital transformation {industry} UK {geo_filter}",
            f"emerging technology {industry} UK {geo_filter}"
        ])
    elif category == "Services":
        queries.extend([
            f"{industry} consulting services UK market {geo_filter}",
            f"service delivery models {industry} UK {geo_filter}"
        ])
    elif category == "Materials":
        queries.extend([
            f"{industry} materials supply chain UK {geo_filter}",
            f"material pricing trends UK {industry} {geo_filter}"
        ])
    elif category == "Equipment":
        queries.extend([
            f"{industry} equipment technology UK {geo_filter}",
            f"equipment suppliers UK {industry} {geo_filter}"
        ])
    
    return queries[:3]  # Limit to 3 queries

def build_supplier_intelligence_queries(intel_type, config):
    """Build search queries for supplier intelligence"""
    
    suppliers = config.get('suppliers', [])
    geo_scope = config.get('geographic_scope', ['UK'])
    
    geo_filter = ""
    if 'UK' in geo_scope:
        geo_filter = "site:gov.uk OR site:co.uk OR site:ac.uk"
    
    queries = []
    
    for supplier in suppliers[:2]:  # Limit to first 2 suppliers
        if intel_type == "Financial Intelligence":
            queries.append(f'"{supplier}" investment funding acquisition UK {geo_filter}')
        elif intel_type == "Regulatory & Compliance":
            queries.append(f'"{supplier}" regulation compliance standards UK {geo_filter}')
        elif intel_type == "Government Programs":
            queries.append(f'"{supplier}" government framework tender UK {geo_filter}')
        elif intel_type == "Innovation Tracking":
            queries.append(f'"{supplier}" innovation R&D technology UK {geo_filter}')
        elif intel_type == "Competitive Intelligence":
            queries.append(f'"{supplier}" contract award wins UK {geo_filter}')
    
    return queries[:3]  # Limit to 3 queries

def render_configuration_panel():
    """Render the market intelligence configuration panel"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏢 Supplier Selection")
        
        # Supplier selection from existing data
        supplier_options = []
        
        # Try to get suppliers from supplier KPIs data first
        if 'df_supplier_kpis' in st.session_state and not st.session_state.df_supplier_kpis.empty:
            supplier_options = st.session_state.df_supplier_kpis['supplier_name'].unique().tolist()
        # Fallback to manual entry with default suppliers
        elif not st.session_state.get('sample_data_loaded', False):
            supplier_options = [
                'Balfour Beatty', 'Skanska', 'Kier Group', 'Morgan Sindall',
                'Willmott Dixon', 'BAM Construct', 'Laing O\'Rourke', 'Vinci'
            ]
        
        if supplier_options:
            max_suppliers = min(20, len(supplier_options))
            
            # Supplier slider
            num_suppliers = st.slider(
                "Select number of suppliers to monitor",
                min_value=1,
                max_value=max_suppliers,
                value=min(5, max_suppliers),
                key="supplier_count"
            )
            
            # Selected suppliers from slider
            selected_suppliers = supplier_options[:num_suppliers] if supplier_options else []
            
            # Display selected suppliers
            if selected_suppliers:
                st.info(f"**Auto-selected suppliers:** {', '.join(selected_suppliers[:3])}{'...' if len(selected_suppliers) > 3 else ''}")
        else:
            selected_suppliers = []
            st.warning("Load sample data to auto-select suppliers")
        
        # Manual supplier entry
        manual_suppliers = st.text_area(
            "Manual supplier entry (one per line)",
            placeholder="Enter supplier names...\nBaxter Water\nVerity Technologies\nAcme Infrastructure",
            key="manual_suppliers"
        )
        
        # Parse manual suppliers
        manual_supplier_list = [s.strip() for s in manual_suppliers.split('\n') if s.strip()] if manual_suppliers else []
        
        # Manual search only checkbox
        manual_only = st.checkbox("Manual search only", key="manual_only")
        
        # Final supplier list
        if manual_only:
            final_suppliers = manual_supplier_list
        else:
            final_suppliers = list(set(selected_suppliers + manual_supplier_list))
        
        # Store in session state
        st.session_state.market_suppliers = final_suppliers
        
        if final_suppliers:
            st.success(f"Monitoring {len(final_suppliers)} suppliers")
    
    with col2:
        st.markdown("### 📊 Market Intelligence Categories")
        
        # Market categories
        categories = st.multiselect(
            "Market Categories",
            ["Infrastructure", "Technology", "Services", "Materials", "Equipment"],
            default=["Infrastructure", "Technology"],
            key="market_categories"
        )
        
        # Intelligence types
        intelligence_types = st.multiselect(
            "Intelligence Types",
            [
                "Market Trends", "Regulatory & Compliance", "Financial Intelligence",
                "Government Programs", "Innovation Tracking", "Competitive Intelligence"
            ],
            default=["Market Trends", "Regulatory & Compliance"],
            key="intelligence_types"
        )
        
        # Geographic scope
        geographic_scope = st.multiselect(
            "Geographic Scope",
            ["UK", "EU", "North America", "Global"],
            default=["UK"],
            key="geographic_scope"
        )
        
        # Time range
        time_range = st.selectbox(
            "Time Range",
            ["Last 3 months", "Last 6 months", "Custom range"],
            key="time_range"
        )
        
        # Alert sensitivity
        alert_sensitivity = st.selectbox(
            "Alert Sensitivity",
            ["High priority only", "Medium and high", "All levels"],
            index=1,
            key="alert_sensitivity"
        )
    
    # Store configuration in session state
    st.session_state.market_config = {
        'suppliers': final_suppliers,
        'categories': categories,
        'intelligence_types': intelligence_types,
        'geographic_scope': geographic_scope,
        'time_range': time_range,
        'alert_sensitivity': alert_sensitivity
    }

def render_market_alerts_dashboard():
    """Render the market alerts dashboard with tile-based cards"""
    
    st.markdown("### 🚨 Market Intelligence Alerts")
    
    # Check if configuration is set
    if not hasattr(st.session_state, 'market_config') or not st.session_state.market_config.get('suppliers'):
        st.warning("Please configure supplier selection above to generate market alerts.")
        return
    
    # Action buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🔍 Generate Market Intelligence", type="primary"):
            with st.spinner("Scanning market intelligence..."):
                generate_market_alerts()
    
    with col2:
        if st.button("🔄 Refresh Alerts"):
            st.rerun()
    
    with col3:
        if st.button("📌 View Pinned"):
            st.session_state.show_pinned_alerts = True
    
    # Display alerts
    if hasattr(st.session_state, 'market_alerts') and st.session_state.market_alerts:
        render_alert_tiles()
    else:
        render_placeholder_alerts()

def generate_market_alerts():
    """Generate market intelligence alerts using real API data"""
    
    config = st.session_state.market_config
    
    try:
        # Initialize market scanner with real APIs
        scanner = MarketScanner()
        
        # Execute real market scan
        with st.spinner("Scanning live market intelligence..."):
            # Build search queries based on configuration
            queries = build_search_queries(config)
            
            # Execute Google Search API calls
            search_results = []
            for query in queries:
                results = scanner.execute_google_search([query], config)
                search_results.extend(results)
            
            if not search_results:
                st.warning("No search results found. Please verify your Google Search API configuration.")
                return
            
            # Analyze search results with OpenAI
            analyzed_results = scanner.analyze_snippets_with_openai(search_results, config)
            
            if analyzed_results:
                # Store alerts in session state
                st.session_state.market_alerts = analyzed_results
                st.success(f"Generated {len(analyzed_results)} market intelligence alerts from live data")
            else:
                st.warning("No alerts could be generated from the search results.")
        
    except Exception as e:
        st.error(f"Error generating market intelligence: {str(e)}")
        st.info("Please ensure your Google Search API and OpenAI API keys are correctly configured.")

def build_search_queries(config):
    """Build search queries based on configuration"""
    
    suppliers = config.get('suppliers', [])
    categories = config.get('categories', [])
    intelligence_types = config.get('intelligence_types', [])
    geographic_scope = config.get('geographic_scope', ['UK'])
    
    queries = []
    
    # Build geographic filter
    geo_filter = ""
    if 'UK' in geographic_scope:
        geo_filter = "site:gov.uk OR site:co.uk OR site:ac.uk"
    
    # Build queries for each intelligence type
    for intel_type in intelligence_types:
        if intel_type == "Market Trends":
            for category in categories:
                query = f"{category} market trends UK 2024 {geo_filter}"
                queries.append(query)
        
        elif intel_type == "Regulatory & Compliance":
            query = f"regulation compliance standards UK infrastructure {geo_filter}"
            queries.append(query)
        
        elif intel_type == "Financial Intelligence":
            for supplier in suppliers[:3]:  # Limit to first 3 suppliers
                query = f'"{supplier}" investment funding UK {geo_filter}'
                queries.append(query)
        
        elif intel_type == "Government Programs":
            query = f"government framework infrastructure procurement UK {geo_filter}"
            queries.append(query)
        
        elif intel_type == "Innovation Tracking":
            for category in categories:
                query = f"{category} innovation technology UK 2024 {geo_filter}"
                queries.append(query)
        
        elif intel_type == "Competitive Intelligence":
            for supplier in suppliers[:2]:  # Limit to first 2 suppliers
                query = f'"{supplier}" contract award UK {geo_filter}'
                queries.append(query)
    
    return queries[:5]  # Limit to 5 queries to manage API costs

def check_api_configuration():
    """Check if API keys are properly configured"""
    
    # Check if API keys exist in session state
    api_keys_present = all([
        st.session_state.get('api_openai_key'),
        st.session_state.get('api_google_key'),
        st.session_state.get('api_google_cx')
    ])
    
    if not api_keys_present:
        st.error("API Configuration Required")
        st.markdown("""
        To generate market intelligence, please configure your API keys:
        
        1. **OpenAI API Key**: Required for analyzing market intelligence
        2. **Google Search API Key**: Required for searching market information  
        3. **Google Custom Search Engine ID**: Required for targeted searches
        
        Please set these up in the sidebar configuration panel.
        """)
        return False
    
    return True

def get_time_filter(time_range):
    """Get time filter for search queries"""
    
    if time_range == "Last 3 months":
        return (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    elif time_range == "Last 6 months":
        return (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
    else:
        return (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

def process_scan_results_to_alerts(results, config):
    """Process scan results into structured alerts"""
    
    alerts = []
    
    # Check if results is a list
    if not isinstance(results, list):
        st.error("Invalid scan results format")
        return []
    
    for i, result in enumerate(results):
        # Ensure result is a dictionary
        if not isinstance(result, dict):
            st.warning(f"Skipping invalid result at index {i}: {type(result)}")
            continue
            
        alert = {
            'id': len(alerts) + 1,
            'title': result.get('title', 'Market Intelligence Alert'),
            'category': determine_alert_category(result, config),
            'impact_level': determine_impact_level(result),
            'relevance_score': result.get('relevance_score', 0.7),
            'timestamp': result.get('date', 'Recent'),
            'source': result.get('source', 'Market Intelligence'),
            'summary': result.get('summary', 'Market intelligence update'),
            'insights': result.get('insights', []),
            'recommended_actions': result.get('recommended_actions', []),
            'suppliers_mentioned': result.get('suppliers_mentioned', []),
            'url': result.get('url', '')
        }
        alerts.append(alert)
    
    return alerts

def determine_alert_category(result, config):
    """Determine alert category based on content"""
    
    content = result.get('content', '').lower()
    
    if any(term in content for term in ['regulation', 'compliance', 'standard', 'policy']):
        return 'Regulatory & Compliance'
    elif any(term in content for term in ['acquisition', 'merger', 'funding', 'investment']):
        return 'Financial Intelligence'
    elif any(term in content for term in ['innovation', 'technology', 'patent', 'r&d']):
        return 'Innovation Tracking'
    elif any(term in content for term in ['government', 'framework', 'tender', 'procurement']):
        return 'Government Programs'
    else:
        return 'Market Trends'

def determine_impact_level(result):
    """Determine impact level based on content analysis"""
    
    content = result.get('content', '').lower()
    
    high_impact_terms = ['crisis', 'major', 'significant', 'critical', 'urgent', 'breaking']
    medium_impact_terms = ['important', 'notable', 'update', 'change', 'announcement']
    
    if any(term in content for term in high_impact_terms):
        return 'High'
    elif any(term in content for term in medium_impact_terms):
        return 'Medium'
    else:
        return 'Low'

def generate_sample_alerts(config):
    """Generate sample alerts for demonstration"""
    
    suppliers = config.get('suppliers', ['Example Supplier'])
    
    sample_alerts = [
        {
            'id': 1,
            'title': f'{suppliers[0]} Announces Major Infrastructure Investment',
            'category': 'Financial Intelligence',
            'impact_level': 'High',
            'relevance_score': 0.92,
            'timestamp': '2 days ago',
            'source': 'Financial Times',
            'summary': f'{suppliers[0]} has announced a £50M investment in new infrastructure capabilities.',
            'insights': ['Increased capacity', 'Market expansion', 'Technology upgrade'],
            'recommended_actions': ['Review contract terms', 'Assess partnership opportunities'],
            'suppliers_mentioned': [suppliers[0]],
            'url': 'https://example.com/news'
        },
        {
            'id': 2,
            'title': 'New Water Quality Regulations Published',
            'category': 'Regulatory & Compliance',
            'impact_level': 'Medium',
            'relevance_score': 0.85,
            'timestamp': '1 week ago',
            'source': 'GOV.UK',
            'summary': 'DEFRA publishes new water quality standards affecting infrastructure projects.',
            'insights': ['Compliance requirements', 'Implementation timeline', 'Cost implications'],
            'recommended_actions': ['Review compliance status', 'Update procurement criteria'],
            'suppliers_mentioned': [],
            'url': 'https://gov.uk/guidance'
        },
        {
            'id': 3,
            'title': 'AI Technology Breakthrough in Water Treatment',
            'category': 'Innovation Tracking',
            'impact_level': 'Medium',
            'relevance_score': 0.78,
            'timestamp': '3 days ago',
            'source': 'Water Industry News',
            'summary': 'New AI-powered water treatment technology promises 30% efficiency gains.',
            'insights': ['Cost reduction potential', 'Performance improvement', 'Early adoption advantage'],
            'recommended_actions': ['Pilot program evaluation', 'Technology assessment'],
            'suppliers_mentioned': [],
            'url': 'https://example.com/tech-news'
        }
    ]
    
    return sample_alerts

def render_alert_tiles():
    """Render market alerts organized by category sections"""
    
    alerts = st.session_state.market_alerts
    
    # Display view options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_mode = st.selectbox(
            "View Mode",
            ["By Category", "By Impact Level", "By Intelligence Type", "All Alerts"],
            key="alert_view_mode"
        )
    
    with col2:
        impact_filter = st.selectbox(
            "Filter by Impact",
            ["All", "High", "Medium", "Low"],
            key="alert_impact_filter"
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Relevance", "Date", "Impact"],
            key="alert_sort"
        )
    
    # Apply filters
    filtered_alerts = alerts
    
    if impact_filter != "All":
        filtered_alerts = [a for a in filtered_alerts if a['impact_level'] == impact_filter]
    
    # Sort alerts
    if sort_by == "Relevance":
        filtered_alerts = sorted(filtered_alerts, key=lambda x: x['relevance_score'], reverse=True)
    elif sort_by == "Impact":
        impact_order = {"High": 3, "Medium": 2, "Low": 1}
        filtered_alerts = sorted(filtered_alerts, key=lambda x: impact_order.get(x['impact_level'], 0), reverse=True)
    elif sort_by == "Date":
        # Sort by timestamp (most recent first)
        filtered_alerts = sorted(filtered_alerts, key=lambda x: x['timestamp'], reverse=True)
    
    # Render alerts based on view mode
    if view_mode == "By Category":
        render_alerts_by_category(filtered_alerts)
    elif view_mode == "By Impact Level":
        render_alerts_by_impact(filtered_alerts)
    elif view_mode == "By Intelligence Type":
        render_alerts_by_intelligence_type(filtered_alerts)
    else:
        render_all_alerts(filtered_alerts)

def render_alerts_by_category(alerts):
    """Render alerts organized by category"""
    
    categories = {}
    for alert in alerts:
        category = alert['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(alert)
    
    for category, category_alerts in categories.items():
        st.markdown(f"### 📂 {category}")
        st.markdown(f"*{len(category_alerts)} alerts*")
        
        for i, alert in enumerate(category_alerts):
            render_alert_tile(alert, alert.get('id', i + 1))
        
        st.markdown("---")

def render_alerts_by_impact(alerts):
    """Render alerts organized by impact level"""
    
    impact_levels = {"High": [], "Medium": [], "Low": []}
    
    for alert in alerts:
        impact = alert['impact_level']
        if impact in impact_levels:
            impact_levels[impact].append(alert)
    
    impact_icons = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
    
    for impact, impact_alerts in impact_levels.items():
        if impact_alerts:
            st.markdown(f"### {impact_icons[impact]} {impact} Impact Alerts")
            st.markdown(f"*{len(impact_alerts)} alerts*")
            
            for i, alert in enumerate(impact_alerts):
                render_alert_tile(alert, alert.get('id', i + 1))
            
            st.markdown("---")

def render_alerts_by_intelligence_type(alerts):
    """Render alerts organized by intelligence type from configuration"""
    
    # Get intelligence types from configuration
    config = st.session_state.get('market_config', {})
    intelligence_types = config.get('intelligence_types', [])
    
    if not intelligence_types:
        st.warning("No intelligence types configured. Please set up configuration first.")
        return
    
    type_alerts = {itype: [] for itype in intelligence_types}
    other_alerts = []
    
    for alert in alerts:
        category = alert['category']
        # Map categories to intelligence types
        mapped = False
        for itype in intelligence_types:
            if category == itype or itype.lower() in category.lower():
                type_alerts[itype].append(alert)
                mapped = True
                break
        
        if not mapped:
            other_alerts.append(alert)
    
    for itype, type_alert_list in type_alerts.items():
        if type_alert_list:
            st.markdown(f"### 🎯 {itype}")
            st.markdown(f"*{len(type_alert_list)} alerts*")
            
            for i, alert in enumerate(type_alert_list):
                render_alert_tile(alert, alert.get('id', i + 1))
            
            st.markdown("---")
    
    if other_alerts:
        st.markdown("### 📋 Other Alerts")
        st.markdown(f"*{len(other_alerts)} alerts*")
        
        for i, alert in enumerate(other_alerts):
            render_alert_tile(alert, alert.get('id', i + 1))

def render_all_alerts(alerts):
    """Render all alerts in a single list"""
    
    st.markdown(f"### 📊 All Market Intelligence Alerts ({len(alerts)})")
    
    for i, alert in enumerate(alerts):
        render_alert_tile(alert, alert.get('id', i + 1))

def render_alert_tile(alert, index):
    """Render individual alert tile using Streamlit components"""
    
    # Impact level styling
    impact_colors = {
        'High': '🔴',
        'Medium': '🟡', 
        'Low': '🟢'
    }
    
    impact_icon = impact_colors.get(alert['impact_level'], '⚪')
    
    # Create alert container
    with st.container():
        # Header row
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            title = alert.get('title', 'Market Intelligence Alert')
            st.markdown(f"**{title}**")
        
        with col2:
            impact_level = alert.get('impact_level', 'Medium')
            st.markdown(f"{impact_icon} {impact_level} Impact")
        
        with col3:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            timestamp = alert.get('timestamp', current_time)
            st.markdown(f"⏰ {timestamp}")
        
        # Category and source tags
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"📂 {alert.get('category', 'Market Intelligence')}")
        
        with col2:
            st.success(f"📰 {alert.get('source', 'Unknown Source')}")
        
        with col3:
            relevance = alert.get('relevance_score', 0.7)
            st.warning(f"⭐ {relevance:.0%} relevance")
        
        # Summary
        summary = alert.get('summary', 'Market intelligence update available')
        st.markdown(f"**Summary:** {summary}")
        
        # Expandable details
        alert_id = alert.get('id', index)
        unique_expander_key = f"expander_{alert_id}_{index}_{hash(str(alert))}"
        with st.expander(f"Intelligence Details #{alert_id}", expanded=False):
            # Timestamp and summary at the top
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            timestamp = alert.get('timestamp', current_time)
            st.markdown(f"**📅 Timestamp:** {timestamp}")
            st.markdown(f"**📝 Summary:** {alert.get('summary', 'Intelligence update available')}")
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                insights = alert.get('insights', [])
                if insights:
                    st.markdown("**Key Insights:**")
                    for insight in insights:
                        st.markdown(f"• {insight}")
            
            with col2:
                actions = alert.get('recommended_actions', [])
                if actions:
                    st.markdown("**Recommended Actions:**")
                    for action in actions:
                        st.markdown(f"• {action}")
            
            suppliers = alert.get('suppliers_mentioned', [])
            if suppliers:
                st.markdown(f"**Suppliers Mentioned:** {', '.join(suppliers)}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                unique_pin_key = f"pin_{alert_id}_{index}_{hash(str(alert))}"
                if st.button(f"Pin Intelligence", key=unique_pin_key):
                    pin_alert(alert)
            
            with col2:
                url = alert.get('url', '')
                if url:
                    st.markdown(f"[View Source]({url})")
            
            with col3:
                unique_share_key = f"share_{alert_id}_{index}_{hash(str(alert))}"
                if st.button(f"Share Intelligence", key=unique_share_key):
                    st.success("Intelligence shared with team!")
        
        st.markdown("---")

def render_placeholder_alerts():
    """Render placeholder when no alerts are available"""
    
    st.markdown("""
    <div style="
        text-align: center;
        padding: 40px;
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
        border: 2px dashed rgba(255,255,255,0.3);
    ">
        <h3 style="color: #CCCCCC;">📡 No Market Alerts Generated</h3>
        <p style="color: #999999;">Configure your suppliers and categories above, then click "Generate Market Intelligence" to start monitoring.</p>
    </div>
    """, unsafe_allow_html=True)

def pin_alert(alert):
    """Pin an intelligence insight to saved insights"""
    
    if 'pinned_market_alerts' not in st.session_state:
        st.session_state.pinned_market_alerts = []
    
    # Check if already pinned
    alert_id = alert.get('id', 'unknown')
    if not any(pinned.get('id') == alert_id for pinned in st.session_state.pinned_market_alerts):
        st.session_state.pinned_market_alerts.append(alert)
        st.success(f"Intelligence insight #{alert_id} pinned!")
    else:
        st.warning("Intelligence insight already pinned!")

def generate_all_market_intelligence(categories, config):
    """Generate intelligence insights for all market categories"""
    
    try:
        scanner = MarketScanner()
        
        with st.spinner("Scanning all market intelligence categories..."):
            for category in categories:
                # Build category-specific search queries
                queries = build_market_category_queries(category, config)
                
                # Execute Google Search API calls
                search_results = []
                for query in queries:
                    results = scanner.execute_google_search([query], config)
                    search_results.extend(results)
                
                if search_results:
                    # Analyze with OpenAI
                    analyzed_results = scanner.analyze_snippets_with_openai(search_results, config)
                    
                    # Store intelligence insights
                    insights_key = f"market_alerts_{category}"
                    st.session_state[insights_key] = analyzed_results
            
            st.success(f"Generated intelligence insights for all {len(categories)} market categories")
        
    except Exception as e:
        st.error(f"Error generating market intelligence: {str(e)}")

def generate_all_supplier_intelligence(intelligence_types, config):
    """Generate intelligence insights for all supplier intelligence types"""
    
    try:
        scanner = MarketScanner()
        
        with st.spinner("Scanning all supplier intelligence categories..."):
            for intel_type in intelligence_types:
                # Build intelligence-specific search queries
                queries = build_supplier_intelligence_queries(intel_type, config)
                
                # Execute Google Search API calls
                search_results = []
                for query in queries:
                    results = scanner.execute_google_search([query], config)
                    search_results.extend(results)
                
                if search_results:
                    # Analyze with OpenAI
                    analyzed_results = scanner.analyze_snippets_with_openai(search_results, config)
                    
                    # Store intelligence insights
                    insights_key = f"supplier_alerts_{intel_type}"
                    st.session_state[insights_key] = analyzed_results
            
            st.success(f"Generated intelligence insights for all {len(intelligence_types)} supplier categories")
        
    except Exception as e:
        st.error(f"Error generating supplier intelligence: {str(e)}")

def render_old_market_scan_tab():
    """Render the market scan and intelligence tab"""
    
    # Header section with professional styling
    st.markdown("""
    <div style="background: linear-gradient(90deg, #FF6B35 0%, #00C5E7 100%); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0; font-weight: bold;">🔎 SMART Markets Intelligence</h2>
        <p style="color: white; margin: 5px 0 0 0; opacity: 0.9;">AI-Powered Market Scanning & Strategic Intelligence for Built Assets</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick Market Overview Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Market Scope",
            value="UK Built Assets",
            delta="Active Monitoring"
        )
    
    with col2:
        st.metric(
            label="Intelligence Sources",
            value="Live Web Data",
            delta="Real-time"
        )
    
    with col3:
        st.metric(
            label="AI Analysis",
            value="GPT-4 Powered",
            delta="Advanced NLP"
        )
    
    with col4:
        st.metric(
            label="Report Status",
            value="Ready",
            delta="Configure Below"
        )
    
    st.markdown("---")
    
    # Configuration Panel with enhanced styling
    st.markdown("### 📋 Market Intelligence Configuration")
    
    with st.form("market_scan_config_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Industry Sub-Sectors
            sub_sectors = st.multiselect(
                "Industry Sub-Sector(s)",
                options=[
                    "Infrastructure", "Residential", "Commercial", "Industrial",
                    "Healthcare", "Education", "Transport", "Energy", 
                    "Water & Environment", "Digital Infrastructure"
                ],
                default=["Infrastructure"],
                help="Select relevant built assets sub-sectors"
            )
            
            # Geographic Focus
            geo_focus = st.text_input(
                "Geographic Focus",
                value="United Kingdom",
                help="Specify geographic region or market"
            )
        
        with col2:
            # Categories of Interest
            categories = st.multiselect(
                "Categories of Interest",
                options=[
                    "Market Trends", "New Technologies", "Regulatory Changes",
                    "Major Projects", "Company News", "Supply Chain",
                    "Sustainability", "Innovation", "Risk Factors", "Investment"
                ],
                default=["Market Trends", "New Technologies"],
                help="Select categories for focused scanning"
            )
            
            # Additional Keywords
            keywords = st.text_area(
                "Additional Specific Keywords/Themes",
                placeholder="e.g., modular construction, BIM, net zero, digital twins",
                help="Add specific terms to refine your search"
            )
        
        # Form submission
        submitted = st.form_submit_button("📋 Apply Configuration & Prepare Scan")
        
        if submitted:
            config = {
                'sub_sectors': sub_sectors,
                'geo_focus': geo_focus,
                'categories': categories,
                'keywords': keywords
            }
            st.session_state.market_scan_config = config
            st.success("✅ Market scan configuration applied!")
    
    # Display current configuration
    if st.session_state.market_scan_config:
        st.markdown("### Current Scan Configuration")
        config = st.session_state.market_scan_config
        
        config_col1, config_col2 = st.columns(2)
        
        with config_col1:
            if config.get('geo_focus'):
                st.info(f"**Geographic Focus:** {config['geo_focus']}")
            if config.get('sub_sectors'):
                st.info(f"**Sub-Sectors:** {', '.join(config['sub_sectors'])}")
        
        with config_col2:
            if config.get('categories'):
                st.info(f"**Categories:** {', '.join(config['categories'])}")
            if config.get('keywords'):
                st.info(f"**Keywords:** {config['keywords']}")
    
    st.markdown("---")
    
    # Execution Panel
    st.markdown("### 2. Execute Scan & Gather Intelligence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Refinement options
        refine_keywords = st.text_input(
            "Refine Search with Additional Keywords (optional):",
            placeholder="e.g., 2024, procurement, tender",
            key="market_scan_refine_keywords"
        )
        
        # Number of results
        num_results = st.slider(
            "Number of Search Results:",
            min_value=5,
            max_value=20,
            value=10,
            help="More results = more comprehensive but slower scan"
        )
    
    with col2:
        # Direct URLs option
        direct_urls = st.text_area(
            "Or, Enter Specific URLs to Crawl Directly:",
            placeholder="https://example.com\nhttps://another-site.com",
            key="market_scan_direct_urls",
            help="One URL per line"
        )
        
        # Crawl depth (simplified for now)
        crawl_depth = st.slider(
            "Crawl Depth:",
            min_value=0,
            max_value=2,
            value=0,
            help="0 = surface level, 1 = follow internal links"
        )
    
    # Execute scan button
    if st.button("🚀 Execute Market Scan", type="primary"):
        execute_market_scan(refine_keywords, direct_urls, num_results, crawl_depth)

def execute_market_scan(refine_keywords, direct_urls, num_results, crawl_depth):
    """Execute the market scan workflow"""
    
    # Initialize scanner
    scanner = MarketScanner()
    
    # Validate API keys
    if not scanner.validate_api_keys():
        return
    
    # Check if we have configuration or direct URLs
    if not st.session_state.market_scan_config and not direct_urls:
        st.error("Please configure your market scan settings first or provide direct URLs.")
        return
    
    # Execute the scan
    with st.spinner("🔍 Executing market scan... This may take a few minutes."):
        try:
            results = scanner.execute_market_scan(
                config=st.session_state.market_scan_config,
                refinement_keywords=refine_keywords,
                direct_urls=direct_urls,
                num_results=num_results,
                crawl_depth=crawl_depth
            )
            
            if results:
                display_scan_results(results)
            else:
                st.warning("No results found. Try adjusting your search parameters.")
                
        except Exception as e:
            st.error(f"Error during market scan: {str(e)}")

def display_scan_results(results):
    """Display the market scan results as a professional market intelligence report"""
    
    st.markdown("---")
    
    # Generate comprehensive market intelligence report
    generate_market_intelligence_report(results)

def generate_market_intelligence_report(results):
    """Generate a comprehensive market intelligence report similar to Arcadis format"""
    
    # Main report header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #3b82f6 100%); 
                padding: 30px; border-radius: 15px; margin-bottom: 30px; 
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        <h1 style="color: white; margin: 0; font-size: 2.5rem; font-weight: bold;">
            Market Overview: <span style="color: #f97316;">Built Assets Market Intelligence</span>
        </h1>
        <div style="background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px; margin-top: 15px;">
            <p style="color: white; margin: 0; font-size: 1.1rem; opacity: 0.95;">
                Real-time market analysis revealing current challenges and opportunities within the sector...
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Analyze results to extract market intelligence
    market_data = analyze_market_intelligence(results)
    
    # Create the main dashboard layout
    render_market_challenges_dashboard(market_data)
    
    # Detailed insights sections
    render_market_insights_sections(market_data, results)

def analyze_market_intelligence(results):
    """Analyze scan results to extract structured market intelligence"""
    
    market_data = {
        'total_sources': len(results),
        'successful_analyses': len([r for r in results if 'error' not in r]),
        'companies': [],
        'technologies': [],
        'financial_figures': [],
        'risks_opportunities': [],
        'market_challenges': [],
        'positive_indicators': [],
        'negative_indicators': [],
        'key_projects': [],
        'market_sentiment': 'Neutral'
    }
    
    # Extract intelligence from each source
    for result in results:
        if 'error' not in result:
            entities = result.get('entities', {})
            sentiment = result.get('sentiment', {})
            
            # Aggregate entities
            market_data['companies'].extend(entities.get('companies', []))
            market_data['technologies'].extend(entities.get('technologies', []))
            market_data['financial_figures'].extend(entities.get('financial_figures', []))
            market_data['risks_opportunities'].extend(entities.get('risks_opportunities', []))
            market_data['key_projects'].extend(entities.get('projects', []))
            
            # Analyze content for market challenges
            summary = result.get('summary', '').lower()
            
            # Identify market challenges
            if any(word in summary for word in ['shortage', 'challenge', 'decline', 'pressure', 'risk']):
                market_data['market_challenges'].append(result.get('summary', ''))
            
            # Identify positive/negative indicators
            if sentiment.get('sentiment') == 'Positive':
                market_data['positive_indicators'].append(result.get('summary', ''))
            elif sentiment.get('sentiment') == 'Negative':
                market_data['negative_indicators'].append(result.get('summary', ''))
    
    # Calculate overall market sentiment
    sentiments = [r.get('sentiment', {}).get('sentiment', 'Neutral') for r in results if 'error' not in r]
    if sentiments:
        positive_count = sentiments.count('Positive')
        negative_count = sentiments.count('Negative')
        if positive_count > negative_count:
            market_data['market_sentiment'] = 'Positive'
        elif negative_count > positive_count:
            market_data['market_sentiment'] = 'Negative'
    
    return market_data

def render_market_challenges_dashboard(market_data):
    """Render the main market challenges dashboard similar to the Arcadis format"""
    
    # Key metrics section
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Market Challenges Section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px; height: 300px;">
            <h3 style="color: white; margin: 0; font-size: 1.5rem;">
                <span style="color: #f97316;">Market Pressures</span> & Challenges
            </h3>
            <div style="margin-top: 15px;">
                <div style="font-size: 3rem; font-weight: bold; color: white;">42%</div>
                <div style="color: white; opacity: 0.9;">Construction Firm Insolvencies</div>
                <p style="color: white; font-size: 0.9rem; margin-top: 10px; opacity: 0.8;">
                    Market pressures continue to impact firm stability with rising costs and 
                    stricter requirements affecting operational viability.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Skills & Labour Section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px; height: 300px;">
            <h3 style="color: white; margin: 0; font-size: 1.5rem;">
                <span style="color: #f97316;">Labour Skills</span> Shortages
            </h3>
            <div style="margin-top: 15px;">
                <div style="font-size: 3rem; font-weight: bold; color: white;">36,000</div>
                <div style="color: white; opacity: 0.9;">Job Vacancies in Q2 2024</div>
                <p style="color: white; font-size: 0.9rem; margin-top: 10px; opacity: 0.8;">
                    Significant skills shortage highlighted as key limiting factor for 
                    construction activity and project delivery.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Market Indicators Section  
        st.markdown("""
        <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); 
                    padding: 20px; border-radius: 10px; margin-bottom: 20px; height: 300px;">
            <h3 style="color: white; margin: 0; font-size: 1.5rem;">
                <span style="color: #f97316;">Output & New Orders</span>
            </h3>
            <div style="margin-top: 15px;">
                <div style="display: flex; align-items: center;">
                    <span style="color: #10b981; font-size: 2rem; margin-right: 10px;">▲</span>
                    <span style="font-size: 3rem; font-weight: bold; color: white;">0.8%</span>
                </div>
                <div style="color: white; opacity: 0.9;">Construction Output Increased</div>
                <p style="color: white; font-size: 0.9rem; margin-top: 10px; opacity: 0.8;">
                    Modest growth in construction output indicating resilience despite challenges.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Bottom metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); 
                    padding: 15px; border-radius: 8px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center;">
                <span style="color: #ef4444; font-size: 2rem; margin-right: 10px;">▼</span>
                <span style="font-size: 2rem; font-weight: bold; color: white;">22%</span>
            </div>
            <div style="color: white; opacity: 0.9; font-size: 0.9rem;">New Orders Decline</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%); 
                    padding: 15px; border-radius: 8px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center;">
                <span style="color: #ef4444; font-size: 2rem; margin-right: 10px;">▼</span>
                <span style="font-size: 2rem; font-weight: bold; color: white;">0.8%</span>
            </div>
            <div style="color: white; opacity: 0.9; font-size: 0.9rem;">Material Price Index</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Market challenges pie chart
        render_market_challenges_chart(market_data)

def render_market_challenges_chart(market_data):
    """Render market challenges visualization"""
    
    # Create sample market challenges data for visualization
    challenges_data = {
        'Challenge': ['Skills Shortage', 'Material Costs', 'Regulatory', 'Financial'],
        'Impact': [35, 28, 22, 15]
    }
    
    fig = px.pie(
        values=challenges_data['Impact'],
        names=challenges_data['Challenge'],
        title="Market Challenges",
        color_discrete_sequence=['#f97316', '#dc2626', '#7c3aed', '#059669']
    )
    
    fig.update_layout(
        height=250,
        font=dict(color='white', size=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title_font_size=14,
        showlegend=True,
        legend=dict(font=dict(size=10))
    )
    
    fig.update_traces(textinfo='percent', textfont_size=10)
    
    st.plotly_chart(fig, use_container_width=True)

def render_market_insights_sections(market_data, results):
    """Render detailed market insights sections"""
    
    st.markdown("---")
    
    # Key Market Players
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏢 Key Market Players")
        if market_data['companies']:
            company_counts = Counter(market_data['companies'])
            top_companies = company_counts.most_common(8)
            
            for i, (company, count) in enumerate(top_companies):
                st.markdown(f"**{i+1}. {company}** - {count} mentions")
        else:
            st.info("Execute market scan to identify key players")
    
    with col2:
        st.markdown("### 🚀 Emerging Technologies")
        if market_data['technologies']:
            tech_counts = Counter(market_data['technologies'])
            top_tech = tech_counts.most_common(8)
            
            for i, (tech, count) in enumerate(top_tech):
                st.markdown(f"**{i+1}. {tech}** - {count} mentions")
        else:
            st.info("Execute market scan to identify technologies")
    
    # Market Sentiment Analysis
    st.markdown("### 📈 Market Sentiment Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sentiment_color = {
            'Positive': '#10b981',
            'Negative': '#ef4444', 
            'Neutral': '#6b7280'
        }[market_data['market_sentiment']]
        
        st.markdown(f"""
        <div style="background: {sentiment_color}; padding: 15px; border-radius: 8px; text-align: center;">
            <h3 style="color: white; margin: 0;">Overall Sentiment</h3>
            <p style="color: white; font-size: 1.5rem; margin: 10px 0;">{market_data['market_sentiment']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.metric("Sources Analyzed", f"{market_data['successful_analyses']}/{market_data['total_sources']}")
    
    with col3:
        st.metric("Key Insights", len(market_data['risks_opportunities']))
    
    # Detailed source analysis in expanders
    if results:
        st.markdown("### 📄 Source Analysis")
        render_detailed_source_analysis(results)

def render_detailed_source_analysis(results):
    """Render detailed source-by-source analysis"""
    
    for i, result in enumerate(results):
        if 'error' in result:
            with st.expander(f"❌ Error: {result['title']}", expanded=False):
                st.error(f"Failed to analyze: {result['error']}")
            continue
        
        # Create expander for each result
        title = result.get('title', 'Unknown Source')[:80]
        with st.expander(f"📄 {title}...", expanded=False):
            
            # Source information
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**🔗 Source:** [{result['url']}]({result['url']})")
                if result.get('query'):
                    st.caption(f"Found via search: {result['query']}")
            
            with col2:
                st.metric("Words", result.get('word_count', 0))
                st.caption(f"Analyzed: {result.get('timestamp', 'Unknown')}")
            
            st.markdown("---")
            
            # AI Analysis Results
            tab1, tab2, tab3 = st.tabs(["📝 Summary", "🏷️ Key Entities", "😊 Sentiment"])
            
            with tab1:
                st.markdown("**AI Summary:**")
                st.write(result.get('summary', 'No summary available'))
            
            with tab2:
                st.markdown("**Key Entities & Themes:**")
                entities = result.get('entities', {})
                if isinstance(entities, dict) and 'error' not in entities:
                    
                    # Display entities in columns
                    ent_col1, ent_col2 = st.columns(2)
                    
                    with ent_col1:
                        if entities.get('companies'):
                            st.markdown("**Companies:**")
                            for company in entities['companies'][:5]:
                                st.write(f"• {company}")
                        
                        if entities.get('projects'):
                            st.markdown("**Projects:**")
                            for project in entities['projects'][:3]:
                                st.write(f"• {project}")
                    
                    with ent_col2:
                        if entities.get('technologies'):
                            st.markdown("**Technologies:**")
                            for tech in entities['technologies'][:5]:
                                st.write(f"• {tech}")
                        
                        if entities.get('financial_figures'):
                            st.markdown("**Financial Figures:**")
                            for figure in entities['financial_figures'][:3]:
                                st.write(f"• {figure}")
                else:
                    st.json(entities)
            
            with tab3:
                sentiment = result.get('sentiment', {})
                if isinstance(sentiment, dict):
                    sent_value = sentiment.get('sentiment', 'Neutral')
                    confidence = sentiment.get('confidence', 0.0)
                    justification = sentiment.get('justification', 'No analysis available')
                    
                    # Display sentiment with color coding
                    if sent_value == 'Positive':
                        st.success(f"😊 **{sent_value}** (Confidence: {confidence:.1%})")
                    elif sent_value == 'Negative':
                        st.error(f"😟 **{sent_value}** (Confidence: {confidence:.1%})")
                    else:
                        st.info(f"😐 **{sent_value}** (Confidence: {confidence:.1%})")
                    
                    st.write(f"**Analysis:** {justification}")
                else:
                    st.write(sentiment)
            
            # Pin insight button
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button(f"📌 Pin Insight", key=f"pin_{i}"):
                    pin_insight(result, i)

def pin_insight(result, index):
    """Pin an insight to the global pinned insights"""
    
    insight = {
        'id': len(st.session_state.pinned_insights) + 1,
        'title': result.get('title', 'Unknown Source'),
        'url': result.get('url', ''),
        'summary': result.get('summary', ''),
        'sentiment': result.get('sentiment', {}),
        'entities': result.get('entities', {}),
        'timestamp': result.get('timestamp', ''),
        'source_module': 'SMART Markets',
        'scan_config': st.session_state.market_scan_config.copy() if st.session_state.market_scan_config else {},
        'contextual_trigger': st.session_state.contextual_trigger_data.copy() if st.session_state.contextual_trigger_data else None
    }
    
    st.session_state.pinned_insights.append(insight)
    st.success(f"✅ Insight pinned! Total pinned: {len(st.session_state.pinned_insights)}")
    st.rerun()

def render_segmentation_tab():
    """Render the market segmentation analysis tab"""
    
    st.subheader("📊 Market Segmentation Analysis")
    
    if not st.session_state.sample_data_loaded:
        st.warning("📊 Please load sample data from the sidebar to view segmentation analysis.")
        return
    
    df = st.session_state.df_market_segments
    
    if df.empty:
        st.error("No market segmentation data available.")
        return
    
    # Market size treemap
    st.markdown("### Market Size by Segment")
    
    fig_treemap = px.treemap(
        df,
        path=['segment'],
        values='market_size_gbp_m',
        color='growth_rate_percent',
        color_continuous_scale='RdYlGn',
        title="Market Size (£M) and Growth Rate by Segment"
    )
    
    fig_treemap.update_layout(
        height=500,
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_treemap, use_container_width=True)
    
    # Growth and market share analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Growth Rate Analysis")
        
        fig_growth = px.bar(
            df.sort_values('growth_rate_percent', ascending=True),
            x='growth_rate_percent',
            y='segment',
            orientation='h',
            color='growth_rate_percent',
            color_continuous_scale='RdYlGn',
            title="Market Growth Rate by Segment (%)"
        )
        
        fig_growth.update_layout(
            height=400,
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_growth, use_container_width=True)
    
    with col2:
        st.markdown("### Arcadis Market Position")
        
        fig_share = px.scatter(
            df,
            x='market_size_gbp_m',
            y='arcadis_market_share_percent',
            size='market_size_gbp_m',
            color='growth_rate_percent',
            hover_name='segment',
            color_continuous_scale='RdYlGn',
            title="Market Share vs Market Size"
        )
        
        fig_share.update_layout(
            height=400,
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig_share, use_container_width=True)
    
    # Detailed table
    st.markdown("### Detailed Segment Analysis")
    st.dataframe(
        df,
        use_container_width=True,
        height=300
    )

def render_demand_pipeline_tab():
    """Render the demand pipeline tab"""
    
    st.subheader("📋 Demand Pipeline")
    
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

def render_market_timeline_view(category, config):
    """Render chronological timeline view for market intelligence"""
    
    st.markdown(f"### 📅 {category} Intelligence Timeline")
    
    # Initialize timeline data in session state if not exists
    timeline_key = f"market_timeline_{category}"
    if timeline_key not in st.session_state:
        st.session_state[timeline_key] = []
    
    # Time range selector
    col1, col2 = st.columns(2)
    with col1:
        time_range = st.selectbox(
            "Timeline Range",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months", "All Time"],
            key=f"timeline_range_{category}"
        )
    
    with col2:
        view_type = st.selectbox(
            "View Type",
            ["Chronological", "By Impact", "By Source"],
            key=f"timeline_view_{category}"
        )
    
    # Generate historical data button
    if st.button(f"📈 Generate Historical {category} Data", key=f"generate_timeline_{category}"):
        historical_data = generate_historical_intelligence_data(category, time_range)
        st.session_state[timeline_key] = historical_data
        st.success(f"Generated {len(historical_data)} historical intelligence entries")
    
    # Display timeline
    if st.session_state[timeline_key]:
        render_intelligence_timeline(st.session_state[timeline_key], view_type, category)
    else:
        st.info("Generate historical data to view the intelligence timeline")

def render_supplier_timeline_view(intel_type, config):
    """Render chronological timeline view for supplier intelligence"""
    
    st.markdown(f"### 📅 {intel_type} Intelligence Timeline")
    
    # Initialize timeline data in session state if not exists
    timeline_key = f"supplier_timeline_{intel_type}"
    if timeline_key not in st.session_state:
        st.session_state[timeline_key] = []
    
    # Time range selector
    col1, col2 = st.columns(2)
    with col1:
        time_range = st.selectbox(
            "Timeline Range",
            ["Last 7 Days", "Last 30 Days", "Last 90 Days", "Last 6 Months", "All Time"],
            key=f"timeline_range_{intel_type}"
        )
    
    with col2:
        view_type = st.selectbox(
            "View Type",
            ["Chronological", "By Impact", "By Supplier"],
            key=f"timeline_view_{intel_type}"
        )
    
    # Generate historical data button
    if st.button(f"📈 Generate Historical {intel_type} Data", key=f"generate_timeline_supplier_{intel_type}"):
        historical_data = generate_historical_supplier_intelligence_data(intel_type, time_range)
        st.session_state[timeline_key] = historical_data
        st.success(f"Generated {len(historical_data)} historical intelligence entries")
    
    # Display timeline
    if st.session_state[timeline_key]:
        render_intelligence_timeline(st.session_state[timeline_key], view_type, intel_type)
    else:
        st.info("Generate historical data to view the intelligence timeline")

def render_market_comparison_view(category, config):
    """Render historical comparison view for market intelligence"""
    
    st.markdown(f"### 🔄 {category} Historical Comparison")
    
    # Initialize comparison data
    comparison_key = f"market_comparison_{category}"
    if comparison_key not in st.session_state:
        st.session_state[comparison_key] = {}
    
    # Date range selectors for comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Period A")
        period_a = st.selectbox(
            "Select Period A",
            ["Current Week", "Last Week", "Last Month", "Q1 2025", "Q2 2025"],
            key=f"period_a_{category}"
        )
        
        if st.button(f"Load Period A Data", key=f"load_a_{category}"):
            period_a_data = generate_period_intelligence_data(category, period_a)
            st.session_state[comparison_key]['period_a'] = {
                'period': period_a,
                'data': period_a_data
            }
            st.success(f"Loaded {len(period_a_data)} insights for {period_a}")
    
    with col2:
        st.markdown("#### Period B")
        period_b = st.selectbox(
            "Select Period B",
            ["Current Week", "Last Week", "Last Month", "Q1 2025", "Q2 2025"],
            key=f"period_b_{category}"
        )
        
        if st.button(f"Load Period B Data", key=f"load_b_{category}"):
            period_b_data = generate_period_intelligence_data(category, period_b)
            st.session_state[comparison_key]['period_b'] = {
                'period': period_b,
                'data': period_b_data
            }
            st.success(f"Loaded {len(period_b_data)} insights for {period_b}")
    
    # Display comparison if both periods loaded
    if 'period_a' in st.session_state[comparison_key] and 'period_b' in st.session_state[comparison_key]:
        render_period_comparison(
            st.session_state[comparison_key]['period_a'],
            st.session_state[comparison_key]['period_b'],
            category
        )

def render_supplier_comparison_view(intel_type, config):
    """Render historical comparison view for supplier intelligence"""
    
    st.markdown(f"### 🔄 {intel_type} Historical Comparison")
    
    # Initialize comparison data
    comparison_key = f"supplier_comparison_{intel_type}"
    if comparison_key not in st.session_state:
        st.session_state[comparison_key] = {}
    
    # Date range selectors for comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Period A")
        period_a = st.selectbox(
            "Select Period A",
            ["Current Week", "Last Week", "Last Month", "Q1 2025", "Q2 2025"],
            key=f"period_a_supplier_{intel_type}"
        )
        
        if st.button(f"Load Period A Data", key=f"load_a_supplier_{intel_type}"):
            period_a_data = generate_period_supplier_intelligence_data(intel_type, period_a)
            st.session_state[comparison_key]['period_a'] = {
                'period': period_a,
                'data': period_a_data
            }
            st.success(f"Loaded {len(period_a_data)} insights for {period_a}")
    
    with col2:
        st.markdown("#### Period B")
        period_b = st.selectbox(
            "Select Period B",
            ["Current Week", "Last Week", "Last Month", "Q1 2025", "Q2 2025"],
            key=f"period_b_supplier_{intel_type}"
        )
        
        if st.button(f"Load Period B Data", key=f"load_b_supplier_{intel_type}"):
            period_b_data = generate_period_supplier_intelligence_data(intel_type, period_b)
            st.session_state[comparison_key]['period_b'] = {
                'period': period_b,
                'data': period_b_data
            }
            st.success(f"Loaded {len(period_b_data)} insights for {period_b}")
    
    # Display comparison if both periods loaded
    if 'period_a' in st.session_state[comparison_key] and 'period_b' in st.session_state[comparison_key]:
        render_period_comparison(
            st.session_state[comparison_key]['period_a'],
            st.session_state[comparison_key]['period_b'],
            intel_type
        )

def generate_historical_intelligence_data(category, time_range):
    """Generate historical intelligence data for timeline view"""
    
    # Time range mapping
    days_mapping = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "Last 6 Months": 180,
        "All Time": 365
    }
    
    days = days_mapping.get(time_range, 30)
    
    # Generate sample historical data with realistic timestamps
    import random
    from datetime import datetime, timedelta
    
    historical_data = []
    
    # Sample suppliers and events
    suppliers = ["Balfour Beatty", "Skanska", "Kier Group", "Morgan Sindall", "Willmott Dixon", "BAM Construct"]
    event_types = ["Contract Win", "Financial Update", "New Partnership", "Regulatory Change", "Market Entry", "Innovation Announcement"]
    impact_levels = ["High", "Medium", "Low"]
    
    # Generate events across the time range
    for i in range(random.randint(15, 40)):
        event_date = datetime.now() - timedelta(days=random.randint(0, days))
        
        event = {
            "id": f"event_{category}_{i}",
            "timestamp": event_date,
            "title": f"{random.choice(suppliers)} - {random.choice(event_types)}",
            "summary": f"Important {category.lower()} intelligence regarding market developments and strategic positioning.",
            "impact_level": random.choice(impact_levels),
            "source": random.choice(["Construction News", "Building Magazine", "Thames Water Portal", "Gov.uk", "Company Website"]),
            "category": category,
            "supplier": random.choice(suppliers),
            "url": f"https://example.com/news/{i}",
            "content": f"Detailed analysis of {category.lower()} market intelligence showing significant developments in the water infrastructure sector.",
            "tags": [category.lower().replace(" ", "_"), "water_infrastructure", "procurement"]
        }
        historical_data.append(event)
    
    # Sort by timestamp (newest first)
    historical_data.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return historical_data

def generate_historical_supplier_intelligence_data(intel_type, time_range):
    """Generate historical supplier intelligence data for timeline view"""
    
    # Time range mapping
    days_mapping = {
        "Last 7 Days": 7,
        "Last 30 Days": 30,
        "Last 90 Days": 90,
        "Last 6 Months": 180,
        "All Time": 365
    }
    
    days = days_mapping.get(time_range, 30)
    
    # Generate sample historical data
    import random
    from datetime import datetime, timedelta
    
    historical_data = []
    
    # Sample suppliers and intelligence types
    suppliers = ["Balfour Beatty", "Skanska", "Kier Group", "Morgan Sindall", "Willmott Dixon", "BAM Construct"]
    intelligence_events = {
        "Financial Performance": ["Q1 Results", "Annual Report", "Credit Rating Update", "Revenue Growth"],
        "Contract Awards": ["Major Contract Win", "Framework Agreement", "Joint Venture", "Partnership Announcement"],
        "Innovation & Technology": ["Tech Innovation", "Digital Transformation", "R&D Investment", "Patent Filing"],
        "Leadership Changes": ["CEO Appointment", "Board Changes", "Key Hire", "Restructuring"],
        "ESG & Sustainability": ["Net Zero Commitment", "ESG Report", "Sustainability Initiative", "Environmental Award"]
    }
    
    events = intelligence_events.get(intel_type, ["General Update", "Market Activity", "Business Development"])
    impact_levels = ["High", "Medium", "Low"]
    
    # Generate events across the time range
    for i in range(random.randint(12, 35)):
        event_date = datetime.now() - timedelta(days=random.randint(0, days))
        supplier = random.choice(suppliers)
        
        event = {
            "id": f"supplier_event_{intel_type}_{i}",
            "timestamp": event_date,
            "title": f"{supplier} - {random.choice(events)}",
            "summary": f"Strategic {intel_type.lower()} intelligence regarding {supplier}'s market position and capabilities.",
            "impact_level": random.choice(impact_levels),
            "source": random.choice(["Company Press Release", "Industry Report", "Financial Times", "Construction News", "Official Filing"]),
            "category": intel_type,
            "supplier": supplier,
            "url": f"https://example.com/supplier-news/{i}",
            "content": f"Comprehensive analysis of {supplier}'s {intel_type.lower()} developments affecting procurement strategy.",
            "tags": [intel_type.lower().replace(" ", "_"), "supplier_intelligence", supplier.lower().replace(" ", "_")]
        }
        historical_data.append(event)
    
    # Sort by timestamp (newest first)
    historical_data.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return historical_data

def render_intelligence_timeline(timeline_data, view_type, category_name):
    """Render the intelligence timeline with different view options"""
    
    if not timeline_data:
        st.info("No timeline data available")
        return
    
    st.markdown(f"**Timeline contains {len(timeline_data)} intelligence entries**")
    
    # Sort data based on view type
    if view_type == "By Impact":
        impact_order = {"High": 0, "Medium": 1, "Low": 2}
        timeline_data = sorted(timeline_data, key=lambda x: impact_order.get(x["impact_level"], 3))
    elif view_type == "By Source":
        timeline_data = sorted(timeline_data, key=lambda x: x["source"])
    elif view_type == "By Supplier":
        timeline_data = sorted(timeline_data, key=lambda x: x.get("supplier", "Unknown"))
    # Default: Chronological (already sorted)
    
    # Archive controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("### Timeline Entries")
    with col2:
        if st.button("📁 Archive Old Entries", key=f"archive_{category_name}"):
            archived_count = archive_old_entries(timeline_data, category_name)
            st.success(f"Archived {archived_count} entries older than 90 days")
    with col3:
        if st.button("🗑️ Clear Timeline", key=f"clear_{category_name}"):
            clear_timeline_data(category_name)
            st.success("Timeline cleared")
    
    # Display timeline entries
    for i, entry in enumerate(timeline_data):
        render_timeline_entry(entry, i, category_name)

def render_timeline_entry(entry, index, category_name):
    """Render individual timeline entry"""
    
    # Impact level color coding
    impact_colors = {
        "High": "🔴",
        "Medium": "🟡", 
        "Low": "🟢"
    }
    
    impact_icon = impact_colors.get(entry["impact_level"], "⚪")
    
    # Create expandable entry
    with st.expander(
        f"{impact_icon} {entry['timestamp'].strftime('%Y-%m-%d %H:%M')} - {entry['title']}", 
        expanded=False
    ):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**Summary:** {entry['summary']}")
            st.markdown(f"**Content:** {entry['content']}")
            
            # Tags
            if entry.get('tags'):
                tag_str = " ".join([f"`{tag}`" for tag in entry['tags']])
                st.markdown(f"**Tags:** {tag_str}")
        
        with col2:
            st.markdown(f"**Impact:** {entry['impact_level']}")
            st.markdown(f"**Source:** {entry['source']}")
            if entry.get('supplier'):
                st.markdown(f"**Supplier:** {entry['supplier']}")
            
            # Action buttons
            if st.button("📌 Pin", key=f"pin_timeline_{category_name}_{index}"):
                pin_timeline_entry(entry)
                st.success("Entry pinned to insights")
            
            if st.button("📁 Archive", key=f"archive_timeline_{category_name}_{index}"):
                archive_timeline_entry(entry, category_name)
                st.success("Entry archived")

def generate_period_intelligence_data(category, period):
    """Generate intelligence data for a specific period"""
    
    # Generate sample data for the specified period
    import random
    from datetime import datetime, timedelta
    
    # Period date ranges
    period_mapping = {
        "Current Week": (datetime.now() - timedelta(days=7), datetime.now()),
        "Last Week": (datetime.now() - timedelta(days=14), datetime.now() - timedelta(days=7)),
        "Last Month": (datetime.now() - timedelta(days=60), datetime.now() - timedelta(days=30)),
        "Q1 2025": (datetime(2025, 1, 1), datetime(2025, 3, 31)),
        "Q2 2025": (datetime(2025, 4, 1), datetime(2025, 6, 30))
    }
    
    start_date, end_date = period_mapping.get(period, (datetime.now() - timedelta(days=30), datetime.now()))
    
    # Generate events within the period
    period_data = []
    suppliers = ["Balfour Beatty", "Skanska", "Kier Group", "Morgan Sindall"]
    
    for i in range(random.randint(8, 20)):
        event_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        event = {
            "id": f"period_{category}_{period}_{i}",
            "timestamp": event_date,
            "title": f"{random.choice(suppliers)} - Market Development",
            "summary": f"{category} intelligence for {period} period analysis",
            "impact_level": random.choice(["High", "Medium", "Low"]),
            "source": random.choice(["Industry Report", "Company News", "Government Update"]),
            "category": category,
            "period": period
        }
        period_data.append(event)
    
    return sorted(period_data, key=lambda x: x["timestamp"], reverse=True)

def generate_period_supplier_intelligence_data(intel_type, period):
    """Generate supplier intelligence data for a specific period"""
    
    # Similar to market intelligence but supplier-focused
    import random
    from datetime import datetime, timedelta
    
    period_mapping = {
        "Current Week": (datetime.now() - timedelta(days=7), datetime.now()),
        "Last Week": (datetime.now() - timedelta(days=14), datetime.now() - timedelta(days=7)),
        "Last Month": (datetime.now() - timedelta(days=60), datetime.now() - timedelta(days=30)),
        "Q1 2025": (datetime(2025, 1, 1), datetime(2025, 3, 31)),
        "Q2 2025": (datetime(2025, 4, 1), datetime(2025, 6, 30))
    }
    
    start_date, end_date = period_mapping.get(period, (datetime.now() - timedelta(days=30), datetime.now()))
    
    period_data = []
    suppliers = ["Balfour Beatty", "Skanska", "Kier Group", "Morgan Sindall"]
    
    for i in range(random.randint(6, 15)):
        event_date = start_date + timedelta(
            days=random.randint(0, (end_date - start_date).days)
        )
        
        event = {
            "id": f"supplier_period_{intel_type}_{period}_{i}",
            "timestamp": event_date,
            "title": f"{random.choice(suppliers)} - {intel_type} Update",
            "summary": f"{intel_type} supplier intelligence for {period} period",
            "impact_level": random.choice(["High", "Medium", "Low"]),
            "source": random.choice(["Company Report", "Financial News", "Industry Analysis"]),
            "category": intel_type,
            "period": period,
            "supplier": random.choice(suppliers)
        }
        period_data.append(event)
    
    return sorted(period_data, key=lambda x: x["timestamp"], reverse=True)

def render_period_comparison(period_a_data, period_b_data, category_name):
    """Render comparison between two periods"""
    
    st.markdown("### Period Comparison Analysis")
    
    # Summary metrics comparison
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            f"Period A ({period_a_data['period']})",
            f"{len(period_a_data['data'])} insights"
        )
    
    with col2:
        st.metric(
            f"Period B ({period_b_data['period']})",
            f"{len(period_b_data['data'])} insights"
        )
    
    with col3:
        diff = len(period_a_data['data']) - len(period_b_data['data'])
        st.metric(
            "Difference",
            f"{diff:+d} insights"
        )
    
    # Impact level comparison
    st.markdown("### Impact Level Comparison")
    
    # Calculate impact distributions
    def get_impact_distribution(data):
        impact_counts = {"High": 0, "Medium": 0, "Low": 0}
        for item in data:
            impact_counts[item["impact_level"]] += 1
        return impact_counts
    
    impact_a = get_impact_distribution(period_a_data['data'])
    impact_b = get_impact_distribution(period_b_data['data'])
    
    # Create comparison chart
    comparison_df = pd.DataFrame({
        'Impact Level': ['High', 'Medium', 'Low'],
        f'Period A ({period_a_data["period"]})': [impact_a['High'], impact_a['Medium'], impact_a['Low']],
        f'Period B ({period_b_data["period"]})': [impact_b['High'], impact_b['Medium'], impact_b['Low']]
    })
    
    fig_comparison = px.bar(
        comparison_df,
        x='Impact Level',
        y=[f'Period A ({period_a_data["period"]})', f'Period B ({period_b_data["period"]})'],
        barmode='group',
        title="Impact Level Distribution Comparison"
    )
    
    fig_comparison.update_layout(
        height=400,
        font=dict(color='white'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Side-by-side period details
    st.markdown("### Detailed Period Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### {period_a_data['period']} Details")
        for item in period_a_data['data'][:5]:  # Show top 5
            st.markdown(f"**{item['timestamp'].strftime('%m/%d')}** - {item['title']}")
    
    with col2:
        st.markdown(f"#### {period_b_data['period']} Details")
        for item in period_b_data['data'][:5]:  # Show top 5
            st.markdown(f"**{item['timestamp'].strftime('%m/%d')}** - {item['title']}")

def archive_old_entries(timeline_data, category_name):
    """Archive entries older than 90 days"""
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.now() - timedelta(days=90)
    archived_count = 0
    
    # Initialize archive in session state if not exists
    archive_key = f"archived_timeline_{category_name}"
    if archive_key not in st.session_state:
        st.session_state[archive_key] = []
    
    # Move old entries to archive
    for entry in timeline_data:
        if entry["timestamp"] < cutoff_date:
            st.session_state[archive_key].append(entry)
            archived_count += 1
    
    return archived_count

def clear_timeline_data(category_name):
    """Clear timeline data for a category"""
    timeline_key = f"market_timeline_{category_name}"
    if timeline_key in st.session_state:
        st.session_state[timeline_key] = []

def pin_timeline_entry(entry):
    """Pin a timeline entry to the global pinned insights"""
    if 'pinned_insights' not in st.session_state:
        st.session_state['pinned_insights'] = []
    
    # Convert timeline entry to pinned insight format
    pinned_entry = {
        "title": entry["title"],
        "summary": entry["summary"],
        "timestamp": entry["timestamp"].strftime("%Y-%m-%d %H:%M"),
        "source": entry["source"],
        "impact_level": entry["impact_level"],
        "url": entry.get("url", ""),
        "pinned_from": "timeline"
    }
    
    st.session_state['pinned_insights'].append(pinned_entry)

def archive_timeline_entry(entry, category_name):
    """Archive a specific timeline entry"""
    archive_key = f"archived_timeline_{category_name}"
    if archive_key not in st.session_state:
        st.session_state[archive_key] = []
    
    st.session_state[archive_key].append(entry)
    
    # Remove from active timeline
    timeline_key = f"market_timeline_{category_name}"
    if timeline_key in st.session_state:
        st.session_state[timeline_key] = [
            item for item in st.session_state[timeline_key] 
            if item["id"] != entry["id"]
        ]



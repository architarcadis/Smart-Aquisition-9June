import streamlit as st
import pandas as pd
import os
import io
import numpy as np
from modules import landing, smart_markets, smart_sourcing, smart_performance, amp8_regulatory

def generate_template_data(template_name):
    """Generate template data based on template type"""
    
    if template_name == "Market Segments":
        return pd.DataFrame({
            'segment': ['Infrastructure', 'Commercial', 'Residential', 'Industrial'],
            'market_size_gbp_m': [0, 0, 0, 0],
            'growth_rate_percent': [0, 0, 0, 0],
            'key_players': ['', '', '', ''],
            'major_projects': ['', '', '', ''],
            'challenges': ['', '', '', '']
        })
    
    elif template_name == "Sourcing Pipeline":
        return pd.DataFrame({
            'package_name': ['Package 1', 'Package 2', 'Package 3'],
            'category': ['Construction', 'Engineering', 'Consulting'],
            'estimated_value_gbp_m': [0, 0, 0],
            'procurement_stage': ['Planning', 'Tender', 'Award'],
            'target_award_date': ['2024-Q1', '2024-Q2', '2024-Q3'],
            'assigned_lead': ['', '', ''],
            'strategic_importance': ['High', 'Medium', 'Low'],
            'market_complexity': ['Complex', 'Medium', 'Simple']
        })
    
    elif template_name == "Supplier KPIs":
        return pd.DataFrame({
            'supplier_name': ['Supplier A', 'Supplier B', 'Supplier C'],
            'category': ['Construction', 'Engineering', 'Materials'],
            'contract_value_gbp_m': [0, 0, 0],
            'performance_score': [0, 0, 0],
            'delivery_performance': [0, 0, 0],
            'quality_score': [0, 0, 0],
            'safety_record': ['', '', ''],
            'sustainability_rating': ['', '', ''],
            'payment_terms_days': [0, 0, 0],
            'relationship_status': ['Active', 'Active', 'Under Review']
        })
    
    elif template_name == "Supply Chain Risks":
        return pd.DataFrame({
            'risk_category': ['Material Shortage', 'Supplier Failure', 'Price Volatility'],
            'affected_suppliers': ['', '', ''],
            'probability': ['High', 'Medium', 'Low'],
            'impact_severity': ['High', 'Medium', 'High'],
            'estimated_cost_impact_gbp_m': [0, 0, 0],
            'mitigation_strategy': ['', '', ''],
            'risk_owner': ['', '', ''],
            'review_date': ['2024-01-31', '2024-02-28', '2024-03-31']
        })
    
    elif template_name == "Team Performance":
        return pd.DataFrame({
            'team_member': ['Person A', 'Person B', 'Person C'],
            'role': ['Senior Procurement Manager', 'Procurement Specialist', 'Category Manager'],
            'packages_managed': [0, 0, 0],
            'total_value_gbp_m': [0, 0, 0],
            'avg_savings_percent': [0, 0, 0],
            'process_compliance_score': [0, 0, 0],
            'stakeholder_satisfaction': [0, 0, 0],
            'development_goals': ['', '', '']
        })
    
    elif template_name == "Demand Pipeline":
        return pd.DataFrame({
            'project_name': ['Project Alpha', 'Project Beta', 'Project Gamma'],
            'business_unit': ['Infrastructure', 'Commercial', 'Residential'],
            'estimated_value_gbp_m': [0, 0, 0],
            'expected_procurement_start': ['2024-Q2', '2024-Q3', '2024-Q4'],
            'project_stage': ['Planning', 'Design', 'Pre-Construction'],
            'procurement_approach': ['Traditional', 'Design & Build', 'Framework'],
            'strategic_priority': ['High', 'Medium', 'Low'],
            'key_requirements': ['', '', '']
        })
    
    else:
        return pd.DataFrame({'error': ['Unknown template type']})

def process_uploaded_templates(uploaded_files):
    """Process and load uploaded template files into the application"""
    
    success_count = 0
    error_count = 0
    
    for uploaded_file in uploaded_files:
        try:
            # Determine file type and read accordingly
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                st.sidebar.error(f"Unsupported file type: {uploaded_file.name}")
                error_count += 1
                continue
            
            # Smart detection based on filename and columns
            filename_lower = uploaded_file.name.lower()
            
            if 'market_segment' in filename_lower or 'segment' in df.columns:
                st.session_state.df_market_segments = df
                st.session_state.sample_data_loaded = True
                
            elif 'sourcing_pipeline' in filename_lower or 'package_name' in df.columns:
                st.session_state.df_sourcing_pipeline = df
                st.session_state.sample_data_loaded = True
                
            elif 'supplier_kpi' in filename_lower or 'supplier_name' in df.columns:
                st.session_state.df_supplier_kpis = df
                st.session_state.sample_data_loaded = True
                
            elif 'supply_chain_risk' in filename_lower or 'risk_category' in df.columns:
                st.session_state.df_supply_chain_risks = df
                st.session_state.sample_data_loaded = True
                
            elif 'team_performance' in filename_lower or 'team_member' in df.columns:
                st.session_state.df_team_performance = df
                st.session_state.sample_data_loaded = True
                
            elif 'demand_pipeline' in filename_lower or 'project_name' in df.columns:
                st.session_state.df_demand_pipeline = df
                st.session_state.sample_data_loaded = True
                
            else:
                # Try to auto-detect based on column patterns
                columns = df.columns.tolist()
                detected = False
                
                # Market segments detection
                if any(col in columns for col in ['segment', 'market_size', 'growth_rate']):
                    st.session_state.df_market_segments = df
                    detected = True
                
                # Sourcing pipeline detection
                elif any(col in columns for col in ['package_name', 'procurement_stage', 'estimated_value']):
                    st.session_state.df_sourcing_pipeline = df
                    detected = True
                
                # Supplier KPIs detection
                elif any(col in columns for col in ['supplier_name', 'performance_score', 'contract_value']):
                    st.session_state.df_supplier_kpis = df
                    detected = True
                
                # Supply chain risks detection
                elif any(col in columns for col in ['risk_category', 'probability', 'impact_severity']):
                    st.session_state.df_supply_chain_risks = df
                    detected = True
                
                # Team performance detection
                elif any(col in columns for col in ['team_member', 'role', 'packages_managed']):
                    st.session_state.df_team_performance = df
                    detected = True
                
                # Demand pipeline detection
                elif any(col in columns for col in ['project_name', 'business_unit', 'procurement_start']):
                    st.session_state.df_demand_pipeline = df
                    detected = True
                
                if detected:
                    st.session_state.sample_data_loaded = True
                else:
                    st.sidebar.warning(f"Could not auto-detect template type for: {uploaded_file.name}")
                    error_count += 1
                    continue
            
            success_count += 1
            st.sidebar.success(f"✅ Loaded: {uploaded_file.name}")
            
        except Exception as e:
            st.sidebar.error(f"Error processing {uploaded_file.name}: {str(e)}")
            error_count += 1
    
    return success_count, error_count

# Set page configuration
st.set_page_config(
    page_title="SMART Acquisition for Built Assets",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "# Arcadis SMART Acquisition for Built Assets v1.0"
    }
)

# Initialize session state variables
def initialize_session_state():
    """Initialize all necessary session state variables"""
    
    # Get API keys from Streamlit secrets first, then environment variables as fallback
    try:
        openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv('OPENAI_API_KEY', ''))
        google_key = st.secrets.get("GOOGLE_API_KEY", os.getenv('GOOGLE_API_KEY', ''))
        google_cx = st.secrets.get("GOOGLE_CX_ID", os.getenv('GOOGLE_CX_ID', ''))
    except:
        # Fallback to environment variables if secrets are not available
        openai_key = os.getenv('OPENAI_API_KEY', '')
        google_key = os.getenv('GOOGLE_API_KEY', '')
        google_cx = os.getenv('GOOGLE_CX_ID', '')
    
    session_vars = {
        'api_openai_key': openai_key,
        'api_google_key': google_key,
        'api_google_cx': google_cx,
        'sample_data_loaded': False,
        'df_market_segments': pd.DataFrame(),
        'df_competencies': pd.DataFrame(),
        'df_demand_pipeline': pd.DataFrame(),
        'df_sourcing_pipeline': pd.DataFrame(),
        'df_team_performance': pd.DataFrame(),
        'df_supplier_kpis': pd.DataFrame(),
        'df_sub_tier_map': pd.DataFrame(),
        'df_supply_chain_risks': pd.DataFrame(),
        'market_scan_config': {},
        'pinned_insights': [],
        'contextual_trigger_data': None
    }
    
    for var, default_value in session_vars.items():
        if var not in st.session_state:
            st.session_state[var] = default_value

# Initialize session state
initialize_session_state()

# Sidebar Navigation
def render_sidebar():
    """Render the global sidebar with navigation and configuration"""
    st.sidebar.title("🏗️ Smart Acquisition")
    st.sidebar.markdown("---")
    
    # API Configuration Status
    st.sidebar.subheader("🔑 API Configuration")
    st.sidebar.caption("Required for SMART Markets functionality")
    
    # Check if API keys are configured via Streamlit Cloud secrets
    api_keys_configured = all([
        st.session_state.api_openai_key, 
        st.session_state.api_google_key, 
        st.session_state.api_google_cx
    ])
    
    if api_keys_configured:
        st.sidebar.success("✅ API Keys configured via Streamlit Cloud")
        
        # Show which keys are available (without revealing values)
        if st.session_state.api_openai_key:
            st.sidebar.info("🤖 OpenAI API: Connected")
        if st.session_state.api_google_key:
            st.sidebar.info("🔍 Google Search API: Connected")
        if st.session_state.api_google_cx:
            st.sidebar.info("🎯 Google CX ID: Connected")
    else:
        st.sidebar.warning("⚠️ API Keys not configured")
        
        with st.sidebar.expander("📋 Setup Instructions", expanded=True):
            st.markdown("""
            **For Streamlit Cloud deployment:**
            
            1. Go to your Streamlit Cloud dashboard
            2. Click on your app settings (⚙️)
            3. Navigate to "Secrets" section
            4. Add the following secrets:
            
            ```toml
            OPENAI_API_KEY = "your-openai-api-key"
            GOOGLE_API_KEY = "your-google-search-api-key"
            GOOGLE_CX_ID = "your-google-custom-search-cx-id"
            ```
            
            5. Save and redeploy your app
            """)
        
        # Fallback manual input for local development
        if st.sidebar.checkbox("🔧 Manual Configuration (Local Dev)", key="manual_config_toggle"):
            st.sidebar.caption("For local development only")
            
            openai_key = st.sidebar.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.api_openai_key,
                key="api_openai_key_input"
            )
            
            google_key = st.sidebar.text_input(
                "Google Search API Key",
                type="password", 
                value=st.session_state.api_google_key,
                key="api_google_key_input"
            )
            
            google_cx = st.sidebar.text_input(
                "Google Search CX ID",
                value=st.session_state.api_google_cx,
                key="api_google_cx_input"
            )
            
            # Save API Keys button
            if st.sidebar.button("💾 Save API Keys"):
                st.session_state.api_openai_key = openai_key
                st.session_state.api_google_key = google_key
                st.session_state.api_google_cx = google_cx
                st.sidebar.success("API Keys saved successfully!")
                st.rerun()
    
    st.sidebar.markdown("---")
    
    # Template System
    st.sidebar.subheader("📋 Data Templates")
    st.sidebar.caption("Download templates, populate with your data, and upload")
    
    # Template download section
    with st.sidebar.expander("📥 Download Templates"):
        template_options = {
            "Market Segments": "market_segments_template.csv",
            "Sourcing Pipeline": "sourcing_pipeline_template.csv", 
            "Supplier KPIs": "supplier_kpis_template.csv",
            "Supply Chain Risks": "supply_chain_risks_template.csv",
            "Team Performance": "team_performance_template.csv",
            "Demand Pipeline": "demand_pipeline_template.csv"
        }
        
        for template_name, filename in template_options.items():
            if st.button(f"📄 {template_name}", key=f"download_{filename}"):
                template_data = generate_template_data(template_name)
                csv_data = template_data.to_csv(index=False)
                st.download_button(
                    label=f"⬇️ Download {template_name}",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key=f"dl_{filename}"
                )
    
    # Smart upload section
    st.sidebar.subheader("📤 Smart Data Upload")
    uploaded_files = st.sidebar.file_uploader(
        "Upload populated templates",
        type=['csv', 'xlsx', 'xls'],
        accept_multiple_files=True,
        key="template_uploader"
    )
    
    if uploaded_files:
        st.sidebar.write(f"📁 {len(uploaded_files)} file(s) selected")
        
        if st.sidebar.button("🔍 Process & Load Data", type="primary"):
            success_count, error_count = process_uploaded_templates(uploaded_files)
            
            if success_count > 0:
                st.sidebar.success(f"✅ {success_count} file(s) processed successfully!")
                st.rerun()
            
            if error_count > 0:
                st.sidebar.error(f"❌ {error_count} file(s) had errors")
    
    st.sidebar.markdown("---")
    
    # Sample Data Management
    st.sidebar.subheader("📊 Application Data")
    
    if not st.session_state.sample_data_loaded:
        if st.sidebar.button("📥 Load Sample Data"):
            from utils.thames_water_research import generate_thames_water_procurement_data
            
            with st.sidebar.status("Loading Thames Water AMP 8 data...", expanded=True) as status:
                st.write("Generating Thames Water AMP 8 procurement data...")
                thames_data = generate_thames_water_procurement_data([])
                
                # Load the Thames Water data into session state
                st.session_state.df_sourcing_pipeline = thames_data['sourcing_pipeline']
                st.session_state.df_supplier_kpis = thames_data['supplier_kpis'] 
                st.session_state.df_supply_chain_risks = thames_data['supply_chain_risks']
                st.session_state.df_team_performance = thames_data['team_performance']
                
                # Generate supporting data
                from utils.data_generator import generate_market_segments_data, generate_demand_pipeline_data, generate_sub_tier_map_data
                st.session_state.df_market_segments = generate_market_segments_data()
                st.session_state.df_demand_pipeline = generate_demand_pipeline_data()
                st.session_state.df_sub_tier_map = generate_sub_tier_map_data()
                st.session_state.df_competencies = pd.DataFrame()
                
                st.session_state.sample_data_loaded = True
                status.update(label="Thames Water AMP 8 data loaded successfully!", state="complete")
            
            st.sidebar.success("Sample data loaded successfully!")
            st.rerun()
    else:
        st.sidebar.success("✅ Data loaded")
        if st.sidebar.button("🗑️ Clear All Data"):
            # Reset all dataframes
            for key in ['df_market_segments', 'df_competencies', 'df_demand_pipeline', 
                       'df_sourcing_pipeline', 'df_team_performance', 'df_supplier_kpis',
                       'df_sub_tier_map', 'df_supply_chain_risks']:
                st.session_state[key] = pd.DataFrame()
            st.session_state.sample_data_loaded = False
            st.sidebar.success("All data cleared!")
            st.rerun()
    


# Main application logic
def main():
    """Main application entry point"""
    render_sidebar()
    
    # Create main navigation tabs - AMP 8 Regulatory Dashboard added as key module
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Landing Page",
        "📊 SMART Sourcing",
        "🚀 SMART Performance",
        "📋 AMP 8 Regulatory", 
        "📈 SMART Markets"
    ])
    
    with tab1:
        landing.render()
    
    with tab2:
        smart_sourcing.render()
    
    with tab3:
        smart_performance.render()
    
    with tab4:
        amp8_regulatory.render()
    
    with tab5:
        smart_markets.render()

if __name__ == "__main__":
    main()

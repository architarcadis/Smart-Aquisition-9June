import streamlit as st

def render():
    """Render the landing page"""
    
    # Hero section
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="font-size: 3.5rem; margin-bottom: 1rem; color: #00C5E7;">
                🏗️ Smart Acquisition
            </h1>
            <h2 style="font-size: 1.8rem; margin-bottom: 2rem; color: #FAFAFA; font-weight: 300;">
                Integrated Intelligence for Capital Programme Success
            </h2>
        </div>
    """, unsafe_allow_html=True)
    
    # Introduction
    st.markdown("""
### Thames Water AMP 8 Delivery Command Center

This platform provides Thames Water's procurement leadership with real-time visibility 
into AMP 8 programme delivery, ensuring regulatory commitments are met while 
maximizing customer value and operational efficiency.

Track contract delivery status, manage supplier performance, and maintain strategic 
oversight of the £15 billion AMP 8 investment programme through integrated 
procurement intelligence.
    """)
    
    st.markdown("---")
    
    # Three pillars
    st.markdown("### 🔺 The Smart Acquisition Framework")
    
    # Create three columns for the pillars
    pillar_col1, pillar_col2, pillar_col3 = st.columns(3)
    
    with pillar_col1:
        st.markdown("""
        #### 💼 SMART Sourcing
        **Contract Delivery Management**
        
        - Project delivery tracking
        - Supplier market health
        - Contract pipeline planning
        - Regulatory deadline monitoring
        - Budget variance tracking
        """)
    
    with pillar_col2:
        st.markdown("""
        #### 🚀 SMART Performance
        **Operational Excellence**
        
        - Contract delivery status
        - Delivery risk oversight
        - Customer impact tracking
        - Supplier performance monitoring
        - Service improvement delivery
        """)
    
    with pillar_col3:
        st.markdown("""
        #### 📈 SMART Markets
        **Strategic Market Intelligence**
        
        - Water industry market scanning
        - Regulatory change monitoring
        - Competitive intelligence
        - Innovation trend analysis
        - Market capacity assessment
        """)
    
    st.markdown("---")
    
    # Key features
    st.markdown("### ✨ Key Features")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        st.markdown("""
        **🔗 Integrated Intelligence**
        - Pin insights from market scanning
        - Reference external data in procurement decisions
        - Cross-module data sharing
        - Contextual analysis triggers
        
        **🤖 AI-Powered Analytics**
        - OpenAI GPT integration for content analysis
        - Automated market intelligence gathering
        - Sentiment analysis and trend detection
        - Entity extraction and summarization
        """)
    
    with feature_col2:
        st.markdown("""
        **📊 Interactive Dashboards**
        - Real-time data visualization
        - Elegant Plotly charts and graphs
        - Responsive design and layout
        - Professional built-assets styling
        
        **🔧 Configurable Scanning**
        - Industry sub-sector targeting
        - Geographic focus settings
        - Category-specific searches
        - Custom keyword integration
        """)
    
    st.markdown("---")
    
    # Getting started
    st.markdown("### 🚀 Getting Started")
    
    # Status checks
    api_configured = all([
        st.session_state.api_openai_key,
        st.session_state.api_google_key,
        st.session_state.api_google_cx
    ])
    
    data_loaded = st.session_state.sample_data_loaded
    
    setup_col1, setup_col2 = st.columns(2)
    
    with setup_col1:
        st.markdown("#### 1️⃣ API Configuration")
        
        if api_configured:
            st.success("✅ APIs configured via Streamlit Cloud")
            st.markdown("""
            **Ready for Market Intelligence:**
            - OpenAI GPT analysis
            - Google Custom Search
            - Real-time data processing
            """)
        else:
            st.warning("⚠️ API keys required")
            st.markdown("""
            **For Streamlit Cloud deployment:**
            
            Configure API keys in your app settings under "Secrets":
            - `OPENAI_API_KEY`: For content analysis
            - `GOOGLE_API_KEY`: For market search
            - `GOOGLE_CX_ID`: Custom search engine
            
            See sidebar for detailed setup instructions.
            """)
    
    with setup_col2:
        st.markdown("#### 2️⃣ Load Sample Data")
        if data_loaded:
            st.success("✅ Sample data is loaded")
            st.markdown("Explore SMART Sourcing and SMART Performance modules with built assets data.")
        else:
            st.info("📊 Sample data available")
            st.markdown("Load built assets sample data from the sidebar to explore all analytics features.")
    
    st.markdown("---")
    
    # Navigation prompt
    st.markdown("""
    ### 🧭 Ready to Explore?
    
    Use the **SMART Acquisition Navigator** in the sidebar to access the three main modules:
    
    - **📈 SMART Markets**: Start with market intelligence and AI-powered scanning
    - **📊 SMART Sourcing**: Analyze procurement pipelines and team performance  
    - **🚀 SMART Performance**: Monitor supplier KPIs and supply chain risks
    
    Each module is designed to work independently while sharing intelligence 
    through the integrated pinned insights system.
    """)
    
    # Call to action
    if not api_configured or not data_loaded:
        st.markdown("---")
        st.info("💡 **Pro Tip**: Complete the setup steps above to unlock the full potential of the SMART Acquisition platform.")
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 1rem; color: #888;">
        <small>
            Arcadis SMART Acquisition for Built Assets v1.0<br>
            Empowering capital programme success through integrated intelligence
        </small>
    </div>
    """, unsafe_allow_html=True)

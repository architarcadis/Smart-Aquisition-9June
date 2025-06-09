import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime, timedelta
import random

def generate_market_segments_data():
    """Generate sample market segmentation data"""
    segments = [
        'Infrastructure', 'Residential', 'Commercial', 'Industrial', 
        'Healthcare', 'Education', 'Transport', 'Energy', 'Water', 'Digital'
    ]
    
    data = []
    for segment in segments:
        data.append({
            'segment': segment,
            'market_size_gbp_m': random.randint(5000, 50000),
            'growth_rate_percent': round(random.uniform(-2.5, 8.5), 1),
            'competitive_intensity': random.choice(['Low', 'Medium', 'High']),
            'regulatory_impact': random.choice(['Low', 'Medium', 'High']),
            'technology_disruption': random.choice(['Low', 'Medium', 'High']),
            'arcadis_market_share_percent': round(random.uniform(2.0, 15.0), 1)
        })
    
    return pd.DataFrame(data)

def generate_competencies_data():
    """Generate sample core competencies data"""
    competencies = [
        'Project Management', 'Design & Engineering', 'Cost Management',
        'Digital Solutions', 'Sustainability', 'Risk Management',
        'Asset Management', 'Programme Delivery', 'Technical Advisory',
        'Infrastructure Planning'
    ]
    
    data = []
    for comp in competencies:
        data.append({
            'competency': comp,
            'demand_score': random.randint(60, 95),
            'supply_capability': random.randint(55, 90),
            'market_position': random.choice(['Leading', 'Strong', 'Developing']),
            'investment_priority': random.choice(['High', 'Medium', 'Low']),
            'revenue_contribution_percent': round(random.uniform(5.0, 20.0), 1)
        })
    
    return pd.DataFrame(data)

def generate_demand_pipeline_data():
    """Generate sample demand pipeline data"""
    project_types = [
        'Major Infrastructure', 'Smart Cities', 'Healthcare Facilities',
        'Educational Campus', 'Transport Hub', 'Energy Infrastructure',
        'Water Treatment', 'Digital Infrastructure', 'Residential Development',
        'Commercial Complex'
    ]
    
    data = []
    start_date = datetime.now()
    
    for i, project_type in enumerate(project_types):
        project_start = start_date + timedelta(days=random.randint(30, 365))
        project_end = project_start + timedelta(days=random.randint(180, 1095))
        
        data.append({
            'project_name': f"{project_type} - Phase {random.randint(1, 3)}",
            'project_type': project_type,
            'client_sector': random.choice(['Public', 'Private', 'Mixed']),
            'estimated_value_gbp_m': random.randint(10, 500),
            'probability_percent': random.randint(25, 85),
            'start_date': project_start.strftime('%Y-%m-%d'),
            'end_date': project_end.strftime('%Y-%m-%d'),
            'region': random.choice(['London', 'North', 'Midlands', 'South', 'Scotland', 'Wales']),
            'status': random.choice(['Opportunity', 'Qualified', 'Proposal', 'Negotiation'])
        })
    
    return pd.DataFrame(data)

def generate_sourcing_pipeline_data():
    """Generate sample sourcing pipeline data"""
    categories = [
        'Construction Services', 'Design Services', 'Technology Solutions',
        'Materials Supply', 'Equipment Hire', 'Specialist Consultancy',
        'Site Services', 'Testing & Inspection', 'Project Controls',
        'Health & Safety'
    ]
    
    stages = ['Market Analysis', 'RFQ Preparation', 'Tender Process', 'Evaluation', 'Award', 'Contract']
    
    data = []
    for i in range(15):
        category = random.choice(categories)
        stage = random.choice(stages)
        
        data.append({
            'package_name': f"{category} Package {random.randint(1, 99)}",
            'procurement_category': category,
            'current_stage': stage,
            'total_value_gbp': random.randint(100000, 10000000),
            'expected_award_date': (datetime.now() + timedelta(days=random.randint(30, 180))).strftime('%Y-%m-%d'),
            'supplier_responses': random.randint(3, 12),
            'stage_progress_percent': random.randint(20, 95),
            'risk_level': random.choice(['Low', 'Medium', 'High']),
            'buyer_lead': f"Buyer {random.randint(1, 8)}",
            'days_in_current_stage': random.randint(5, 45)
        })
    
    return pd.DataFrame(data)

def generate_team_performance_data():
    """Generate sample team performance data"""
    teams = ['North Region', 'South Region', 'London', 'Scotland', 'Digital', 'Infrastructure']
    
    data = []
    for team in teams:
        data.append({
            'team': team,
            'procurement_cycle_days_avg': random.randint(45, 120),
            'cost_savings_percent': round(random.uniform(3.5, 12.0), 1),
            'supplier_satisfaction_score': round(random.uniform(7.2, 9.5), 1),
            'compliance_score_percent': random.randint(85, 98),
            'active_suppliers': random.randint(25, 85),
            'contracts_awarded_qtd': random.randint(15, 55),
            'spend_under_management_gbp_m': random.randint(20, 150)
        })
    
    return pd.DataFrame(data)

def generate_supplier_kpis_data():
    """Generate sample supplier KPIs data"""
    suppliers = [
        'Balfour Beatty', 'Skanska', 'Kier Group', 'Morgan Sindall',
        'Willmott Dixon', 'BAM Construct', 'Laing O\'Rourke', 'Vinci',
        'Bouygues UK', 'Galliford Try', 'Wates Group', 'ISG'
    ]
    
    data = []
    for supplier in suppliers:
        data.append({
            'supplier_name': supplier,
            'overall_score': round(random.uniform(6.5, 9.2), 1),
            'quality_score': round(random.uniform(7.0, 9.5), 1),
            'delivery_score': round(random.uniform(6.8, 9.3), 1),
            'cost_performance_score': round(random.uniform(6.2, 8.8), 1),
            'sustainability_score': round(random.uniform(5.5, 9.0), 1),
            'innovation_score': round(random.uniform(5.8, 8.5), 1),
            'contracts_active': random.randint(2, 15),
            'total_spend_gbp_m': round(random.uniform(5.0, 75.0), 1),
            'risk_level': random.choice(['Low', 'Medium', 'High'])
        })
    
    return pd.DataFrame(data)

def generate_sub_tier_map_data():
    """Generate sample sub-tier mapping data"""
    main_contractors = ['Balfour Beatty', 'Skanska', 'Kier Group', 'Morgan Sindall']
    sub_contractors = [
        'ABC Electrical', 'XYZ Plumbing', 'Steel Solutions Ltd', 'Concrete Experts',
        'Green Energy Co', 'Safety First Ltd', 'Tech Install Pro', 'Foundation Specialists'
    ]
    
    data = []
    for main in main_contractors:
        # Each main contractor has 3-6 sub-contractors
        num_subs = random.randint(3, 6)
        selected_subs = random.sample(sub_contractors, num_subs)
        
        for sub in selected_subs:
            data.append({
                'main_contractor': main,
                'sub_contractor': sub,
                'relationship_strength': random.choice(['Strong', 'Medium', 'Weak']),
                'contract_value_gbp': random.randint(50000, 2000000),
                'performance_rating': round(random.uniform(6.0, 9.0), 1),
                'risk_exposure': random.choice(['Low', 'Medium', 'High'])
            })
    
    return pd.DataFrame(data)

def generate_supply_chain_risks_data():
    """Generate sample supply chain risks data"""
    risk_categories = [
        'Material Shortages', 'Price Volatility', 'Supplier Financial Health',
        'Geopolitical Disruption', 'Regulatory Changes', 'Cyber Security',
        'Climate Impact', 'Skills Shortage', 'Transport Disruption', 'Quality Issues'
    ]
    
    data = []
    for risk in risk_categories:
        data.append({
            'risk_category': risk,
            'probability': random.choice(['Very Low', 'Low', 'Medium', 'High', 'Very High']),
            'impact': random.choice(['Very Low', 'Low', 'Medium', 'High', 'Very High']),
            'current_mitigation': random.choice(['None', 'Basic', 'Adequate', 'Strong', 'Comprehensive']),
            'affected_suppliers': random.randint(5, 45),
            'estimated_cost_impact_gbp_m': round(random.uniform(0.5, 25.0), 1),
            'timeline_to_impact_days': random.randint(30, 365),
            'mitigation_owner': random.choice(['Procurement', 'Risk', 'Operations', 'Finance'])
        })
    
    return pd.DataFrame(data)

def load_all_sample_data():
    """Load all sample data into session state"""
    try:
        st.session_state.df_market_segments = generate_market_segments_data()
        st.session_state.df_competencies = generate_competencies_data()
        st.session_state.df_demand_pipeline = generate_demand_pipeline_data()
        st.session_state.df_sourcing_pipeline = generate_sourcing_pipeline_data()
        st.session_state.df_team_performance = generate_team_performance_data()
        st.session_state.df_supplier_kpis = generate_supplier_kpis_data()
        st.session_state.df_sub_tier_map = generate_sub_tier_map_data()
        st.session_state.df_supply_chain_risks = generate_supply_chain_risks_data()
        
        return True
    except Exception as e:
        st.error(f"Error loading sample data: {str(e)}")
        return False

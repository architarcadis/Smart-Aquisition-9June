import streamlit as st
import requests
import time
import json
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from openai import OpenAI
from utils.web_scraper import get_website_text_content
from urllib.parse import urlparse, urljoin
import re

class MarketScanner:
    def __init__(self):
        self.openai_client = None
        self.google_service = None
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize API clients with Streamlit secrets and environment fallback"""
        try:
            # Get API keys from Streamlit secrets first, then environment variables as fallback
            try:
                openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv('OPENAI_API_KEY'))
                google_key = st.secrets.get("GOOGLE_API_KEY", os.getenv('GOOGLE_API_KEY'))
                google_cx = st.secrets.get("GOOGLE_CX_ID", os.getenv('GOOGLE_CX_ID'))
            except:
                # Fallback to environment variables if secrets are not available
                openai_key = os.getenv('OPENAI_API_KEY')
                google_key = os.getenv('GOOGLE_API_KEY') 
                google_cx = os.getenv('GOOGLE_CX_ID')
            
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
            
            if google_key and google_cx:
                self.google_service = build(
                    "customsearch", "v1", 
                    developerKey=google_key
                )
                self.google_cx = google_cx
                
        except Exception as e:
            st.error(f"Error setting up APIs: {str(e)}")
    
    def validate_api_keys(self):
        """Validate that all required API keys are present"""
        try:
            openai_key = st.secrets.get("OPENAI_API_KEY", os.getenv('OPENAI_API_KEY'))
            google_key = st.secrets.get("GOOGLE_API_KEY", os.getenv('GOOGLE_API_KEY'))
            google_cx = st.secrets.get("GOOGLE_CX_ID", os.getenv('GOOGLE_CX_ID'))
        except:
            openai_key = os.getenv('OPENAI_API_KEY')
            google_key = os.getenv('GOOGLE_API_KEY')
            google_cx = os.getenv('GOOGLE_CX_ID')
        
        if not all([openai_key, google_key, google_cx]):
            st.error("API keys are missing. Please ensure Google Search and OpenAI API keys are configured.")
            return False
        return True
    
    def construct_search_queries(self, config, refinement_keywords=""):
        """
        Intelligently construct search queries based on configuration and context
        """
        queries = []
        
        # Check for contextual trigger data
        if st.session_state.contextual_trigger_data:
            trigger = st.session_state.contextual_trigger_data
            if trigger['type'] == 'sourcing_package':
                # Create query based on sourcing package
                query = f"{trigger['name']} {trigger['category']} market trends suppliers UK"
                queries.append(query)
                # Clear the trigger data after use
                st.session_state.contextual_trigger_data = None
                return queries
        
        # Base components from configuration
        base_components = []
        
        if 'geo_focus' in config and config['geo_focus']:
            base_components.append(config['geo_focus'])
        
        if 'sub_sectors' in config and config['sub_sectors']:
            base_components.extend(config['sub_sectors'])
        
        if 'categories' in config and config['categories']:
            base_components.extend(config['categories'])
        
        if 'keywords' in config and config['keywords']:
            base_components.append(config['keywords'])
        
        if refinement_keywords:
            base_components.append(refinement_keywords)
        
        # Add built assets context
        base_components.extend(["built assets", "construction", "infrastructure"])
        
        # Create main query
        if base_components:
            main_query = " ".join(base_components[:6])  # Limit to avoid too long queries
            queries.append(main_query)
            
            # Create variations for broader coverage
            if len(base_components) > 3:
                variation1 = " ".join([base_components[0], base_components[1], "market analysis", "2024"])
                variation2 = " ".join([base_components[0], "procurement", "suppliers", "trends"])
                queries.extend([variation1, variation2])
        else:
            # Default query
            queries.append("UK built assets construction market trends 2024")
        
        return queries[:3]  # Limit to 3 queries maximum
    
    def execute_google_search(self, queries, config):
        """Execute Google Custom Search API calls with geographic filtering and no scraping"""
        if not self.google_service:
            st.error("Google Search API not configured")
            return []
        
        all_results = []
        geographic_scope = config.get('geographic_scope', ['UK'])
        time_range = config.get('time_range', 'Last 6 months')
        
        # Set date restriction based on time range
        date_restrict = 'm6' if time_range == 'Last 6 months' else 'm3'
        
        for query in queries:
            try:
                # Enhance query with geographic filters for UK focus
                if 'UK' in geographic_scope:
                    enhanced_query = f'{query} (site:gov.uk OR site:ac.uk OR site:co.uk) "United Kingdom" OR "UK"'
                    gl_param = 'uk'  # Geographic location
                    hl_param = 'en-GB'  # Language
                else:
                    enhanced_query = query
                    gl_param = None
                    hl_param = 'en'
                
                with st.spinner(f"Searching UK sources for: {query}"):
                    search_params = {
                        'q': enhanced_query,
                        'cx': st.session_state.api_google_cx,
                        'num': min(10, 10),  # API limit is 10 per request
                        'dateRestrict': date_restrict
                    }
                    
                    if gl_param:
                        search_params['gl'] = gl_param
                        search_params['hl'] = hl_param
                    
                    result = self.google_service.cse().list(**search_params).execute()
                    
                    if 'items' in result:
                        for item in result['items']:
                            # Check if result is UK-relevant
                            if self._is_uk_relevant(item, geographic_scope):
                                search_result = {
                                    'title': item.get('title', ''),
                                    'url': item.get('link', ''),
                                    'snippet': item.get('snippet', ''),
                                    'source': item.get('displayLink', ''),
                                    'date': self._extract_date_from_result(item),
                                    'query': query,
                                    'content': item.get('snippet', '')  # Use snippet as content - no scraping needed
                                }
                                all_results.append(search_result)
                    
                    time.sleep(1.0)  # Rate limiting
                    
            except HttpError as e:
                st.error(f"Google Search API error for query '{query}': {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error during search: {str(e)}")
        
        return all_results
    
    def _is_uk_relevant(self, item, geographic_scope):
        """Check if search result is relevant to specified geographic scope"""
        if 'UK' not in geographic_scope:
            return True
            
        url = item.get('link', '').lower()
        title_snippet = f"{item.get('title', '')} {item.get('snippet', '')}".lower()
        
        # Check for UK domains
        uk_domains = ['.gov.uk', '.ac.uk', '.co.uk', '.org.uk', '.nhs.uk']
        if any(domain in url for domain in uk_domains):
            return True
            
        # Check for UK keywords
        uk_keywords = ['united kingdom', 'uk', 'britain', 'england', 'wales', 'scotland', 'ofwat', 'defra']
        if any(keyword in title_snippet for keyword in uk_keywords):
            return True
            
        # Exclude obvious non-UK sources
        non_uk_indicators = ['usa', 'united states', 'colorado', 'california', '.edu']
        if any(indicator in url or indicator in title_snippet for indicator in non_uk_indicators):
            return False
            
        return True
    
    def _extract_date_from_result(self, item):
        """Extract date from search result metadata"""
        # Try to extract date from various metadata fields
        pagemap = item.get('pagemap', {})
        
        # Try metatags first
        metatags = pagemap.get('metatags', [{}])
        if metatags:
            date_fields = ['article:published_time', 'date', 'pubdate', 'last-modified']
            for field in date_fields:
                date_val = metatags[0].get(field)
                if date_val:
                    return date_val
        
        # Try other pagemap sources
        for source in ['newsarticle', 'article', 'webpage']:
            if source in pagemap:
                date_val = pagemap[source][0].get('datepublished') or pagemap[source][0].get('datemodified')
                if date_val:
                    return date_val
        
        return 'Recent'
    
    def analyze_search_snippets(self, search_results, config):
        """Analyze search snippets directly without web scraping"""
        analyzed_content = []
        
        for result in search_results:
            try:
                # Use snippet as content source - no scraping needed
                snippet_content = {
                    'url': result['url'],
                    'content': result['snippet'],
                    'title': result['title'],
                    'source': result['source'],
                    'date': result['date'],
                    'query': result['query']
                }
                analyzed_content.append(snippet_content)
                
            except Exception as e:
                st.warning(f"Failed to process result from {result.get('source', 'unknown')}: {str(e)}")
                continue
        
        return analyzed_content
    
    def analyze_snippets_with_openai(self, snippet_data, config):
        """Analyze search snippets with OpenAI for market intelligence"""
        if not self.openai_client:
            st.error("OpenAI API not configured")
            return []
        
        analyzed_results = []
        suppliers = config.get('suppliers', [])
        intelligence_types = config.get('intelligence_types', [])
        market_categories = config.get('market_categories', [])
        
        try:
            # Group snippets for batch analysis
            snippet_text = "\n\n".join([
                f"Title: {item['title']}\nSource: {item['source']}\nDate: {item['date']}\nContent: {item['content']}"
                for item in snippet_data
            ])
            
            # Determine analysis context based on configuration
            if market_categories:
                context_categories = ', '.join(market_categories)
                analysis_focus = "market intelligence across sectors"
            elif intelligence_types:
                context_categories = ', '.join(intelligence_types)
                analysis_focus = "supplier intelligence insights"
            else:
                context_categories = "All categories"
                analysis_focus = "market intelligence"
            
            prompt = f"""
            Analyze the following market intelligence snippets for procurement insights.
            
            Focus on suppliers: {', '.join(suppliers) if suppliers else 'Any suppliers mentioned'}
            Analysis categories: {context_categories}
            
            Snippets:
            {snippet_text}
            
            For each relevant snippet, provide comprehensive analysis with:
            1. Title (concise and descriptive)
            2. Category (Infrastructure/Technology/Services/Materials/Equipment for market intelligence OR Financial/Regulatory/Government Programs/Innovation/Competitive for supplier intelligence)
            3. Impact Level (High/Medium/Low)
            4. Summary (2-3 detailed sentences explaining the key intelligence and procurement implications)
            5. Key Insights (3-5 specific bullet points with actionable intelligence)
            6. Recommended Actions (2-3 concrete procurement actions)
            7. Suppliers Mentioned (any specific companies mentioned)
            8. Relevance Score (0-1 based on procurement value)
            
            CRITICAL: Always provide a comprehensive summary for each insight. The summary must explain the intelligence value, market implications, and procurement relevance clearly.
            
            Respond in JSON format:
            {{
                "insights": [
                    {{
                        "title": "descriptive title",
                        "category": "appropriate category",
                        "impact_level": "High/Medium/Low",
                        "summary": "detailed 2-3 sentence summary explaining intelligence value and procurement implications",
                        "insights": ["specific insight 1", "actionable insight 2", "market insight 3"],
                        "recommended_actions": ["concrete action 1", "procurement action 2"],
                        "suppliers_mentioned": ["supplier1", "supplier2"],
                        "relevance_score": 0.85
                    }}
                ]
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if content:
                result = json.loads(content)
            else:
                result = {"insights": []}
            
            # Process OpenAI results
            for i, insight in enumerate(result.get('insights', [])):
                # Map insight to corresponding source data
                source_index = i % len(snippet_data) if snippet_data else 0
                source_data = snippet_data[source_index] if snippet_data else {}
                
                processed_result = {
                    'id': f"insight_{int(time.time())}_{i}",
                    'title': insight.get('title', f'Market Intelligence #{i+1}'),
                    'category': insight.get('category', 'Market Trends'),
                    'impact_level': insight.get('impact_level', 'Medium'),
                    'summary': insight.get('summary', ''),
                    'insights': insight.get('insights', []),
                    'recommended_actions': insight.get('recommended_actions', []),
                    'suppliers_mentioned': insight.get('suppliers_mentioned', []),
                    'relevance_score': insight.get('relevance_score', 0.7),
                    'source': source_data.get('source', 'Market Intelligence'),
                    'url': source_data.get('url', ''),
                    'timestamp': source_data.get('date', 'Recent'),
                    'intelligence_type': insight.get('category', 'Market Trends')
                }
                analyzed_results.append(processed_result)
            
        except Exception as e:
            st.error(f"OpenAI analysis error: {str(e)}")
            # Return processed snippet data as fallback
            for i, item in enumerate(snippet_data):
                fallback_result = {
                    'id': f"fallback_{int(time.time())}_{i}",
                    'title': item['title'],
                    'category': 'Market Trends',
                    'impact_level': 'Medium',
                    'summary': item['content'][:200] + '...',
                    'insights': ['Market information available'],
                    'recommended_actions': ['Review detailed source information'],
                    'suppliers_mentioned': [],
                    'relevance_score': 0.6,
                    'source': item.get('source', 'Unknown'),
                    'url': item.get('url', ''),
                    'timestamp': item.get('date', 'Recent'),
                    'intelligence_type': 'Market Trends'
                }
                analyzed_results.append(fallback_result)
        
        return analyzed_results
    
    def crawl_urls(self, urls, crawl_depth=0):
        """Crawl URLs and extract content"""
        crawled_content = []
        processed_urls = set()
        
        for url_info in urls:
            if isinstance(url_info, dict):
                url = url_info['url']
                title = url_info.get('title', '')
                query = url_info.get('query', '')
            else:
                url = url_info
                title = ''
                query = ''
            
            if url in processed_urls:
                continue
            
            processed_urls.add(url)
            
            try:
                with st.spinner(f"Crawling: {url[:50]}..."):
                    # Use the web scraper utility
                    content = get_website_text_content(url)
                    
                    if content and len(content.strip()) > 100:  # Minimum content threshold
                        crawled_content.append({
                            'url': url,
                            'title': title or self._extract_title_from_url(url),
                            'content': content,
                            'query': query,
                            'word_count': len(content.split())
                        })
                    else:
                        st.warning(f"Insufficient content extracted from {url}")
                
                time.sleep(1)  # Politeness delay
                
            except Exception as e:
                st.warning(f"Failed to crawl {url}: {str(e)}")
        
        return crawled_content
    
    def _extract_title_from_url(self, url):
        """Extract a readable title from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            path_parts = [p for p in parsed.path.split('/') if p]
            if path_parts:
                return f"{domain} - {path_parts[-1].replace('-', ' ').replace('_', ' ').title()}"
            return domain
        except:
            return url[:50] + "..."
    
    def analyze_with_openai(self, crawled_data):
        """Analyze crawled content with OpenAI"""
        if not self.openai_client:
            st.error("OpenAI API not configured")
            return []
        
        analyzed_results = []
        
        for item in crawled_data:
            try:
                with st.spinner(f"Analyzing content from {item['title']}..."):
                    # Truncate content if too long (API limits)
                    content = item['content'][:8000]  # Rough token limit
                    
                    # Summary analysis
                    summary_prompt = f"""
                    Analyze this text from the perspective of a procurement professional in the built assets sector.
                    Provide a concise summary in 3-5 bullet points focusing on:
                    - Key market trends and insights
                    - Important companies, projects, or technologies mentioned
                    - Procurement or supply chain implications
                    - Financial figures or market data
                    
                    Text: {content}
                    """
                    
                    summary_response = self.openai_client.chat.completions.create(
                        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                        messages=[{"role": "user", "content": summary_prompt}],
                        max_tokens=500,
                        temperature=0.3
                    )
                    
                    # Entity extraction
                    entity_prompt = f"""
                    Extract key information from this text in JSON format:
                    {{
                        "companies": ["list of company names mentioned"],
                        "projects": ["list of project names and values"],
                        "technologies": ["list of technologies or innovations"],
                        "locations": ["list of geographic locations"],
                        "financial_figures": ["list of monetary values or market sizes"],
                        "key_dates": ["list of important dates mentioned"],
                        "risks_opportunities": ["list of risks or opportunities mentioned"]
                    }}
                    
                    Text: {content}
                    """
                    
                    entity_response = self.openai_client.chat.completions.create(
                        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                        messages=[{"role": "user", "content": entity_prompt}],
                        response_format={"type": "json_object"},
                        max_tokens=500,
                        temperature=0.1
                    )
                    
                    # Sentiment analysis
                    sentiment_prompt = f"""
                    Assess the overall sentiment of this text regarding built assets and construction market as:
                    - Positive, Negative, or Neutral
                    - Provide a brief justification (1-2 sentences)
                    
                    Format your response as JSON:
                    {{
                        "sentiment": "Positive/Negative/Neutral",
                        "justification": "brief explanation",
                        "confidence": 0.0-1.0
                    }}
                    
                    Text: {content}
                    """
                    
                    sentiment_response = self.openai_client.chat.completions.create(
                        model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                        messages=[{"role": "user", "content": sentiment_prompt}],
                        response_format={"type": "json_object"},
                        max_tokens=200,
                        temperature=0.1
                    )
                    
                    # Parse responses
                    try:
                        entities_content = entity_response.choices[0].message.content
                        if entities_content:
                            entities = json.loads(entities_content)
                        else:
                            entities = {"error": "Empty response from entity extraction"}
                    except:
                        entities = {"error": "Failed to parse entity extraction"}
                    
                    try:
                        sentiment_content = sentiment_response.choices[0].message.content
                        if sentiment_content:
                            sentiment = json.loads(sentiment_content)
                        else:
                            sentiment = {"sentiment": "Neutral", "justification": "Empty response", "confidence": 0.0}
                    except:
                        sentiment = {"sentiment": "Neutral", "justification": "Analysis failed", "confidence": 0.0}
                    
                    analyzed_results.append({
                        'url': item['url'],
                        'title': item['title'],
                        'query': item.get('query', ''),
                        'word_count': item['word_count'],
                        'summary': summary_response.choices[0].message.content,
                        'entities': entities,
                        'sentiment': sentiment,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    })
                    
                    time.sleep(0.5)  # Rate limiting
                    
            except Exception as e:
                st.error(f"Failed to analyze content from {item['title']}: {str(e)}")
                analyzed_results.append({
                    'url': item['url'],
                    'title': item['title'],
                    'error': str(e),
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                })
        
        return analyzed_results
    
    def execute_market_scan(self, config, refinement_keywords="", direct_urls="", 
                          num_results=10, crawl_depth=0):
        """
        Execute complete market scan workflow
        """
        if not self.validate_api_keys():
            return []
        
        all_urls = []
        
        # Handle direct URLs if provided
        if direct_urls:
            url_list = [url.strip() for url in direct_urls.split('\n') if url.strip()]
            all_urls.extend([{'url': url, 'title': '', 'query': 'Direct URL'} for url in url_list])
        
        # Execute Google searches if no direct URLs or if we want both
        if not direct_urls or len(all_urls) < num_results:
            queries = self.construct_search_queries(config, refinement_keywords)
            if queries:
                search_results = self.execute_google_search(queries, num_results)
                all_urls.extend(search_results)
        
        if not all_urls:
            st.warning("No URLs found to crawl")
            return []
        
        # Remove duplicates
        seen_urls = set()
        unique_urls = []
        for url_info in all_urls:
            url = url_info['url']
            if url not in seen_urls:
                seen_urls.add(url)
                unique_urls.append(url_info)
        
        # Crawl URLs and extract content
        crawled_content = self.crawl_urls(unique_urls[:num_results], crawl_depth)
        
        if not crawled_content:
            st.warning("No content successfully crawled")
            return []
        
        # Analyze with OpenAI
        analyzed_results = self.analyze_with_openai(crawled_content)
        
        return analyzed_results

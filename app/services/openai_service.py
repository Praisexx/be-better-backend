from openai import OpenAI
from config import settings
from typing import Dict, Any
import json
import requests

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def search_similar_businesses(business_niche: str) -> list:
    """
    Search for real similar businesses using web search APIs
    Falls back to AI-generated suggestions if web search fails
    """
    try:
        # Use OpenAI to identify the business niche first
        niche_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extract the main business niche/industry from this data in 2-3 words. Be specific."},
                {"role": "user", "content": business_niche}
            ],
            temperature=0.3
        )
        niche = niche_response.choices[0].message.content.strip()
        
        print(f"Identified niche: {niche}")

        # Try to use web search API if available
        web_results = []
        
        # Option 1: Try Tavily API (if configured)
        tavily_api_key = settings.TAVILY_API_KEY if hasattr(settings, 'TAVILY_API_KEY') else None
        if tavily_api_key:
            try:
                tavily_response = requests.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": tavily_api_key,
                        "query": f"top companies in {niche} industry with websites",
                        "search_depth": "advanced",
                        "max_results": 10
                    },
                    timeout=10
                )
                if tavily_response.status_code == 200:
                    tavily_data = tavily_response.json()
                    web_results = tavily_data.get('results', [])
                    print(f"Tavily search returned {len(web_results)} results")
            except Exception as e:
                print(f"Tavily search failed: {e}")
        
        # Option 2: Try SerpAPI (if configured and Tavily didn't work)
        if not web_results:
            serpapi_key = settings.SERPAPI_KEY if hasattr(settings, 'SERPAPI_KEY') else None
            if serpapi_key:
                try:
                    serp_response = requests.get(
                        "https://serpapi.com/search",
                        params={
                            "api_key": serpapi_key,
                            "q": f"top companies in {niche} industry",
                            "num": 10
                        },
                        timeout=10
                    )
                    if serp_response.status_code == 200:
                        serp_data = serp_response.json()
                        web_results = serp_data.get('organic_results', [])
                        print(f"SerpAPI search returned {len(web_results)} results")
                except Exception as e:
                    print(f"SerpAPI search failed: {e}")

        # If we have web results, use AI to structure them
        if web_results:
            # Prepare web results summary for AI
            web_summary = "\n".join([
                f"- {r.get('title', r.get('name', 'Unknown'))}: {r.get('snippet', r.get('description', r.get('content', '')[:200]))}"
                for r in web_results[:15]
            ])
            
            structure_response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": f"""You are a business research expert. Based on these web search results about the {niche} industry, extract and structure information about real companies.

For each company found, provide:
1. name: Exact company name
2. description: What they do (1-2 sentences)
3. website: Their website URL if available

Return as JSON with a 'businesses' array containing 8-10 companies.
Only include real, existing companies mentioned in the search results."""},
                    {"role": "user", "content": f"Web search results:\n{web_summary}\n\nExtract structured information about companies in the {niche} industry."}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(structure_response.choices[0].message.content)
            businesses = result.get('businesses', [])
            
            if businesses:
                print(f"Structured {len(businesses)} businesses from web results")
                return businesses

        # Fallback: Use AI knowledge to suggest real companies
        print("Using AI knowledge fallback for business suggestions")
        search_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"""You are a business research expert. Find REAL, EXISTING companies in the {niche} industry.
For each business, provide:
1. name: Exact company name (real company that exists)
2. description: Brief description (what they do)
3. website: Website URL if known

Return as JSON with a 'businesses' array. Include both well-known companies and emerging startups."""},
                {"role": "user", "content": f"List 8-10 real existing businesses/competitors in the {niche} industry based on your knowledge."}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(search_response.choices[0].message.content)
        businesses = result.get('businesses', result.get('companies', result.get('results', [])))

        return businesses if businesses else []

    except Exception as e:
        print(f"Business search failed: {e}")
        return []

def analyze_meta_ads(csv_data_summary: str) -> Dict[str, Any]:
    """
    Use OpenAI to analyze Meta Ads data and generate insights
    """

    system_prompt = """You are an expert marketing and business analyst.
Analyze the provided campaign/business data and provide comprehensive insights in the following structured format:

1. Performance Report: Key metrics analysis and trends
2. AI Insights: 5-7 actionable insights based on the data
3. Next Ad Plan: Specific recommendations for the next campaign
4. 30-Day Content Strategy: Week-by-week content plan
5. Creative Prompts: 5-10 creative ideas for ads
6. Captions + Hashtags: 5-10 ready-to-use captions with relevant hashtags

Return your response in valid JSON format with these exact keys:
{
  "performance_report": {},
  "ai_insights": [],
  "next_ad_plan": {},
  "content_strategy": {},
  "creative_prompts": [],
  "captions_hashtags": [],
  "business_context": "Brief description of the business/industry based on the data"
}
"""

    try:
        # Get main analysis
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Analyze this campaign data:\n\n{csv_data_summary}"}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # Extract business context for better company search
        business_context = result.get('business_context', csv_data_summary)
        
        # Search for real similar businesses from the web
        try:
            print("Searching for similar businesses...")
            similar_businesses = search_similar_businesses(business_context)
            result['similar_businesses'] = similar_businesses
            print(f"Found {len(similar_businesses)} similar businesses")
        except Exception as e:
            print(f"Similar businesses search failed: {e}")
            result['similar_businesses'] = []

        return result

    except Exception as e:
        raise Exception(f"OpenAI analysis failed: {str(e)}")


"""
Official NewsAPI.org Integration
Fetches news using the official NewsAPI with filtered, clean responses
Only returns: title, content, source, and url
"""

import os
import requests
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()


def get_news(category: str = None, country: str = "us", query: str = None, max_results: int = 5) -> dict:
    """
    Fetch news from official NewsAPI.org
    
    Args:
        category (str): News category - 'general', 'technology', 'business', 
                       'entertainment', 'health', 'science', 'sports'
        country (str): Two-letter country code - 'us', 'in', 'gb', 'au', 'ca', etc.
        query (str): Search query (if provided, ignores category/country)
        max_results (int): Maximum number of articles to return (default: 5)
    
    Returns:
        dict: Filtered news articles with only useful information
    """
    
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key:
        return {"error": "NEWSAPI_KEY not found in environment variables"}
    
    try:
        # Use everything endpoint for search queries, top-headlines for categories
        if query:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "apiKey": api_key,
                "pageSize": max_results,
                "sortBy": "publishedAt",
                "language": "en"
            }
        else:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "apiKey": api_key,
                "pageSize": max_results,
                "language": "en"
            }
            
            if category:
                params["category"] = category
            if country and not query:  # Country only works with top-headlines
                params["country"] = country
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") != "ok":
            return {"error": f"API error: {data.get('message', 'Unknown error')}"}
        
        articles = data.get("articles", [])
        
        if not articles:
            return {
                "error": "No articles found",
                "total": 0
            }
        
        # Filter articles to only useful information
        filtered_articles = []
        for article in articles:
            filtered_articles.append({
                "title": article.get("title", "No title"),
                "content": article.get("content") or article.get("description", "No content available"),
                "source": article.get("source", {}).get("name", "Unknown source"),
                "url": article.get("url", "")
            })
        
        return {
            "articles": filtered_articles,
            "total": len(filtered_articles),
            "category": category,
            "country": country,
            "query": query
        }
    
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch news: {str(e)}"}
    except Exception as e:
        return {"error": f"Error: {str(e)}"}


def get_news_formatted(category: str = None, country: str = "us", query: str = None, max_results: int = 5, **kwargs) -> str:
    """
    Get news and format it as a readable string for AI assistant.
    Only returns title, content, source, and URL - no images or extra data.
    
    Args:
        category (str): News category
        country (str): Two-letter country code
        query (str): Search query
        max_results (int): Maximum articles to return
        **kwargs: Additional arguments (ignored for compatibility)
    
    Returns:
        str: Formatted news text with only useful information
    """
    result = get_news(category, country, query, max_results)
    
    # Handle errors
    if "error" in result:
        return f"❌ {result['error']}"
    
    articles = result.get("articles", [])
    if not articles:
        return "❌ No news articles found"
    
    # Format output
    output = "📰 NEWS RESULTS\n"
    output += "=" * 50 + "\n\n"
    
    if result.get("query"):
        output += f"🔍 Search: {result['query']}\n\n"
    elif result.get("category"):
        output += f"📂 Category: {result['category'].title()}\n"
        if result.get("country"):
            output += f"🌍 Country: {result['country'].upper()}\n"
        output += "\n"
    
    # Display articles
    for i, article in enumerate(articles, 1):
        output += f"{i}. **{article['title']}**\n"
        output += f"   📍 Source: {article['source']}\n"
        
        if article.get('content'):
            # Truncate very long content
            content = article['content']
            if len(content) > 300:
                content = content[:297] + "..."
            output += f"   📝 {content}\n"
        
        if article.get('url'):
            output += f"   🔗 {article['url']}\n"
        
        output += "\n"
    
    output += f"📊 Total articles: {result['total']}"
    
    return output


# Available categories
CATEGORIES = [
    'general',
    'technology',
    'business',
    'entertainment',
    'health',
    'science',
    'sports'
]

# Available countries
COUNTRIES = {
    'us': 'United States',
    'in': 'India',
    'gb': 'United Kingdom',
    'au': 'Australia',
    'ca': 'Canada',
    'ae': 'UAE',
    'ar': 'Argentina',
    'at': 'Austria',
    'be': 'Belgium',
    'br': 'Brazil',
    'bg': 'Bulgaria',
    'cn': 'China',
    'co': 'Colombia',
    'cz': 'Czech Republic',
    'eg': 'Egypt',
    'fr': 'France',
    'de': 'Germany',
    'gr': 'Greece',
    'hk': 'Hong Kong',
    'hu': 'Hungary',
    'id': 'Indonesia',
    'ie': 'Ireland',
    'il': 'Israel',
    'it': 'Italy',
    'jp': 'Japan',
    'my': 'Malaysia',
    'mx': 'Mexico',
    'nl': 'Netherlands',
    'nz': 'New Zealand',
    'ng': 'Nigeria',
    'no': 'Norway',
    'ph': 'Philippines',
    'pl': 'Poland',
    'pt': 'Portugal',
    'ro': 'Romania',
    'ru': 'Russia',
    'sa': 'Saudi Arabia',
    'sg': 'Singapore',
    'za': 'South Africa',
    'kr': 'South Korea',
    'se': 'Sweden',
    'ch': 'Switzerland',
    'tw': 'Taiwan',
    'th': 'Thailand',
    'tr': 'Turkey',
    'ua': 'Ukraine'
}

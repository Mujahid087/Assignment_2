

# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel
# import requests
# from bs4 import BeautifulSoup
# import difflib
# import re
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from functools import lru_cache
# import time
# from typing import List, Dict, Optional

# app = FastAPI(title="CDP Documentation API", 
#               description="API for searching and comparing Customer Data Platform documentation")

# class Query(BaseModel):
#     question: str

# # URLs for the CDP documentation
# CDP_DOCS = {
#     "segment": "https://segment.com/docs/?ref=nav",
#     "mparticle": "https://docs.mparticle.com/",
#     "lytics": "https://docs.lytics.com/",
#     "zeotap": "https://docs.zeotap.com/home/en-us/"
# }

# # Cache for storing scraped documentation to avoid repeated requests
# @lru_cache(maxsize=16)
# def get_documentation_cache(url: str) -> List[str]:
#     """Cache function for storing scraped documentation"""
#     return scrape_documentation(url)

# def get_selenium_driver():
#     """Create and configure a Selenium WebDriver"""
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
    
#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options
#         )
#         return driver
#     except Exception as e:
#         print(f"Error initializing Chrome driver: {e}")
#         return None

# def extract_keywords(question: str) -> List[str]:
#     """Extract meaningful keywords from a question"""
#     # Remove common words and punctuation
#     words = re.sub(r'[^\w\s]', '', question.lower()).split()
#     stopwords = ['how', 'to', 'what', 'is', 'are', 'the', 'in', 'on', 'for', 'a', 'an', 'of', 'and', 'or']
#     keywords = [word for word in words if word not in stopwords and len(word) > 2]
#     return keywords

# def calculate_relevance_score(text: str, keywords: List[str]) -> float:
#     """Calculate relevance score based on keyword matches"""
#     text_lower = text.lower()
#     score = 0
    
#     for keyword in keywords:
#         if keyword in text_lower:
#             # Give higher weight to keywords in headings or beginning of paragraphs
#             if keyword in text_lower[:50]:
#                 score += 2
#             else:
#                 score += 1
                
#     return score

# def scrape_documentation(url: str) -> List[str]:
#     """Scrape documentation using Requests & BeautifulSoup"""
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }
    
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code != 200:
#             return []
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         text_blocks = []
        
#         # Extract text from various sections with their headings context
#         for heading in soup.find_all(['h1', 'h2', 'h3']):
#             heading_text = heading.get_text().strip()
            
#             # Find next sibling elements until the next heading
#             siblings = []
#             next_elem = heading.find_next_sibling()
            
#             while next_elem and next_elem.name not in ['h1', 'h2', 'h3']:
#                 if next_elem.name == 'p' and next_elem.get_text().strip():
#                     siblings.append(next_elem.get_text().strip())
#                 next_elem = next_elem.find_next_sibling()
            
#             # Create a text block with heading and its content
#             if siblings:
#                 text_blocks.append(f"{heading_text}: {' '.join(siblings)}")
#             else:
#                 text_blocks.append(heading_text)
        
#         return text_blocks
    
#     except requests.RequestException as e:
#         print(f"Error scraping documentation: {e}")
#         return []

# def scrape_documentation_with_selenium(url: str) -> List[str]:
#     """Scrape documentation using Selenium for JavaScript-heavy sites"""
#     driver = get_selenium_driver()
    
#     if not driver:
#         return []
    
#     try:
#         driver.get(url)
#         # Wait for dynamic content to load
#         time.sleep(3)
        
#         page_source = driver.page_source
#         soup = BeautifulSoup(page_source, 'html.parser')
        
#         text_blocks = []
        
#         # Extract text from various sections with their headings context
#         for heading in soup.find_all(['h1', 'h2', 'h3']):
#             heading_text = heading.get_text().strip()
            
#             # Find next sibling elements until the next heading
#             siblings = []
#             next_elem = heading.find_next_sibling()
            
#             while next_elem and next_elem.name not in ['h1', 'h2', 'h3']:
#                 if next_elem.name == 'p' and next_elem.get_text().strip():
#                     siblings.append(next_elem.get_text().strip())
#                 next_elem = next_elem.find_next_sibling()
            
#             # Create a text block with heading and its content
#             if siblings:
#                 text_blocks.append(f"{heading_text}: {' '.join(siblings)}")
#             else:
#                 text_blocks.append(heading_text)
        
#         return text_blocks
    
#     except Exception as e:
#         print(f"Error with Selenium scraping: {e}")
#         return []
    
#     finally:
#         driver.quit()

# def find_relevant_content(query: str, text_blocks: List[str]) -> List[Dict]:
#     """Find and rank content relevant to the query"""
#     keywords = extract_keywords(query)
    
#     if not keywords:
#         # If no meaningful keywords found, fall back to fuzzy matching
#         best_matches = difflib.get_close_matches(query, text_blocks, n=5, cutoff=0.3)
#         return [{"text": match, "score": 1.0} for match in best_matches]
    
#     # Score each text block based on keyword matches
#     scored_blocks = []
#     for block in text_blocks:
#         score = calculate_relevance_score(block, keywords)
#         if score > 0:
#             scored_blocks.append({"text": block, "score": score})
    
#     # Sort by relevance score (highest first)
#     scored_blocks.sort(key=lambda x: x["score"], reverse=True)
    
#     # Return top 5 matches or fewer if not enough found
#     return scored_blocks[:5]

# @app.post("/ask")
# async def ask_question(query: Query):
#     """Endpoint to ask questions about a specific CDP"""
#     question = query.question.lower()
    
#     # Identify which CDP is being asked about
#     matched_cdp = None
#     for cdp in CDP_DOCS.keys():
#         if cdp in question:
#             matched_cdp = cdp
#             break
    
#     if not matched_cdp:
#         raise HTTPException(
#             status_code=400, 
#             detail="CDP not recognized in the question. Please specify one of: segment, mparticle, lytics, or zeotap."
#         )
    
#     # Try to get documentation from cache first
#     try:
#         text_blocks = get_documentation_cache(CDP_DOCS[matched_cdp])
#     except Exception:
#         text_blocks = []
    
#     # If cache failed or returned empty, try direct scraping
#     if not text_blocks:
#         text_blocks = scrape_documentation(CDP_DOCS[matched_cdp])
    
#     # If direct scraping failed, try Selenium as fallback
#     if not text_blocks:
#         text_blocks = scrape_documentation_with_selenium(CDP_DOCS[matched_cdp])
    
#     if not text_blocks:
#         return {
#             "answer": f"Unable to retrieve documentation for {matched_cdp}.", 
#             "suggestions": [
#                 "Check if the documentation site is accessible",
#                 "Try a different CDP",
#                 "Check your internet connection"
#             ]
#         }
    
#     # Find relevant content
#     results = find_relevant_content(question, text_blocks)
    
#     if not results:
#         return {
#             "answer": f"No relevant information found for your question about {matched_cdp}.", 
#             "suggestions": [
#                 "Try rephrasing your question",
#                 "Check for specific feature names or terminology",
#                 "Browse the documentation directly at " + CDP_DOCS[matched_cdp]
#             ]
#         }
    
#     # Format the results - THIS IS THE FIXED LINE
#     return {
#         "cdp": matched_cdp,
#         "answer": [result["text"] for result in results],  # Changed "results" to "answer"
#         "relevant_sections": len(results),
#         "documentation_url": CDP_DOCS[matched_cdp]
#     }

# # CDP comparison data
# CDP_COMPARISONS = {
#     "segment vs mparticle": {
#         "ease_of_use": "Segment has a more straightforward UI, while mParticle offers more granular controls that can have a steeper learning curve.",
#         "integrations": "Segment offers 300+ integrations; mParticle offers 175+ but with deeper enterprise platform integrations.",
#         "pricing": "Segment typically starts lower for small businesses; mParticle is enterprise-focused with higher minimum contracts.",
#         "data_governance": "mParticle offers more advanced data governance features than Segment's base plan."
#     },
#     "segment vs lytics": {
#         "core_focus": "Segment focuses on data collection and routing; Lytics emphasizes customer insights and personalization.",
#         "audience_building": "Lytics has more advanced ML-based audience segmentation; Segment offers simpler rule-based segmentation.",
#         "pricing_model": "Segment prices based on tracked users; Lytics prices based on active users and features.",
#         "implementation": "Segment typically has faster initial implementation; Lytics requires more configuration for its advanced features."
#     },
#     "mparticle vs lytics": {
#         "platform_approach": "mParticle is a broader data platform; Lytics focuses more on activation and personalization use cases.",
#         "enterprise_features": "mParticle offers more enterprise governance features; Lytics emphasizes real-time decisioning.",
#         "industry_focus": "mParticle has stronger presence in retail and media; Lytics in publishing and subscription services.",
#         "technical_requirements": "Both require technical implementation, with mParticle generally requiring more developer resources."
#     },
#     "segment vs zeotap": {
#         "global_presence": "Zeotap has stronger presence in European and Asian markets; Segment is stronger in North America.",
#         "identity_resolution": "Zeotap offers more advanced identity resolution capabilities compared to Segment.",
#         "data_enrichment": "Zeotap provides more built-in third-party data enrichment options than Segment.",
#         "compliance": "Both offer strong compliance features, with Zeotap emphasizing GDPR compliance more heavily."
#     }
# }

# @app.post("/compare")
# async def compare_cdp(query: Query):
#     """Endpoint for comparing different CDPs"""
#     question = query.question.lower()
    
#     # Find which comparison is being requested
#     matched_comparison = None
    
#     # First, try to match exact comparison strings
#     for comparison in CDP_COMPARISONS.keys():
#         if comparison in question or comparison.replace(" vs ", " versus ") in question:
#             matched_comparison = comparison
#             break
    
#     # If no exact match, try to detect individual CDPs
#     if not matched_comparison:
#         mentioned_cdps = []
#         for cdp in CDP_DOCS.keys():
#             if cdp in question:
#                 mentioned_cdps.append(cdp)
        
#         # If we found at least 2 CDPs, try to construct a comparison
#         if len(mentioned_cdps) >= 2:
#             # Try all possible pairs in order mentioned
#             for i in range(len(mentioned_cdps)):
#                 for j in range(i+1, len(mentioned_cdps)):
#                     possible_comparison = f"{mentioned_cdps[i]} vs {mentioned_cdps[j]}"
#                     reverse_comparison = f"{mentioned_cdps[j]} vs {mentioned_cdps[i]}"
                    
#                     if possible_comparison in CDP_COMPARISONS:
#                         matched_comparison = possible_comparison
#                         break
#                     elif reverse_comparison in CDP_COMPARISONS:
#                         matched_comparison = reverse_comparison
#                         break
                
#                 if matched_comparison:
#                     break
    
#     # If still no match but "compare" or "vs" is in the question, generate a generic response
#     if not matched_comparison and ("compare" in question or " vs " in question or "versus" in question):
#         # Extract all mentioned CDPs
#         mentioned_cdps = [cdp for cdp in CDP_DOCS.keys() if cdp in question]
        
#         if len(mentioned_cdps) >= 2:
#             # Create a basic comparison for the first two mentioned CDPs
#             cdp1, cdp2 = mentioned_cdps[0], mentioned_cdps[1]
            
#             # Generate generic comparison information
#             generic_comparison = {
#                 "platforms": f"Both {cdp1} and {cdp2} are customer data platforms with different strengths.",
#                 "suggestion": f"For a detailed comparison between {cdp1} and {cdp2}, please consult their documentation directly."
#             }
            
#             return {
#                 "comparison": f"{cdp1} vs {cdp2}",
#                 "cdps": [cdp1, cdp2],
#                 "aspects": generic_comparison,
#                 "note": "This is a generic comparison. For more specific information, try asking about particular aspects.",
#                 "documentation_urls": {cdp: CDP_DOCS[cdp] for cdp in [cdp1, cdp2] if cdp in CDP_DOCS}
#             }
#         else:
#             # Not enough CDPs mentioned for comparison
#             raise HTTPException(
#                 status_code=400, 
#                 detail="Please mention at least two CDPs to compare. Available CDPs are: " + ", ".join(CDP_DOCS.keys())
#             )
    
#     if not matched_comparison:
#         raise HTTPException(
#             status_code=400, 
#             detail="Comparison not recognized. Please specify two CDPs to compare, like 'segment vs mparticle'."
#         )
    
#     # Extract keywords to determine which aspects to focus on
#     keywords = extract_keywords(question)
#     focus_areas = []
    
#     comparison_data = CDP_COMPARISONS[matched_comparison]
    
#     # Map of common terms to comparison aspects
#     focus_aspect_map = {
#         "use": "ease_of_use",
#         "user": "ease_of_use",
#         "interface": "ease_of_use",
#         "ui": "ease_of_use",
#         "ux": "ease_of_use",
#         "integrations": "integrations",
#         "connect": "integrations",
#         "connections": "integrations",
#         "price": "pricing",
#         "cost": "pricing",
#         "pricing": "pricing",
#         "governance": "data_governance",
#         "compliance": "compliance",
#         "gdpr": "compliance",
#         "ccpa": "compliance",
#         "audience": "audience_building",
#         "segment": "audience_building",
#         "identity": "identity_resolution",
#         "resolution": "identity_resolution",
#         "implementation": "implementation",
#         "setup": "implementation",
#         "install": "implementation",
#         "enterprise": "enterprise_features",
#         "focus": "core_focus",
#         "approach": "platform_approach",
#         "global": "global_presence",
#         "region": "global_presence",
#         "enrichment": "data_enrichment",
#         "industry": "industry_focus",
#         "technical": "technical_requirements"
#     }
    
#     # Check for aspect-related keywords
#     for keyword in keywords:
#         for term, aspect in focus_aspect_map.items():
#             if keyword == term or keyword.startswith(term) or term in keyword:
#                 if aspect in comparison_data and aspect not in focus_areas:
#                     focus_areas.append(aspect)
    
#     # If no specific focus areas found, include all
#     if not focus_areas:
#         focus_areas = list(comparison_data.keys())
    
#     # Create focused response
#     focused_comparison = {area: comparison_data[area] for area in focus_areas if area in comparison_data}
    
#     # If somehow we ended up with no data, include everything
#     if not focused_comparison:
#         focused_comparison = comparison_data
    
#     cdps = matched_comparison.split(" vs ")
    
#     return {
#         "comparison": matched_comparison,
#         "cdps": cdps,
#         "aspects": focused_comparison,
#         "documentation_urls": {cdp: CDP_DOCS[cdp] for cdp in cdps if cdp in CDP_DOCS}
#     }


# @app.post("/advanced")
# async def advanced_question(query: Query):
#     """Endpoint for advanced how-to questions about CDPs"""
#     question = query.question.lower()
    
#     # Identify which CDP and advanced topic is being asked about
#     matched_cdp = None
#     for cdp in CDP_DOCS.keys():
#         if cdp in question:
#             matched_cdp = cdp
#             break
    
#     if not matched_cdp:
#         raise HTTPException(
#             status_code=400, 
#             detail="CDP not recognized in the question. Please specify one of: segment, mparticle, lytics, or zeotap."
#         )
    
#     # Advanced topics database
#     advanced_topics = {
#         "segment": {
#             "tracking_plan": "To implement a tracking plan in Segment, follow these steps:\n1. Define your events and properties\n2. Use Segment's Protocols feature to enforce your plan\n3. Set up tracking in your codebase using the appropriate SDK\n4. Validate implementation with Segment's debugger",
#             "identity_resolution": "For advanced identity resolution in Segment:\n1. Use userId and anonymousId consistently\n2. Implement .identify() calls at login/registration\n3. Consider using Personas for cross-device identity resolution\n4. Use ID mapping tables for legacy systems",
#             "custom_destination": "To create a custom destination in Segment:\n1. Use Segment's Function sources\n2. Write a serverless function to transform and route data\n3. Deploy the function to your preferred cloud provider\n4. Connect the function to Segment as a destination",
#             "data_governance": "For implementing data governance in Segment:\n1. Use Protocols to enforce data quality\n2. Set up workspace permissions for team access control\n3. Implement privacy settings for GDPR/CCPA compliance\n4. Use filtering rules to control data flow to destinations"
#         },
#         "mparticle": {
#             "audience_builder": "For advanced audience building in mParticle:\n1. Use mParticle's Audience Builder to create segments\n2. Utilize calculated attributes for complex criteria\n3. Apply behavioral filters based on event frequency/recency\n4. Leverage lookalike modeling for expanded audiences",
#             "data_planning": "To implement a data plan in mParticle:\n1. Define your data model in mParticle's Data Planning UI\n2. Apply validations and transformations\n3. Link the plan to your workspaces\n4. Monitor data quality in the Data Master dashboard",
#             "identity_strategy": "For identity strategies in mParticle:\n1. Configure the Identity Hierarchy in settings\n2. Implement IDSync to capture identifiers\n3. Use Identity Priority to resolve conflicts\n4. Set up cross-device tracking with household IDs"
#         },
#         "lytics": {
#             "behavioral_scoring": "To implement behavioral scoring in Lytics:\n1. Define your scoring model in the Lytics UI\n2. Select relevant user behaviors to track\n3. Apply weighting to different actions\n4. Set up score decay for time-based relevance",
#             "content_affinity": "For content affinity modeling in Lytics:\n1. Ensure content tags are properly set up\n2. Enable content affinity modeling in settings\n3. Create segments based on content preferences\n4. Use these insights for content recommendations"
#         },
#         "zeotap": {
#             "identity_resolution": "For advanced identity resolution in Zeotap:\n1. Implement the Zeotap ID+ solution\n2. Connect first-party data sources\n3. Configure match rules for cross-device linking\n4. Monitor match rates in the Zeotap dashboard",
#             "compliance_workflows": "To set up compliance workflows in Zeotap:\n1. Configure data retention policies\n2. Set up consent management integration\n3. Implement data subject request handling\n4. Configure regional data storage settings"
#         }
#     }
    
#     # Extract keywords to determine which advanced topic is being asked about
#     keywords = extract_keywords(question)
    
#     # Map common keywords to topics
#     topic_keyword_map = {
#         "tracking plan": "tracking_plan",
#         "data plan": "data_planning",
#         "identity": "identity_resolution",
#         "id resolution": "identity_resolution",
#         "custom destination": "custom_destination",
#         "destination": "custom_destination",
#         "governance": "data_governance",
#         "compliance": "compliance_workflows",
#         "audience": "audience_builder",
#         "segment": "audience_builder",
#         "behavioral": "behavioral_scoring",
#         "scoring": "behavioral_scoring",
#         "content": "content_affinity",
#         "affinity": "content_affinity"
#     }
    
#     # Find matching topic
#     matched_topic = None
#     for phrase, topic in topic_keyword_map.items():
#         if phrase in question and topic in advanced_topics.get(matched_cdp, {}):
#             matched_topic = topic
#             break
    
#     if not matched_topic:
#         # Try to match any available topic for the CDP
#         for topic in advanced_topics.get(matched_cdp, {}):
#             topic_words = topic.replace("_", " ").split()
#             if any(word in question for word in topic_words):
#                 matched_topic = topic
#                 break
    
#     if not matched_topic:
#         # If still no match, provide general guidance
#         return {
#             "cdp": matched_cdp,
#             "answer": f"Your question about advanced functionality in {matched_cdp} couldn't be matched to a specific topic.",
#             "available_topics": list(advanced_topics.get(matched_cdp, {}).keys()),
#             "suggestion": f"Try asking about one of the available advanced topics for {matched_cdp}."
#         }
    
#     # Return the matched topic information
#     return {
#         "cdp": matched_cdp,
#         "topic": matched_topic,
#         "answer": advanced_topics[matched_cdp][matched_topic],
#         "documentation_url": CDP_DOCS[matched_cdp]
#     }

# @app.get("/health")
# async def health_check():
#     """Endpoint for system health check"""
#     return {"status": "healthy", "version": "1.0.0"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)




# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel
# import requests
# from bs4 import BeautifulSoup
# import difflib
# import re
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from functools import lru_cache
# import time
# from typing import List, Dict, Optional

# app = FastAPI(
#     title="CDP Documentation API", 
#     description="API for searching and comparing Customer Data Platform documentation"
# )

# class Query(BaseModel):
#     question: str

# # URLs for the CDP documentation
# CDP_DOCS = {
#     "segment": "https://segment.com/docs/?ref=nav",
#     "mparticle": "https://docs.mparticle.com/",
#     "lytics": "https://docs.lytics.com/",
#     "zeotap": "https://docs.zeotap.com/home/en-us/"
# }

# # Cache for storing scraped documentation to avoid repeated requests
# @lru_cache(maxsize=16)
# def get_documentation_cache(url: str) -> List[str]:
#     """Cache function for storing scraped documentation"""
#     return scrape_documentation(url)

# def get_selenium_driver():
#     """Create and configure a Selenium WebDriver"""
#     options = Options()
#     options.add_argument("--headless")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
    
#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options
#         )
#         return driver
#     except Exception as e:
#         print(f"Error initializing Chrome driver: {e}")
#         return None

# def extract_keywords(question: str) -> List[str]:
#     """Extract meaningful keywords from a question"""
#     # Remove common words and punctuation
#     words = re.sub(r'[^\w\s]', '', question.lower()).split()
#     stopwords = ['how', 'to', 'what', 'is', 'are', 'the', 'in', 'on', 'for', 'a', 'an', 'of', 'and', 'or']
#     keywords = [word for word in words if word not in stopwords and len(word) > 2]
#     return keywords

# def calculate_relevance_score(text: str, keywords: List[str]) -> float:
#     """Calculate relevance score based on keyword matches"""
#     text_lower = text.lower()
#     score = 0
    
#     for keyword in keywords:
#         if keyword in text_lower:
#             # Give higher weight to keywords in headings or beginning of paragraphs
#             if keyword in text_lower[:50]:
#                 score += 2
#             else:
#                 score += 1
                
#     return score

# def scrape_documentation(url: str) -> List[str]:
#     """Scrape documentation using Requests & BeautifulSoup"""
#     headers = {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
#     }
    
#     try:
#         response = requests.get(url, headers=headers, timeout=10)
#         if response.status_code != 200:
#             return []
        
#         soup = BeautifulSoup(response.text, 'html.parser')
#         text_blocks = []
        
#         # Extract text from various sections with their headings context
#         for heading in soup.find_all(['h1', 'h2', 'h3']):
#             heading_text = heading.get_text().strip()
            
#             # Find next sibling elements until the next heading
#             siblings = []
#             next_elem = heading.find_next_sibling()
            
#             while next_elem and next_elem.name not in ['h1', 'h2', 'h3']:
#                 if next_elem.name == 'p' and next_elem.get_text().strip():
#                     siblings.append(next_elem.get_text().strip())
#                 next_elem = next_elem.find_next_sibling()
            
#             # Create a text block with heading and its content
#             if siblings:
#                 text_blocks.append(f"{heading_text}: {' '.join(siblings)}")
#             else:
#                 text_blocks.append(heading_text)
        
#         return text_blocks
    
#     except requests.RequestException as e:
#         print(f"Error scraping documentation: {e}")
#         return []

# def scrape_documentation_with_selenium(url: str) -> List[str]:
#     """Scrape documentation using Selenium for JavaScript-heavy sites"""
#     driver = get_selenium_driver()
    
#     if not driver:
#         return []
    
#     try:
#         driver.get(url)
#         # Wait for dynamic content to load
#         time.sleep(3)
        
#         page_source = driver.page_source
#         soup = BeautifulSoup(page_source, 'html.parser')
        
#         text_blocks = []
        
#         # Extract text from various sections with their headings context
#         for heading in soup.find_all(['h1', 'h2', 'h3']):
#             heading_text = heading.get_text().strip()
            
#             # Find next sibling elements until the next heading
#             siblings = []
#             next_elem = heading.find_next_sibling()
            
#             while next_elem and next_elem.name not in ['h1', 'h2', 'h3']:
#                 if next_elem.name == 'p' and next_elem.get_text().strip():
#                     siblings.append(next_elem.get_text().strip())
#                 next_elem = next_elem.find_next_sibling()
            
#             # Create a text block with heading and its content
#             if siblings:
#                 text_blocks.append(f"{heading_text}: {' '.join(siblings)}")
#             else:
#                 text_blocks.append(heading_text)
        
#         return text_blocks
    
#     except Exception as e:
#         print(f"Error with Selenium scraping: {e}")
#         return []
    
#     finally:
#         driver.quit()

# def find_relevant_content(query: str, text_blocks: List[str]) -> List[Dict]:
#     """Find and rank content relevant to the query"""
#     keywords = extract_keywords(query)
    
#     if not keywords:
#         # If no meaningful keywords found, fall back to fuzzy matching
#         best_matches = difflib.get_close_matches(query, text_blocks, n=5, cutoff=0.3)
#         return [{"text": match, "score": 1.0} for match in best_matches]
    
#     # Score each text block based on keyword matches
#     scored_blocks = []
#     for block in text_blocks:
#         score = calculate_relevance_score(block, keywords)
#         if score > 0:
#             scored_blocks.append({"text": block, "score": score})
    
#     # Sort by relevance score (highest first)
#     scored_blocks.sort(key=lambda x: x["score"], reverse=True)
    
#     # Return top 5 matches or fewer if not enough found
#     return scored_blocks[:5]

# @app.post("/ask")
# async def ask_question(query: Query):
#     """Endpoint to ask questions about a specific CDP"""
#     question = query.question.lower()
    
#     # Identify which CDP is being asked about
#     matched_cdp = None
#     for cdp in CDP_DOCS.keys():
#         if cdp in question:
#             matched_cdp = cdp
#             break
    
#     if not matched_cdp:
#         raise HTTPException(
#             status_code=400, 
#             detail="CDP not recognized in the question. Please specify one of: segment, mparticle, lytics, or zeotap."
#         )
    
#     # Try to get documentation from cache first
#     try:
#         text_blocks = get_documentation_cache(CDP_DOCS[matched_cdp])
#     except Exception:
#         text_blocks = []
    
#     # If cache failed or returned empty, try direct scraping
#     if not text_blocks:
#         text_blocks = scrape_documentation(CDP_DOCS[matched_cdp])
    
#     # If direct scraping failed, try Selenium as fallback
#     if not text_blocks:
#         text_blocks = scrape_documentation_with_selenium(CDP_DOCS[matched_cdp])
    
#     if not text_blocks:
#         return {
#             "answer": f"Unable to retrieve documentation for {matched_cdp}.", 
#             "suggestions": [
#                 "Check if the documentation site is accessible",
#                 "Try a different CDP",
#                 "Check your internet connection"
#             ]
#         }
    
#     # Find relevant content
#     results = find_relevant_content(question, text_blocks)
    
#     if not results:
#         return {
#             "answer": f"No relevant information found for your question about {matched_cdp}.", 
#             "suggestions": [
#                 "Try rephrasing your question",
#                 "Check for specific feature names or terminology",
#                 "Browse the documentation directly at " + CDP_DOCS[matched_cdp]
#             ]
#         }
    
#     # Format the results
#     return {
#         "cdp": matched_cdp,
#         "answer": [result["text"] for result in results],
#         "relevant_sections": len(results),
#         "documentation_url": CDP_DOCS[matched_cdp]
#     }

# # CDP comparison data
# CDP_COMPARISONS = {
#     "segment vs mparticle": {
#         "ease_of_use": "Segment has a more straightforward UI, while mParticle offers more granular controls that can have a steeper learning curve.",
#         "integrations": "Segment offers 300+ integrations; mParticle offers 175+ but with deeper enterprise platform integrations.",
#         "pricing": "Segment typically starts lower for small businesses; mParticle is enterprise-focused with higher minimum contracts.",
#         "data_governance": "mParticle offers more advanced data governance features than Segment's base plan."
#     },
#     "segment vs lytics": {
#         "core_focus": "Segment focuses on data collection and routing; Lytics emphasizes customer insights and personalization.",
#         "audience_building": "Lytics has more advanced ML-based audience segmentation; Segment offers simpler rule-based segmentation.",
#         "pricing_model": "Segment prices based on tracked users; Lytics prices based on active users and features.",
#         "implementation": "Segment typically has faster initial implementation; Lytics requires more configuration for its advanced features."
#     },
#     "mparticle vs lytics": {
#         "platform_approach": "mParticle is a broader data platform; Lytics focuses more on activation and personalization use cases.",
#         "enterprise_features": "mParticle offers more enterprise governance features; Lytics emphasizes real-time decisioning.",
#         "industry_focus": "mParticle has stronger presence in retail and media; Lytics in publishing and subscription services.",
#         "technical_requirements": "Both require technical implementation, with mParticle generally requiring more developer resources."
#     },
#     "segment vs zeotap": {
#         "global_presence": "Zeotap has stronger presence in European and Asian markets; Segment is stronger in North America.",
#         "identity_resolution": "Zeotap offers more advanced identity resolution capabilities compared to Segment.",
#         "data_enrichment": "Zeotap provides more built-in third-party data enrichment options than Segment.",
#         "compliance": "Both offer strong compliance features, with Zeotap emphasizing GDPR compliance more heavily."
#     }
# }

# @app.post("/compare")
# async def compare_cdp(query: Query):
#     """Endpoint for comparing different CDPs"""
#     question = query.question.lower()
    
#     # Find which comparison is being requested
#     matched_comparison = None
    
#     # First, try to match exact comparison strings
#     for comparison in CDP_COMPARISONS.keys():
#         if comparison in question or comparison.replace(" vs ", " versus ") in question:
#             matched_comparison = comparison
#             break
    
#     # If no exact match, try to detect individual CDPs
#     if not matched_comparison:
#         mentioned_cdps = []
#         for cdp in CDP_DOCS.keys():
#             if cdp in question:
#                 mentioned_cdps.append(cdp)
        
#         # If we found at least 2 CDPs, try to construct a comparison
#         if len(mentioned_cdps) >= 2:
#             # Try all possible pairs in order mentioned
#             for i in range(len(mentioned_cdps)):
#                 for j in range(i+1, len(mentioned_cdps)):
#                     possible_comparison = f"{mentioned_cdps[i]} vs {mentioned_cdps[j]}"
#                     reverse_comparison = f"{mentioned_cdps[j]} vs {mentioned_cdps[i]}"
                    
#                     if possible_comparison in CDP_COMPARISONS:
#                         matched_comparison = possible_comparison
#                         break
#                     elif reverse_comparison in CDP_COMPARISONS:
#                         matched_comparison = reverse_comparison
#                         break
                
#                 if matched_comparison:
#                     break
    
#     # If still no match but "compare" or "vs" is in the question, generate a generic response
#     if not matched_comparison and ("compare" in question or " vs " in question or "versus" in question):
#         # Extract all mentioned CDPs
#         mentioned_cdps = [cdp for cdp in CDP_DOCS.keys() if cdp in question]
        
#         if len(mentioned_cdps) >= 2:
#             # Create a basic comparison for the first two mentioned CDPs
#             cdp1, cdp2 = mentioned_cdps[0], mentioned_cdps[1]
            
#             # Generate generic comparison information
#             generic_comparison = {
#                 "platforms": f"Both {cdp1} and {cdp2} are customer data platforms with different strengths.",
#                 "suggestion": f"For a detailed comparison between {cdp1} and {cdp2}, please consult their documentation directly."
#             }
            
#             return {
#                 "comparison": f"{cdp1} vs {cdp2}",
#                 "cdps": [cdp1, cdp2],
#                 "aspects": generic_comparison,
#                 "note": "This is a generic comparison. For more specific information, try asking about particular aspects.",
#                 "documentation_urls": {cdp: CDP_DOCS[cdp] for cdp in [cdp1, cdp2] if cdp in CDP_DOCS}
#             }
#         else:
#             # Not enough CDPs mentioned for comparison
#             raise HTTPException(
#                 status_code=400, 
#                 detail="Please mention at least two CDPs to compare. Available CDPs are: " + ", ".join(CDP_DOCS.keys())
#             )
    
#     if not matched_comparison:
#         raise HTTPException(
#             status_code=400, 
#             detail="Comparison not recognized. Please specify two CDPs to compare, like 'segment vs mparticle'."
#         )
    
#     # Extract keywords to determine which aspects to focus on
#     keywords = extract_keywords(question)
#     focus_areas = []
    
#     comparison_data = CDP_COMPARISONS[matched_comparison]
    
#     # Map of common terms to comparison aspects
#     focus_aspect_map = {
#         "use": "ease_of_use",
#         "user": "ease_of_use",
#         "interface": "ease_of_use",
#         "ui": "ease_of_use",
#         "ux": "ease_of_use",
#         "integrations": "integrations",
#         "connect": "integrations",
#         "connections": "integrations",
#         "price": "pricing",
#         "cost": "pricing",
#         "pricing": "pricing",
#         "governance": "data_governance",
#         "compliance": "compliance",
#         "gdpr": "compliance",
#         "ccpa": "compliance",
#         "audience": "audience_building",
#         "segment": "audience_building",
#         "identity": "identity_resolution",
#         "resolution": "identity_resolution",
#         "implementation": "implementation",
#         "setup": "implementation",
#         "install": "implementation",
#         "enterprise": "enterprise_features",
#         "focus": "core_focus",
#         "approach": "platform_approach",
#         "global": "global_presence",
#         "region": "global_presence",
#         "enrichment": "data_enrichment",
#         "industry": "industry_focus",
#         "technical": "technical_requirements"
#     }
    
#     # Check for aspect-related keywords
#     for keyword in keywords:
#         for term, aspect in focus_aspect_map.items():
#             if keyword == term or keyword.startswith(term) or term in keyword:
#                 if aspect in comparison_data and aspect not in focus_areas:
#                     focus_areas.append(aspect)
    
#     # If no specific focus areas found, include all
#     if not focus_areas:
#         focus_areas = list(comparison_data.keys())
    
#     # Create focused response
#     focused_comparison = {area: comparison_data[area] for area in focus_areas if area in comparison_data}
    
#     # If somehow we ended up with no data, include everything
#     if not focused_comparison:
#         focused_comparison = comparison_data
    
#     cdps = matched_comparison.split(" vs ")
    
#     return {
#         "comparison": matched_comparison,
#         "cdps": cdps,
#         "aspects": focused_comparison,
#         "documentation_urls": {cdp: CDP_DOCS[cdp] for cdp in cdps if cdp in CDP_DOCS}
#     }
    
# @app.post("/advanced")
# async def advanced_question(query: Query):
#     """Endpoint for advanced how-to questions about CDPs"""
#     question = query.question.lower()
    
#     # Identify which CDP and advanced topic is being asked about
#     matched_cdp = None
#     for cdp in CDP_DOCS.keys():
#         if cdp in question:
#             matched_cdp = cdp
#             break
    
#     if not matched_cdp:
#         raise HTTPException(
#             status_code=400, 
#             detail="CDP not recognized in the question. Please specify one of: segment, mparticle, lytics, or zeotap."
#         )
    
#     # Advanced topics database
#     advanced_topics = {
#         "segment": {
#             "tracking_plan": "To implement a tracking plan in Segment, follow these steps:\n1. Define your events and properties\n2. Use Segment's Protocols feature to enforce your plan\n3. Set up tracking in your codebase using the appropriate SDK\n4. Validate implementation with Segment's debugger",
#             "identity_resolution": "For advanced identity resolution in Segment:\n1. Use userId and anonymousId consistently\n2. Implement .identify() calls at login/registration\n3. Consider using Personas for cross-device identity resolution\n4. Use ID mapping tables for legacy systems",
#             "custom_destination": "To create a custom destination in Segment:\n1. Use Segment's Function sources\n2. Write a serverless function to transform and route data\n3. Deploy the function to your preferred cloud provider\n4. Connect the function to Segment as a destination",
#             "data_governance": "For implementing data governance in Segment:\n1. Use Protocols to enforce data quality\n2. Set up workspace permissions for team access control\n3. Implement privacy settings for GDPR/CCPA compliance\n4. Use filtering rules to control data flow to destinations"
#         },
#         "mparticle": {
#             "audience_builder": "For advanced audience building in mParticle:\n1. Use mParticle's Audience Builder to create segments\n2. Utilize calculated attributes for complex criteria\n3. Apply behavioral filters based on event frequency/recency\n4. Leverage lookalike modeling for expanded audiences",
#             "data_planning": "To implement a data plan in mParticle:\n1. Define your data model in mParticle's Data Planning UI\n2. Apply validations and transformations\n3. Link the plan to your workspaces\n4. Monitor data quality in the Data Master dashboard",
#             "identity_strategy": "For identity strategies in mParticle:\n1. Configure the Identity Hierarchy in settings\n2. Implement IDSync to capture identifiers\n3. Use Identity Priority to resolve conflicts\n4. Set up cross-device tracking with household IDs"
#         },
#         "lytics": {
#             "behavioral_scoring": "To implement behavioral scoring in Lytics:\n1. Define your scoring model in the Lytics UI\n2. Select relevant user behaviors to track\n3. Apply weighting to different actions\n4. Set up score decay for time-based relevance",
#             "content_affinity": "For content affinity modeling in Lytics:\n1. Ensure content tags are properly set up\n2. Enable content affinity modeling in settings\n3. Create segments based on content preferences\n4. Use these insights for content recommendations"
#         },
#         "zeotap": {
#             "identity_resolution": "For advanced identity resolution in Zeotap:\n1. Implement the Zeotap ID+ solution\n2. Connect first-party data sources\n3. Configure match rules for cross-device linking\n4. Monitor match rates in the Zeotap dashboard",
#             "compliance_workflows": "To set up compliance workflows in Zeotap:\n1. Configure data retention policies\n2. Set up consent management integration\n3. Implement data subject request handling\n4. Configure regional data storage settings"
#         }
#     }
    
#     # Extract keywords to determine which advanced topic is being asked about
#     keywords = extract_keywords(question)
    
#     # Map common keywords to topics
#     topic_keyword_map = {
#         "tracking plan": "tracking_plan",
#         "data plan": "data_planning",
#         "identity": "identity_resolution",
#         "id resolution": "identity_resolution",
#         "custom destination": "custom_destination",
#         "destination": "custom_destination",
#         "governance": "data_governance",
#         "compliance": "compliance_workflows",
#         "audience": "audience_builder",
#         "segment": "audience_builder",
#         "behavioral": "behavioral_scoring",
#         "scoring": "behavioral_scoring",
#         "content": "content_affinity",
#         "affinity": "content_affinity"
#     }
    
#     # Find matching topic
#     matched_topic = None
#     for phrase, topic in topic_keyword_map.items():
#         if phrase in question and topic in advanced_topics.get(matched_cdp, {}):
#             matched_topic = topic
#             break
    
#     if not matched_topic:
#         # Try to match any available topic for the CDP
#         for topic in advanced_topics.get(matched_cdp, {}):
#             topic_words = topic.replace("_", " ").split()
#             if any(word in question for word in topic_words):
#                 matched_topic = topic
#                 break
    
#     if not matched_topic:
#         # If still no match, provide general guidance
#         return {
#             "cdp": matched_cdp,
#             "answer": f"Your question about advanced functionality in {matched_cdp} couldn't be matched to a specific topic.",
#             "available_topics": list(advanced_topics.get(matched_cdp, {}).keys()),
#             "suggestion": f"Try asking about one of the available advanced topics for {matched_cdp}."
#         }
    
#     # Return the matched topic information
#     return {
#         "cdp": matched_cdp,
#         "topic": matched_topic,
#         "answer": advanced_topics[matched_cdp][matched_topic],
#         "documentation_url": CDP_DOCS[matched_cdp]
#     }

# @app.get("/health")
# async def health_check():
#     """Endpoint for system health check"""
#     return {"status": "healthy", "version": "1.0.0"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)



from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import difflib
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from functools import lru_cache
import time
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CDP Documentation API",
    description="API for searching and comparing Customer Data Platform documentation"
)

class Query(BaseModel):
    question: str

# URLs for the CDP documentation
CDP_DOCS = {
    "segment": "https://segment.com/docs/?ref=nav",
    "mparticle": "https://docs.mparticle.com/",
    "lytics": "https://docs.lytics.com/",
    "zeotap": "https://docs.zeotap.com/home/en-us/"
}

# Cache for storing scraped documentation to avoid repeated requests
@lru_cache(maxsize=16)
def get_documentation_cache(url: str) -> List[str]:
    """Cache function for storing scraped documentation"""
    return scrape_documentation(url)

def get_selenium_driver():
    """Create and configure a Selenium WebDriver"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver
    except Exception as e:
        logger.error(f"Error initializing Chrome driver: {e}")
        return None

def extract_keywords(question: str) -> List[str]:
    """Extract meaningful keywords from a question"""
    words = re.sub(r'[^\w\s]', '', question.lower()).split()
    stopwords = {'how', 'to', 'what', 'is', 'are', 'the', 'in', 'on', 'for', 'a', 'an', 'of', 'and', 'or'}
    keywords = [word for word in words if word not in stopwords and len(word) > 2]
    return keywords

def calculate_relevance_score(text: str, keywords: List[str]) -> float:
    """Calculate relevance score based on keyword matches"""
    text_lower = text.lower()
    score = 0
    
    for keyword in keywords:
        if keyword in text_lower:
            # Give higher weight to keywords in headings or beginning of paragraphs
            if keyword in text_lower[:50]:
                score += 2
            else:
                score += 1
                
    return score

def scrape_documentation(url: str) -> List[str]:
    """Scrape documentation using Requests & BeautifulSoup"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text_blocks = []
        
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text().strip()
            siblings = []
            next_elem = heading.find_next_sibling()
            
            while next_elem and next_elem.name not in ['h1', 'h2', 'h3']:
                if next_elem.name == 'p' and next_elem.get_text().strip():
                    siblings.append(next_elem.get_text().strip())
                next_elem = next_elem.find_next_sibling()
            
            if siblings:
                text_blocks.append(f"{heading_text}: {' '.join(siblings)}")
            else:
                text_blocks.append(heading_text)
        
        return text_blocks
    
    except requests.RequestException as e:
        logger.error(f"Error scraping documentation from {url}: {e}")
        return []

def scrape_documentation_with_selenium(url: str) -> List[str]:
    """Scrape documentation using Selenium for JavaScript-heavy sites"""
    driver = get_selenium_driver()
    
    if not driver:
        return []
    
    try:
        driver.get(url)
        time.sleep(3)  # Wait for dynamic content to load
        
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        text_blocks = []
        
        for heading in soup.find_all(['h1', 'h2', 'h3']):
            heading_text = heading.get_text().strip()
            siblings = []
            next_elem = heading.find_next_sibling()
            
            while next_elem and next_elem.name not in ['h1', 'h2', 'h3']:
                if next_elem.name == 'p' and next_elem.get_text().strip():
                    siblings.append(next_elem.get_text().strip())
                next_elem = next_elem.find_next_sibling()
            
            if siblings:
                text_blocks.append(f"{heading_text}: {' '.join(siblings)}")
            else:
                text_blocks.append(heading_text)
        
        return text_blocks
    
    except Exception as e:
        logger.error(f"Error with Selenium scraping: {e}")
        return []
    
    finally:
        driver.quit()

def find_relevant_content(query: str, text_blocks: List[str]) -> List[Dict]:
    """Find and rank content relevant to the query"""
    keywords = extract_keywords(query)
    
    if not keywords:
        # Fall back to fuzzy matching if no keywords are found
        best_matches = difflib.get_close_matches(query, text_blocks, n=5, cutoff=0.3)
        return [{"text": match, "score": 1.0} for match in best_matches]
    
    # Score each text block based on keyword matches
    scored_blocks = []
    for block in text_blocks:
        score = calculate_relevance_score(block, keywords)
        if score > 0:
            scored_blocks.append({"text": block, "score": score})
    
    # Sort by relevance score (highest first)
    scored_blocks.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top 5 matches or fewer if not enough found
    return scored_blocks[:5]

@app.post("/ask")
async def ask_question(query: Query):
    """Endpoint to ask questions about a specific CDP"""
    try:
        question = query.question.lower()
        
        # Identify which CDP is being asked about
        matched_cdp = None
        for cdp in CDP_DOCS.keys():
            if cdp in question:
                matched_cdp = cdp
                break
        
        if not matched_cdp:
            raise HTTPException(
                status_code=400, 
                detail="CDP not recognized in the question. Please specify one of: segment, mparticle, lytics, or zeotap."
            )
        
        # Try to get documentation from cache first
        text_blocks = get_documentation_cache(CDP_DOCS[matched_cdp])
        
        # If cache failed or returned empty, try direct scraping
        if not text_blocks:
            text_blocks = scrape_documentation(CDP_DOCS[matched_cdp])
        
        # If direct scraping failed, try Selenium as fallback
        if not text_blocks:
            text_blocks = scrape_documentation_with_selenium(CDP_DOCS[matched_cdp])
        
        if not text_blocks:
            return {
                "answer": f"Unable to retrieve documentation for {matched_cdp}.", 
                "suggestions": [
                    "Check if the documentation site is accessible",
                    "Try a different CDP",
                    "Check your internet connection"
                ]
            }
        
        # Find relevant content
        results = find_relevant_content(question, text_blocks)
        
        if not results:
            return {
                "answer": f"No relevant information found for your question about {matched_cdp}.", 
                "suggestions": [
                    "Try rephrasing your question",
                    "Check for specific feature names or terminology",
                    "Browse the documentation directly at " + CDP_DOCS[matched_cdp]
                ]
            }
        
        # Format the results
        return {
            "cdp": matched_cdp,
            "answer": [result["text"] for result in results],
            "relevant_sections": len(results),
            "documentation_url": CDP_DOCS[matched_cdp]
        }
    
    except Exception as e:
        logger.error(f"Error in /ask endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# CDP comparison data
CDP_COMPARISONS = {
    "segment vs mparticle": {
        "ease_of_use": "Segment has a more straightforward UI, while mParticle offers more granular controls that can have a steeper learning curve.",
        "integrations": "Segment offers 300+ integrations; mParticle offers 175+ but with deeper enterprise platform integrations.",
        "pricing": "Segment typically starts lower for small businesses; mParticle is enterprise-focused with higher minimum contracts.",
        "data_governance": "mParticle offers more advanced data governance features than Segment's base plan."
    },
    "segment vs lytics": {
        "core_focus": "Segment focuses on data collection and routing; Lytics emphasizes customer insights and personalization.",
        "audience_building": "Lytics has more advanced ML-based audience segmentation; Segment offers simpler rule-based segmentation.",
        "pricing_model": "Segment prices based on tracked users; Lytics prices based on active users and features.",
        "implementation": "Segment typically has faster initial implementation; Lytics requires more configuration for its advanced features."
    },
    "mparticle vs lytics": {
        "platform_approach": "mParticle is a broader data platform; Lytics focuses more on activation and personalization use cases.",
        "enterprise_features": "mParticle offers more enterprise governance features; Lytics emphasizes real-time decisioning.",
        "industry_focus": "mParticle has stronger presence in retail and media; Lytics in publishing and subscription services.",
        "technical_requirements": "Both require technical implementation, with mParticle generally requiring more developer resources."
    },
    "segment vs zeotap": {
        "global_presence": "Zeotap has stronger presence in European and Asian markets; Segment is stronger in North America.",
        "identity_resolution": "Zeotap offers more advanced identity resolution capabilities compared to Segment.",
        "data_enrichment": "Zeotap provides more built-in third-party data enrichment options than Segment.",
        "compliance": "Both offer strong compliance features, with Zeotap emphasizing GDPR compliance more heavily."
    }
}


@app.post("/compare")
async def compare_cdp(query: Query):
    """Endpoint for comparing different CDPs"""
    try:
        question = query.question.lower()
        
        # Find which comparison is being requested
        matched_comparison = None
        for comparison in CDP_COMPARISONS.keys():
            if comparison in question or comparison.replace(" vs ", " versus ") in question:
                matched_comparison = comparison
                break
        
        # If no exact match, try to detect individual CDPs
        if not matched_comparison:
            mentioned_cdps = [cdp for cdp in CDP_DOCS.keys() if cdp in question]
            if len(mentioned_cdps) >= 2:
                matched_comparison = f"{mentioned_cdps[0]} vs {mentioned_cdps[1]}"
        
        if not matched_comparison:
            raise HTTPException(
                status_code=400, 
                detail="Comparison not recognized. Please specify two CDPs to compare, like 'segment vs mparticle'."
            )
        
        # Extract keywords to determine which aspects to focus on
        keywords = extract_keywords(question)
        focus_areas = []
        
        # Map of common terms to comparison aspects
        focus_aspect_map = {
    "use": "ease_of_use",
    "user": "ease_of_use",
    "interface": "ease_of_use",
    "ui": "ease_of_use",
    "ux": "ease_of_use",
    "integrations": "integrations",
    "connect": "integrations",
    "connections": "integrations",
    "price": "pricing",
    "cost": "pricing",
    "pricing": "pricing",
    "governance": "data_governance",
    "compliance": "compliance",
    "gdpr": "compliance",
    "ccpa": "compliance",
    "audience": "audience_building",
    "segment": "audience_building",
    "identity": "identity_resolution",
    "resolution": "identity_resolution",
    "implementation": "implementation",
    "setup": "implementation",
    "install": "implementation",
    "enterprise": "enterprise_features",
    "focus": "core_focus",
    "approach": "platform_approach",
    "global": "global_presence",
    "region": "global_presence",
    "enrichment": "data_enrichment",
    "industry": "industry_focus",
    "technical": "technical_requirements"
}

        
        # Check for aspect-related keywords
        for keyword in keywords:
            for term, aspect in focus_aspect_map.items():
                if keyword == term or keyword.startswith(term) or term in keyword:
                    if aspect in CDP_COMPARISONS.get(matched_comparison, {}) and aspect not in focus_areas:
                        focus_areas.append(aspect)
        
        # If no specific focus areas found, include all
        if not focus_areas:
            focus_areas = list(CDP_COMPARISONS.get(matched_comparison, {}).keys())
        
        # Create focused response
        focused_comparison = {area: CDP_COMPARISONS[matched_comparison][area] for area in focus_areas if area in CDP_COMPARISONS.get(matched_comparison, {})}
        
        # If somehow we ended up with no data, include everything
        if not focused_comparison:
            focused_comparison = CDP_COMPARISONS.get(matched_comparison, {})
        
        cdps = matched_comparison.split(" vs ")
        
        return {
            "comparison": matched_comparison,
            "cdps": cdps,
            "aspects": focused_comparison,
            "documentation_urls": {cdp: CDP_DOCS[cdp] for cdp in cdps if cdp in CDP_DOCS}
        }
    
    except Exception as e:
        logger.error(f"Error in /compare endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/advanced")
async def advanced_question(query: Query):
    """Endpoint for advanced how-to questions about CDPs"""
    try:
        question = query.question.lower()
        
        # Identify which CDP and advanced topic is being asked about
        matched_cdp = None
        for cdp in CDP_DOCS.keys():
            if cdp in question:
                matched_cdp = cdp
                break
        
        if not matched_cdp:
            raise HTTPException(
                status_code=400, 
                detail="CDP not recognized in the question. Please specify one of: segment, mparticle, lytics, or zeotap."
            )
        
        # Advanced topics database
        advanced_topics = {
    "segment": {
        "tracking_plan": "To implement a tracking plan in Segment, follow these steps:\n1. Define your events and properties\n2. Use Segment's Protocols feature to enforce your plan\n3. Set up tracking in your codebase using the appropriate SDK\n4. Validate implementation with Segment's debugger",
        "identity_resolution": "For advanced identity resolution in Segment:\n1. Use userId and anonymousId consistently\n2. Implement .identify() calls at login/registration\n3. Consider using Personas for cross-device identity resolution\n4. Use ID mapping tables for legacy systems",
        "custom_destination": "To create a custom destination in Segment:\n1. Use Segment's Function sources\n2. Write a serverless function to transform and route data\n3. Deploy the function to your preferred cloud provider\n4. Connect the function to Segment as a destination",
        "data_governance": "For implementing data governance in Segment:\n1. Use Protocols to enforce data quality\n2. Set up workspace permissions for team access control\n3. Implement privacy settings for GDPR/CCPA compliance\n4. Use filtering rules to control data flow to destinations"
    },
    "mparticle": {
        "audience_builder": "For advanced audience building in mParticle:\n1. Use mParticle's Audience Builder to create segments\n2. Utilize calculated attributes for complex criteria\n3. Apply behavioral filters based on event frequency/recency\n4. Leverage lookalike modeling for expanded audiences",
        "data_planning": "To implement a data plan in mParticle:\n1. Define your data model in mParticle's Data Planning UI\n2. Apply validations and transformations\n3. Link the plan to your workspaces\n4. Monitor data quality in the Data Master dashboard",
        "identity_strategy": "For identity strategies in mParticle:\n1. Configure the Identity Hierarchy in settings\n2. Implement IDSync to capture identifiers\n3. Use Identity Priority to resolve conflicts\n4. Set up cross-device tracking with household IDs"
    },
    "lytics": {
        "behavioral_scoring": "To implement behavioral scoring in Lytics:\n1. Define your scoring model in the Lytics UI\n2. Select relevant user behaviors to track\n3. Apply weighting to different actions\n4. Set up score decay for time-based relevance",
        "content_affinity": "For content affinity modeling in Lytics:\n1. Ensure content tags are properly set up\n2. Enable content affinity modeling in settings\n3. Create segments based on content preferences\n4. Use these insights for content recommendations"
    },
    "zeotap": {
        "identity_resolution": "For advanced identity resolution in Zeotap:\n1. Implement the Zeotap ID+ solution\n2. Connect first-party data sources\n3. Configure match rules for cross-device linking\n4. Monitor match rates in the Zeotap dashboard",
        "compliance_workflows": "To set up compliance workflows in Zeotap:\n1. Configure data retention policies\n2. Set up consent management integration\n3. Implement data subject request handling\n4. Configure regional data storage settings"
    }
}

    
        
        # Extract keywords to determine which advanced topic is being asked about
        keywords = extract_keywords(question)
        
        # Map common keywords to topics
        topic_keyword_map = {
    "tracking plan": "tracking_plan",
    "data plan": "data_planning",
    "identity": "identity_resolution",
    "id resolution": "identity_resolution",
    "custom destination": "custom_destination",
    "destination": "custom_destination",
    "governance": "data_governance",
    "compliance": "compliance_workflows",
    "audience": "audience_builder",
    "segment": "audience_builder",
    "behavioral": "behavioral_scoring",
    "scoring": "behavioral_scoring",
    "content": "content_affinity",
    "affinity": "content_affinity"
}

        
        # Find matching topic
        matched_topic = None
        for phrase, topic in topic_keyword_map.items():
            if phrase in question and topic in advanced_topics.get(matched_cdp, {}):
                matched_topic = topic
                break
        
        if not matched_topic:
            # Try to match any available topic for the CDP
            for topic in advanced_topics.get(matched_cdp, {}):
                topic_words = topic.replace("_", " ").split()
                if any(word in question for word in topic_words):
                    matched_topic = topic
                    break
        
        if not matched_topic:
            # If still no match, provide general guidance
            return {
                "cdp": matched_cdp,
                "answer": f"Your question about advanced functionality in {matched_cdp} couldn't be matched to a specific topic.",
                "available_topics": list(advanced_topics.get(matched_cdp, {}).keys()),
                "suggestion": f"Try asking about one of the available advanced topics for {matched_cdp}."
            }
        
        # Return the matched topic information
        return {
            "cdp": matched_cdp,
            "topic": matched_topic,
            "answer": advanced_topics[matched_cdp][matched_topic],
            "documentation_url": CDP_DOCS[matched_cdp]
        }
    
    except Exception as e:
        logger.error(f"Error in /advanced endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Endpoint for system health check"""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
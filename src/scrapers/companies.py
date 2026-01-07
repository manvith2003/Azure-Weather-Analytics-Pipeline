"""Scraper for realistic B2B SaaS company names."""
import requests
from bs4 import BeautifulSoup
import logging
import random
from typing import List, Dict

logger = logging.getLogger(__name__)


class CompanyScraper:
    """Scrapes and generates realistic company names for B2B SaaS."""
    
    # Fallback list of real B2B SaaS companies
    FALLBACK_COMPANIES = [
        ("Slack", "slack.com"),
        ("Asana", "asana.com"),
        ("Notion", "notion.so"),
        ("Figma", "figma.com"),
        ("Airtable", "airtable.com"),
        ("Miro", "miro.com"),
        ("Datadog", "datadoghq.com"),
        ("Stripe", "stripe.com"),
        ("Twilio", "twilio.com"),
        ("Segment", "segment.com"),
        ("Amplitude", "amplitude.com"),
        ("Mixpanel", "mixpanel.com"),
        ("Intercom", "intercom.com"),
        ("Zendesk", "zendesk.com"),
        ("HubSpot", "hubspot.com"),
        ("Salesforce", "salesforce.com"),
        ("Workday", "workday.com"),
        ("ServiceNow", "servicenow.com"),
        ("Atlassian", "atlassian.com"),
        ("Zoom", "zoom.us"),
        ("DocuSign", "docusign.com"),
        ("Dropbox", "dropbox.com"),
        ("Box", "box.com"),
        ("Okta", "okta.com"),
        ("Auth0", "auth0.com"),
        ("Cloudflare", "cloudflare.com"),
        ("Fastly", "fastly.com"),
        ("PagerDuty", "pagerduty.com"),
        ("LaunchDarkly", "launchdarkly.com"),
        ("Splunk", "splunk.com"),
        ("New Relic", "newrelic.com"),
        ("Elastic", "elastic.co"),
        ("MongoDB", "mongodb.com"),
        ("Redis", "redis.com"),
        ("Snowflake", "snowflake.com"),
        ("Databricks", "databricks.com"),
        ("Confluent", "confluent.io"),
        ("HashiCorp", "hashicorp.com"),
        ("GitLab", "gitlab.com"),
        ("GitHub", "github.com"),
        ("CircleCI", "circleci.com"),
        ("Vercel", "vercel.com"),
        ("Netlify", "netlify.com"),
        ("Render", "render.com"),
        ("Postman", "postman.com"),
        ("Apollo", "apollographql.com"),
        ("Contentful", "contentful.com"),
        ("Sanity", "sanity.io"),
    ]
    
    def __init__(self):
        self.companies = []
    
    def scrape_yc_companies(self) -> List[Dict[str, str]]:
        """
        Scrape Y Combinator companies.
        Note: This is a simplified version. In production, you'd want more robust scraping.
        """
        try:
            # Try to get YC companies from their API/directory
            # For this assignment, we'll use fallback + generated names
            logger.info("Using curated B2B SaaS company list")
            return [
                {"name": name, "domain": domain} 
                for name, domain in self.FALLBACK_COMPANIES
            ]
            
        except Exception as e:
            logger.warning(f"Could not scrape companies: {e}")
            return []
    
    def generate_synthetic_companies(self, count: int = 50) -> List[Dict[str, str]]:
        """Generate realistic B2B SaaS company names."""
        prefixes = [
            "Data", "Cloud", "Signal", "Stream", "Sync", "Meta", "Proto",
            "Vertex", "Apex", "Core", "Nexus", "Quantum", "Cipher", "Pulse"
        ]
        
        suffixes = [
            "Labs", "Tech", "Systems", "Solutions", "Platform", "AI",
            "Dynamics", "Works", "Hub", "Stack", "Flow", "Sync"
        ]
        
        standalone = [
            "Harmonize", "Catalyze", "Synthesize", "Optimize", "Streamline",
            "Calibrate", "Integrate", "Accelerate", "Amplify", "Elevate"
        ]
        
        companies = []
        
        # Generate combined names
        for _ in range(count // 2):
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            name = f"{prefix}{suffix}"
            domain = f"{name.lower()}.com"
            companies.append({"name": name, "domain": domain})
        
        # Generate standalone names
        for _ in range(count // 2):
            name = random.choice(standalone)
            domain = f"{name.lower()}.io"
            companies.append({"name": name, "domain": domain})
        
        return companies
    
    def get_companies(self, count: int = 100) -> List[Dict[str, str]]:
        """Get a mix of real and synthetic company names."""
        real_companies = self.scrape_yc_companies()
        
        # Calculate how many synthetic we need
        synthetic_needed = max(0, count - len(real_companies))
        
        if synthetic_needed > 0:
            synthetic = self.generate_synthetic_companies(synthetic_needed)
            companies = real_companies + synthetic
        else:
            companies = real_companies[:count]
        
        random.shuffle(companies)
        
        logger.info(f"Generated {len(companies)} company names "
                   f"({len(real_companies)} real, {synthetic_needed} synthetic)")
        
        return companies
    
    def select_company(self) -> Dict[str, str]:
        """Select a random company for the simulation."""
        if not self.companies:
            self.companies = self.get_companies(100)
        
        return random.choice(self.companies)
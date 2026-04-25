"""
WEB SCRAPING EXAMPLE
====================

This file shows how to scrape REAL job data from Indeed/Glassdoor
Currently NOT used in main app (using simulated data), but you can use this
to replace the generate_sample_job_data() function.

WARNING: Always check website's robots.txt and terms before scraping.
         Use delays between requests to avoid being blocked.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# ============================================================================
# OPTION 1: Scrape Indeed (Easier, Less Dynamic)
# ============================================================================

def scrape_indeed_jobs(job_title="Data Scientist", location="India", pages=3):
    """
    Scrape job listings from Indeed
    
    Args:
        job_title: Job position to search
        location: Geographic location
        pages: Number of pages to scrape (each page = ~15 jobs)
    
    Returns:
        DataFrame with job data
    """
    
    jobs_data = []
    
    for page in range(pages):
        # Indeed URL structure
        url = f"https://in.indeed.com/jobs?q={job_title}&l={location}&start={page*10}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all job cards
            job_cards = soup.find_all('div', class_='job_seen_beacon')
            
            print(f"Page {page+1}: Found {len(job_cards)} jobs")
            
            for card in job_cards:
                try:
                    # Extract job information
                    title_elem = card.find('h2', class_='jobTitle')
                    title = title_elem.get_text(strip=True) if title_elem else "N/A"
                    
                    company_elem = card.find('span', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else "N/A"
                    
                    location_elem = card.find('div', class_='companyLocation')
                    job_location = location_elem.get_text(strip=True) if location_elem else "N/A"
                    
                    # Extract salary (if available)
                    salary_elem = card.find('span', class_='salary-snippet')
                    salary = salary_elem.get_text(strip=True) if salary_elem else "Not listed"
                    
                    # Extract job description snippet
                    description_elem = card.find('div', class_='job-snippet')
                    description = description_elem.get_text(strip=True) if description_elem else "N/A"
                    
                    # Extract posting date
                    date_elem = card.find('span', class_='date')
                    date_posted = date_elem.get_text(strip=True) if date_elem else "N/A"
                    
                    jobs_data.append({
                        'job_title': title,
                        'company': company,
                        'location': job_location,
                        'salary': salary,
                        'job_description': description,
                        'date_posted': date_posted
                    })
                
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue
            
            # Be nice to the server - add delay
            time.sleep(random.uniform(2, 5))
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page+1}: {e}")
            continue
    
    df = pd.DataFrame(jobs_data)
    print(f"\nTotal jobs scraped: {len(df)}")
    return df


# ============================================================================
# OPTION 2: Using LinkedIn API (Requires Authentication)
# ============================================================================

def scrape_linkedin_jobs_api(search_keyword="Data Scientist", location="India"):
    """
    LinkedIn official API approach (requires API credentials)
    
    Note: LinkedIn blocks scrapers. Official way is through:
    1. LinkedIn Recruiter API (paid enterprise solution)
    2. LinkedIn Graph API (deprecated for job search)
    3. Third-party services like RapidAPI
    
    This is for reference only.
    """
    
    # Example using RapidAPI LinkedIn Data API
    headers = {
        'x-rapidapi-key': 'YOUR_API_KEY_HERE',
        'x-rapidapi-host': 'linkedin-data-api.p.rapidapi.com'
    }
    
    params = {
        'query': search_keyword,
        'location': location,
        'count': 100
    }
    
    # This is hypothetical - actual endpoint depends on API
    url = "https://linkedin-data-api.p.rapidapi.com/search-jobs"
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        # Parse response
        jobs_df = pd.DataFrame(data['jobs'])
        return jobs_df
    
    except Exception as e:
        print(f"LinkedIn API Error: {e}")
        return None


# ============================================================================
# OPTION 3: Glassdoor Scraping (Using Selenium for JavaScript)
# ============================================================================

def scrape_glassdoor_jobs(job_title="Data Scientist", location="India", pages=3):
    """
    Scrape Glassdoor using Selenium (handles JavaScript-rendered content)
    
    Note: Glassdoor actively blocks scrapers. Use at your own risk!
    """
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    jobs_data = []
    
    # Initialize Chrome driver
    driver = webdriver.Chrome()  # Download chromedriver first
    
    try:
        for page in range(pages):
            # Glassdoor URL structure
            url = f"https://www.glassdoor.com/Job/data-scientist-jobs-SRCH_KO0,14.htm?fromAge=7&page={page}"
            driver.get(url)
            
            # Wait for jobs to load (JavaScript rendering)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "JobCard_jobCardContent"))
            )
            
            # Find all job cards
            job_cards = driver.find_elements(By.CLASS_NAME, "JobCard_jobCardContent")
            
            for card in job_cards:
                try:
                    title = card.find_element(By.CLASS_NAME, "JobCard_jobTitle").text
                    company = card.find_element(By.CLASS_NAME, "EmployerName").text
                    location_elem = card.find_element(By.CLASS_NAME, "JobCard_location")
                    job_location = location_elem.text
                    
                    salary_elem = card.find_element(By.CLASS_NAME, "JobCard_salary")
                    salary = salary_elem.text if salary_elem else "Not listed"
                    
                    jobs_data.append({
                        'job_title': title,
                        'company': company,
                        'location': job_location,
                        'salary': salary,
                        'source': 'glassdoor'
                    })
                
                except Exception as e:
                    print(f"Error parsing job card: {e}")
                    continue
            
            time.sleep(random.uniform(3, 6))
    
    finally:
        driver.quit()
    
    return pd.DataFrame(jobs_data)


# ============================================================================
# HELPER FUNCTION: Parse Salary Strings
# ============================================================================

def parse_salary(salary_string):
    """
    Convert salary strings like "₹10-15 Lakhs" to numeric values
    
    Args:
        salary_string: e.g., "₹10-15 Lakhs"
    
    Returns:
        (min_salary, max_salary) in INR
    """
    
    import re
    
    if not salary_string or salary_string == "Not listed":
        return None, None
    
    # Remove currency symbols
    salary_string = salary_string.replace('₹', '').replace('$', '').strip()
    
    # Find numbers
    numbers = re.findall(r'[\d.]+', salary_string)
    
    if len(numbers) < 2:
        return None, None
    
    min_sal = float(numbers[0])
    max_sal = float(numbers[1])
    
    # Convert Lakhs to actual values if needed
    if 'Lakh' in salary_string:
        min_sal *= 100000
        max_sal *= 100000
    
    return int(min_sal), int(max_sal)


# ============================================================================
# EXAMPLE: How to Use
# ============================================================================

if __name__ == "__main__":
    
    # Example 1: Scrape Indeed
    print("=" * 60)
    print("EXAMPLE: Scraping Indeed")
    print("=" * 60)
    
    df_indeed = scrape_indeed_jobs(
        job_title="Data Scientist",
        location="India",
        pages=2  # Start small to test
    )
    
    print(df_indeed.head())
    
    # Save to CSV
    df_indeed.to_csv('jobs_indeed.csv', index=False)
    print("✅ Saved to jobs_indeed.csv")
    
    # Parse salaries
    print("\nParsing salaries...")
    df_indeed[['salary_min', 'salary_max']] = df_indeed['salary'].apply(
        lambda x: pd.Series(parse_salary(x))
    )
    print(df_indeed[['salary', 'salary_min', 'salary_max']].head())


# ============================================================================
# TIPS FOR ETHICAL SCRAPING
# ============================================================================

"""
1. RESPECT robots.txt
   - Check website.com/robots.txt before scraping
   - Indeed allows scraping (mostly)
   - LinkedIn blocks scrapers explicitly

2. USE DELAYS
   - Add 2-5 second delays between requests
   - Don't hammer the server
   
3. ROTATE USER-AGENTS
   - Use different browser headers
   - Makes requests look more natural

4. IDENTIFY YOURSELF
   - Include contact info in User-Agent
   - Example: 'User-Agent: MyBot/1.0 (+contact@myemail.com)'

5. RESPECT RATE LIMITS
   - Don't scrape thousands of pages at once
   - Use API if available (and paid)

6. CHECK TERMS OF SERVICE
   - Many sites prohibit scraping
   - Violating ToS = legal risk

7. CACHE RESULTS
   - Don't scrape same data repeatedly
   - Save to CSV, reuse locally

8. HANDLE ERRORS GRACEFULLY
   - Website might be down
   - Use try-except blocks
   - Log what happened
"""

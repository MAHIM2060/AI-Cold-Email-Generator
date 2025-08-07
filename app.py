import streamlit as st
import requests
from bs4 import BeautifulSoup

from chains import Chain
from candidate_db import CandidateDB
from utils import clean_text


def scrape_job_description(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        content = soup.select_one('#content')
        if content:
            return content.get_text(separator=" ", strip=True)
        else:
            return soup.get_text(separator=" ", strip=True)
    except requests.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return None


def create_streamlit_app(llm, db, clean_text):
    st.title("💡 AtliQ Talent Matcher")
    url_input = st.text_input("Enter a Job Posting URL to Match:", value="https://boards.greenhouse.io/mozilla/jobs/7542901002")
    submit_button = st.button("Find Candidate & Generate Email")

    if submit_button:
        with st.spinner("Step 1: Scraping job posting..."):
            scraped_text = scrape_job_description(url_input)
        
        if scraped_text:
            data = clean_text(scraped_text)
            
            with st.spinner("Step 2: Extracting job details and finding top candidates..."):
                db.load_candidates()
                jobs = llm.extract_jobs(data)
                
                if not jobs:
                    st.error("Could not extract job details from the URL.")
                    return
                
                job = jobs[0]
                job_skills = job.get('skills', [])

                # --- New Display Block Added Here ---
                with st.expander("👀 View Skills Extracted from Job Posting"):
                    st.write("The AI found the following skills and requirements in the job description:")
                    st.info(", ".join(job_skills))
                # --- End of New Block ---
                
                top_candidates = db.find_best_candidates(job_skills)

            if top_candidates:
                with st.spinner("Step 3: AI is ranking the best candidates..."):
                    ranked_result = llm.rank_candidates(job, top_candidates)
                    best_candidate_name = ranked_result.get('best_candidate_name')
                    reasoning = ranked_result.get('reasoning')

                st.success(f"AI has selected the best candidate: **{best_candidate_name}**")
                st.info(f"**Reasoning:** {reasoning}")

                final_candidate = next((c for c in top_candidates if c['name'] == best_candidate_name), None)

                if final_candidate:
                    with st.spinner(f"Step 4: Writing outreach email to {final_candidate['name']}..."):
                        email = llm.write_mail(job, final_candidate)
                        st.code(email, language='markdown')
            else:
                st.error("Could not find any suitable candidates in the database.")


if __name__ == "__main__":
    chain = Chain()
    candidate_db = CandidateDB()
    st.set_page_config(layout="wide", page_title="AtliQ Talent Matcher", page_icon="💡")
    create_streamlit_app(chain, candidate_db, clean_text)
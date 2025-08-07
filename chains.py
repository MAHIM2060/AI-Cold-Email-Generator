import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-8b-8192")

    def extract_jobs(self, cleaned_text):
        # --- The prompt below is updated for better skill extraction ---
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from a job posting. Your job is to extract the details and return them in JSON format.
            The JSON must contain the following keys: `role`, `experience`, `skills` and `description`.

            The 'skills' key is mandatory. A skill can be a programming language (Python, Java), a technology (AWS, Docker), a tool (Jira, Figma), or a key qualification (Project Management, Team Leadership).
            If no specific technologies are mentioned, extract the main qualifications and responsibilities into the skills list. Do not return an empty skills list.

            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def rank_candidates(self, job, candidates):
        prompt_rank = PromptTemplate.from_template(
            """
            ### INSTRUCTION:
            You are an expert technical recruiter. Your task is to analyze a job description and a list of potential candidates and determine the single best fit.

            ### JOB DESCRIPTION:
            {job_description}

            ### POTENTIAL CANDIDATES:
            {candidate_list}

            ### YOUR TASK:
            Review the job description and the list of candidates. Return a JSON object with two keys:
            1. "best_candidate_name": The name of the single best candidate.
            2. "reasoning": A brief, one-sentence explanation for why you chose them.

            Choose the candidate whose skills and headline most closely match the specific requirements and title of the job. For example, if the job is for a "Frontend Developer", prioritize the candidate with that headline.

            ### JSON RESPONSE:
            """
        )
        
        candidate_str_list = []
        for candidate in candidates:
            candidate_str_list.append(
                f"Name: {candidate['name']}, Headline: {candidate['headline']}, Skills: {candidate['skills']}"
            )
        
        chain_rank = prompt_rank | self.llm | JsonOutputParser()
        
        res = chain_rank.invoke({
            "job_description": str(job),
            "candidate_list": "\n".join(candidate_str_list)
        })
        return res

    def write_mail(self, job, candidate):
        prompt_email = PromptTemplate.from_template(
            """
            ### INSTRUCTION:
            You are the "AtliQ Talent Team", a sophisticated AI that matches talented developers with their dream jobs.
            You are writing a professional and exciting outreach email to a candidate from your platform whose skills are a strong match for a new job opening.

            ### CANDIDATE DETAILS:
            - Name: {candidate_name}
            - Headline: {candidate_headline}
            - Portfolio: {candidate_portfolio}

            ### JOB DETAILS:
            - Role: {job_role}
            - Company: (Infer from the job description)
            - Description Summary: {job_description}

            ### EMAIL TO BE WRITTEN:
            Write a concise email to the candidate ({candidate_name}).
            - Start with a personal greeting (e.g., "Hi {candidate_name},").
            - Announce that the AtliQ matching engine has found an exciting new opportunity that aligns perfectly with their skills.
            - Mention the specific role and the company.
            - Briefly explain *why* their profile (e.g., their expertise in {relevant_skills}) is an excellent match for this role's requirements.
            - End with a clear call to action, encouraging them to review the opportunity and express their interest through a provided (hypothetical) link.
            - Sign off as "The AtliQ Talent Team".
            
            Do not use a subject line. Do not use a preamble.
            ### EMAIL:
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "candidate_name": candidate['name'],
            "candidate_headline": candidate['headline'],
            "candidate_portfolio": candidate['portfolio_link'],
            "job_role": job.get('role', 'N/A'),
            "job_description": str(job),
            "relevant_skills": ", ".join(job.get('skills', []))
        })
        return res.content
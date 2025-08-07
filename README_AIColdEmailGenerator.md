#  AI Cold Email Generator

A Python-based tool that automates the recruitment process by scraping job postings, matching candidates from a local database, and generating personalized cold emails.

---

##  Overview

This project streamlines recruitment in three steps:

1. **Scrape Job Postings**  
   Extracts job details from company career pages.

2. **Find the Best Match**  
   Searches a local CSV database for candidates with matching skills.

3. **Generate Personalized Emails**  
   Crafts outreach emails tailored to the matched candidate.

---

##  Features

-  Web Scraping  
-  Candidate Matching (skill-based ranking)  
-  Personalized Email Generation  
-  Runs entirely on your local machine

---

##  Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/MAHIM2060/AI-Cold-Email-Generator.git
cd AI-Cold-Email-Generator
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare the Candidate Database

- Create a file named `candidates.csv` in the root directory.
- Include fields like `name`, `email`, `skills`, `experience`, etc.

---

##  Usage

Launch the application using Streamlit:

```bash
streamlit run app.py
```

Then in the browser:

1. Paste a job posting URL.
2. Click **"Find Candidate & Generate Email"**.
3. See the best-matched candidate and the generated email.

---

##  Contributing

Contributions are welcome! Follow these steps:

```bash
# 1. Fork the repository
# 2. Create your feature branch
git checkout -b feature/YourFeatureName

# 3. Commit your changes
git commit -m "Add YourFeatureName"

# 4. Push to your branch
git push origin feature/YourFeatureName

# 5. Open a Pull Request on GitHub
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
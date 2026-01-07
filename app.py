import streamlit as st
import pdfplumber
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables (GROQ_API_KEY from .env)
load_dotenv()

# ==================== CONFIGURATION ====================
st.set_page_config(
    page_title="Unleash - AI Career Coach",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 Unleash")
st.markdown("**Your AI-powered career coach for any industry. Upload your CV, job posting, and get expert feedback — instantly.**")

# Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Use a current, supported model
MODEL = "llama-3.1-8b-instant"  # Fast and high-quality (change to "llama-3.1-70b-versatile" for more depth)

# Sectors with their council roles
SECTORS = {
    "Technology": ["CEO", "CTO", "HR Director", "Team Lead", "Devil's Advocate", "Career Coach", "Synthesizer"],
    "Healthcare": ["Service Director", "Clinical Lead", "HR Manager", "Team Supervisor", "Devil's Advocate", "Career Advisor", "Synthesizer"],
    "Finance": ["CFO", "Compliance Officer", "HR Director", "Department Head", "Devil's Advocate", "Career Coach", "Synthesizer"],
    "Education": ["Headteacher", "Curriculum Lead", "HR Manager", "Department Coordinator", "Devil's Advocate", "Career Advisor", "Synthesizer"],
    "Marketing": ["CMO", "Digital Lead", "HR Director", "Campaign Manager", "Devil's Advocate", "Career Coach", "Synthesizer"],
    "Sales": ["Sales Director", "Account Manager", "HR Manager", "Team Lead", "Devil's Advocate", "Career Coach", "Synthesizer"],
    "Creative": ["Creative Director", "Art Director", "HR Manager", "Project Manager", "Devil's Advocate", "Career Coach", "Synthesizer"],
}

# Role prompts
ROLE_PROMPTS = {
    "CEO": "You are a visionary CEO focused on growth, leadership, and cultural fit.",
    "CTO": "You are a technical CTO prioritizing skills, innovation, and scalability.",
    "Service Director": "You are a healthcare leader focused on patient outcomes and NHS values.",
    "Clinical Lead": "You are a clinical expert emphasizing safety and evidence-based practice.",
    "CFO": "You are a CFO focused on financial acumen and risk management.",
    "CMO": "You are a CMO focused on brand, creativity, and market impact.",
    "HR Director": "You are an HR leader focused on culture, diversity, and fit.",
    "HR Manager": "You are an HR manager focused on culture, diversity, and fit.",
    "Team Lead": "You are a hands-on manager focused on daily impact and teamwork.",
    "Devil's Advocate": "You are the Devil's Advocate — challenge assumptions and highlight risks.",
    "Career Coach": "You are a supportive career coach giving realistic, encouraging advice.",
    "Career Advisor": "You are a supportive career advisor giving realistic, encouraging advice.",
    "Synthesizer": "You are an impartial synthesizer delivering balanced final insights."
}

# Career trajectory & salary info (UK 2026 estimates)
CAREER_DATA = {
    "Technology": "Junior (£35k–£50k) → Mid (£60k–£90k) → Senior/Lead (£100k+) → CTO (£150k+). Focus: Coding, cloud, AI skills.",
    "Healthcare": "Band 3–4 (£24k–£30k) → Band 5–7 (£30k–£46k) → Band 8+ (£50k–£70k+). NHS pensions excellent.",
    "Finance": "Analyst (£40k–£60k) → Manager (£70k–£100k) → Director/CFO (£120k+). CFA/ACCA valuable.",
    "Education": "TA (£23k–£30k) → Teacher (£33k–£51k) → Head (£60k+). PGCE required.",
    "Marketing": "Executive (£28k–£40k) → Manager (£45k–£70k) → Director/CMO (£80k+). Portfolio key.",
    "Sales": "SDR (£30k–£45k) → AE (£60k–£90k OTE) → Director (£120k+ OTE). Quota attainment critical.",
    "Creative": "Junior (£25k–£35k) → Mid (£40k–£60k) → Director (£70k+). Strong portfolio essential."
}

TARGETED_QUESTIONS = [
    "What keywords from the job posting are missing in my CV?",
    "Suggest 3 improved bullet points for my top experience.",
    "How should I tailor my personal statement?",
    "What red flags might recruiters see — and how to fix them?",
    "What smart questions should I ask in interview?",
    "Cover letter: yes/no and key points to include?",
    "On a 1–10 scale, how strong is my application right now?"
]

# Mental health tips
MENTAL_HEALTH_TIPS = """
**Mental Health Tips for Job Seekers**
1. Take regular breaks — job hunting is a marathon.
2. Practice mindfulness or short walks to reduce stress.
3. Talk to friends or a professional if feeling overwhelmed.
4. Celebrate small wins like sending an application.
"""

# ======================================================

def extract_text(file):
    if file is not None:
        with pdfplumber.open(file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    return ""

def ask_llm(prompt):
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# ==================== SIDEBAR ====================
with st.sidebar:
    st.header("Upload Documents")
    cv_file = st.file_uploader("CV (PDF)", type="pdf")
    job_file = st.file_uploader("Job Posting (PDF)", type="pdf")
    org_file = st.file_uploader("Company Info (PDF)", type="pdf")

    linkedin_text = st.text_area("Paste your LinkedIn 'About' section or experience summary (text only)")

    sector = st.selectbox("Your Sector", options=list(SECTORS.keys()))

# ==================== MAIN UI ====================
cv_text = extract_text(cv_file)
job_text = extract_text(job_file)
org_text = extract_text(org_file)

if st.button("🚀 Unleash My Career Feedback", type="primary"):
    if not cv_text:
        st.error("Please upload your CV or paste text.")
    elif not client:
        st.error("API key not found. Check your .env file.")
    else:
        context = f"Sector: {sector}\nCV:\n{cv_text}\nJob Posting:\n{job_text}\nCompany:\n{org_text}\nLinkedIn: {linkedin_text}"

        with st.spinner("Your expert council is reviewing your application..."):
            report_parts = []
            full_debate = ""

            council = SECTORS[sector]
            progress = st.progress(0)
            for i, role in enumerate(council):
                if role == "Synthesizer":
                    continue
                prompt = f"{ROLE_PROMPTS.get(role, 'You are an expert reviewer.')}\n\nContext: {context}\n\nGive specific, constructive feedback on this application (150–300 words)."
                response = ask_llm(prompt)
                st.write(f"**{role}:**")
                st.write(response)
                full_debate += f"{role}: {response}\n\n"
                report_parts.append(f"{role}:\n{response}\n")
                progress.progress((i + 1) / len(council))

            # Final Synthesis
            synth_prompt = f"You are the Synthesizer. Provide a balanced, final recommendation based on this debate:\n\n{full_debate}"
            final = ask_llm(synth_prompt)
            st.success("**Final Recommendation:**")
            st.write(final)
            report_parts.append(f"\nFinal Recommendation:\n{final}")

            # LinkedIn Analysis
            if linkedin_text.strip():
                st.markdown("### 🔗 LinkedIn Profile Analysis")
                with st.spinner("Analyzing your LinkedIn profile..."):
                    linkedin_prompt = f"Analyze this pasted LinkedIn text for career strengths, gaps, improvements, and suggestions to make it more impactful for job applications in {sector}:\n\n{linkedin_text}"
                    linkedin_analysis = ask_llm(linkedin_prompt)
                    st.write(linkedin_analysis)
                    report_parts.append(f"\nLinkedIn Analysis:\n{linkedin_analysis}")
            else:
                st.info("💡 Paste your LinkedIn 'About' section or experience summary for personalized analysis.")

            # Career Path
            st.info(f"**Career Trajectory & Salary Bands ({sector})**\n\n{CAREER_DATA.get(sector, 'Data coming soon')}")

            # Targeted Questions
            st.markdown("### 🎯 Targeted Coaching Questions")
            for q in TARGETED_QUESTIONS:
                with st.expander(q):
                    q_prompt = f"{context}\n\nQuestion: {q}\nAnswer directly and actionably."
                    answer = ask_llm(q_prompt)
                    st.write(answer)
                    report_parts.append(f"\n{q}:\n{answer}")

            # Mental Health Tips
            st.markdown("### 🧠 Mental Health Tips for Job Seekers")
            st.write(MENTAL_HEALTH_TIPS)

            # Download Report
            full_report = "\n\n".join(report_parts) + f"\n\nCareer Path:\n{CAREER_DATA.get(sector, '')}\n\nMental Health Tips:\n{MENTAL_HEALTH_TIPS}"
            st.download_button(
                "📥 Download Full Report",
                full_report,
                file_name="unleash_career_report.txt",
                mime="text/plain"
            )

st.caption("Powered by Groq • Built for ambitious professionals • January 2026")
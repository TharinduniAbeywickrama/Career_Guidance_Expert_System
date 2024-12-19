import streamlit as st
import sqlite3
from experta import Fact, KnowledgeEngine, Rule, MATCH, Field

# Define user input facts
class UserInput(Fact):
    gpa = Field(float, mandatory=False)
    skills = Field(list, mandatory=False)
    interests = Field(list, mandatory=False)
    preferred_categories = Field(list, mandatory=False)
    internships = Field(bool, mandatory=False)
    hackathons = Field(bool, mandatory=False)

# Define the career guidance engine
class CareerGuidanceEngine(KnowledgeEngine):
    def __init__(self, careers):
        super().__init__()
        self.careers = careers
        self.results = []

    @Rule(UserInput(gpa=MATCH.gpa, skills=MATCH.skills, interests=MATCH.interests, preferred_categories=MATCH.preferred_categories,
                    internships=MATCH.internships, hackathons=MATCH.hackathons))
    def evaluate_careers(self, gpa, skills, interests, preferred_categories, internships, hackathons):
        for career in self.careers:
            career_name, required_skills, minimum_gpa, category, alternative_career = career[1:]
            score = 0

            # 1. Skill match
            if skills:  # Check if skills were provided
                required_skills_list = [skill.lower().strip() for skill in required_skills.split(",")]  # Normalize skills
                skill_match_count = sum(1 for skill in skills if skill.lower() in required_skills_list)  # Compare in lowercase
                score += skill_match_count * 2
            else:
                score += 0  # No skills provided, no match

            # 2. GPA match
            if gpa is not None:
                if gpa >= minimum_gpa:
                    score += 3
            else:
                score += 1  # Neutral score for missing GPA

            # 3. Interest match (career_name or alternative_career)
            if interests:  # Check if interests were provided
                if any(interest in career_name for interest in interests) or \
                   any(interest in alternative_career for interest in interests):
                    score += 2
            else:
                score += 1  # Neutral score for missing interests

            # 4. Category match
            if preferred_categories:  # Check if preferred categories were provided
                if category in preferred_categories:
                    score += 1  # Reward for match
                else:
                    score -= 1  # Penalize for mismatch if preferences exist
            else:
                score += 0  # Neutral score for missing categories

            # 5. Extra-curricular activities
            if internships:
                score += 1
            if hackathons:
                score += 1

            # Store the results as a tuple (career, score)
            self.results.append(((career_name, required_skills, minimum_gpa, category, alternative_career), score))

    def get_recommendations(self):
        # Sort results by score
        self.results.sort(key=lambda x: x[1], reverse=True)
        # Filter results by score threshold (minimum score = 2)
        filtered_results = [(career, score) for (career, score) in self.results if score >= 2]
        return filtered_results

    def get_alternative(self, recommendations):
        """Get the lowest scoring careers as alternatives."""
        if not recommendations:
            return None
        # Find the lowest score(s) in the filtered recommendations
        lowest_score = min(recommendations, key=lambda x: x[1])[1]
        alternatives = [career for career, score in recommendations if score == lowest_score]
        return alternatives

# Calculate confidence level
def calculate_uncertainty(user_input):
    """Estimate confidence level based on completeness of user inputs."""
    filled_fields = sum(1 for value in user_input.values() if value)
    total_fields = len(user_input)
    confidence = filled_fields / total_fields

    if confidence >= 0.8:
        return "High Confidence"
    elif confidence >= 0.5:
        return "Medium Confidence"
    else:
        return "Low Confidence"

# Generate explanation for recommendations
def explain_recommendation(career, score, user_input):
    """Generate explanation for a recommendation based on available data."""
    career_name, required_skills, minimum_gpa, category, alternative_career = career  # Unpack the career tuple

    explanation = []
    explanation.append(f"Career: {career_name}")

    # Skills match
    if user_input['skills']:  # Check if skills were provided
        required_skills_list = [skill.lower().strip() for skill in required_skills.split(",")]  # Normalize skills
        matched_skills = [skill for skill in user_input['skills'] if skill.lower() in required_skills_list]  # Compare in lowercase
        if matched_skills:
            explanation.append(f"Matched Skills: {', '.join(matched_skills)} ({len(matched_skills)} matches)")
        else:
            explanation.append("No skills match found.")
    else:
        explanation.append("No skills provided, assuming no match.")

    # GPA match
    if user_input['gpa']:
        if user_input['gpa'] >= minimum_gpa:
            explanation.append(f"GPA ({user_input['gpa']}) meets or exceeds the minimum requirement ({minimum_gpa}).")
        else:
            explanation.append(f"GPA ({user_input['gpa']}) does not meet the minimum requirement.")
    else:
        explanation.append("GPA not provided, assuming neutral.")

    # Interest match
    if user_input['interests']:  # Check if interests were provided
        if any(interest in career_name for interest in user_input['interests']) or \
           any(interest in alternative_career for interest in user_input['interests']):
            explanation.append("Your interests align with this career.")
        else:
            explanation.append("Your interests do not align with this career.")
    else:
        explanation.append("No interests provided, assuming neutral match.")

    # Category match
    if user_input['preferred_categories']:  # Check if preferred categories were provided
        if category in user_input['preferred_categories']:
            explanation.append(f"This matches the {category} career path.")
        else:
            explanation.append(f"This does not matches the {category} career path.")
    else:
        explanation.append("No preferred career path provided, assuming neutral match.")

    return explanation

# Streamlit UI for user inputs
st.title("Career Guidance System for IT Undergraduates")

# User input fields
name = st.text_input("Name", "") 
year_of_study = st.selectbox("Year of Study", [1, 2, 3, "Final"])
gpa = st.selectbox("GPA", [round(x * 0.01, 2) for x in range(0, 401)])
skills = st.multiselect("Skills", ["Programming", "Problem-Solving", "Data Analysis", "Machine Learning", "Research", 
                                    "Network Security", "Risk Analysis", "Teaching", "Deep Learning", "Cloud Platforms", 
                                    "Network Administration", "System Design", "Data Interpretation"])
interest_areas = st.multiselect("Interest Areas", ["Software Developer", "Web Developer", "Data Scientist", "Data Analyst", 
                                                    "Cybersecurity", "Research Assistant", "Lecturer", "Cybersecurity Analyst", 
                                                    "Forensics Analyst", "AI/ML Engineer", "AI Researcher", "Cloud Solutions Architect", 
                                                    "Cloud Engineer", "Researcher/Academia", "Lecturer"]) 
preferred_categories = st.multiselect("Preferred Career Path", ["Industry", "Academia"], 
                                       help="Select one or both. Leave blank if you're fine with both.")
internships = st.checkbox("Internships")
hackathons = st.checkbox("Hackathons")

# Process the form when submitted
if st.button("Submit"):
    # If no categories are selected, assume both are acceptable
    if not preferred_categories:
        preferred_categories = ["Industry", "Academia"]

    # Create user input dictionary
    user_input = {
        'gpa': gpa,
        'skills': skills,
        'interests': interest_areas,
        'preferred_categories': preferred_categories,
        'internships': internships,
        'hackathons': hackathons
    }

    # Calculate uncertainty level
    confidence = calculate_uncertainty(user_input)

    # Connect to the SQLite database
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM career_knowledge_base")
    careers = cursor.fetchall()

    # Initialize and run the expert system
    engine = CareerGuidanceEngine(careers)
    engine.reset()
    engine.declare(UserInput(**user_input))
    engine.run()

    # Get recommendations
    recommendations = engine.get_recommendations()

    # Check if all scores are below 2
    if not recommendations or all(score < 3 for _, score in recommendations):
        st.warning("No recommendations provided!")
    else:
        st.subheader(f"Confidence Level: {confidence}")
        if name.strip():
            st.subheader(f"Hi {name}, your recommended careers (from most to least suitable):")
        else:
            st.subheader("Your recommended careers (from most to least suitable):")
        for career, score in recommendations:
            explanation = explain_recommendation(career, score, user_input)
            st.write(f"- {career[0]}")
            with st.expander("Why this career?"):
                for line in explanation:
                    st.write(line)

        # Get alternative career recommendation
        alternatives = engine.get_alternative(recommendations)
        if alternatives:
            st.subheader("Alternative Career Recommendation:")
            for alternative in alternatives:
                explanation = explain_recommendation(alternative, score, user_input)
                st.write(f"- {alternative[0]}")
                with st.expander("Why this alternative career?"):
                    for line in explanation:
                        st.write(line)

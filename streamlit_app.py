import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI  # Install OpenAI library: pip install openai

# Function to scrape Twitch data
def scrape_twitch_data(twitch_link):
    try:
        # Send a GET request to the Twitch link
        response = requests.get(twitch_link)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract stream title
        title = soup.find('meta', {'property': 'og:title'})['content'] if soup.find('meta', {'property': 'og:title'}) else "Title not found"
        
        # Extract stream description
        description = soup.find('meta', {'property': 'og:description'})['content'] if soup.find('meta', {'property': 'og:description'}) else "Description not found"
        
        # Attempt to extract number of followers (if available in the page source)
        followers = None
        followers_tag = soup.find('p', class_='CoreText-sc-cpl358-0')  # Update class based on Twitch's HTML structure
        if followers_tag:
            followers = followers_tag.text.strip()
        
        # Attempt to extract live viewers (if available in the page source)
        viewers = None
        viewers_tag = soup.find('p', class_='live-viewers-class')  # Update class based on Twitch's HTML structure
        if viewers_tag:
            viewers = viewers_tag.text.strip()
        
        return {
            "title": title,
            "description": description,
            # "followers": followers or "Followers data not found",
            # "viewers": viewers or "Live viewers data not found",
            "link": twitch_link
        }
    except Exception as e:
        return {"error": str(e), "link": twitch_link}

# Function to interact with OpenAI API
def generate_feedback_with_ai(api_key, messages, api_type):
    try:
        api_type = api_type.lower()
        if api_type == "perplexity":
            client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
            model = "sonar-pro"  # Replace with the desired Perplexity model
            max_tokens = 1000  # Adjust max tokens as needed

        elif api_type == "openai":
            client = OpenAI(api_key=api_key)  # OpenAI uses its default base URL
            model = "gpt-4o"  # Replace with the desired OpenAI model
            max_tokens = 1500  # Adjust max tokens as needed
        else:
            return "Invalid API type specified."

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating feedback: {e}"
# Main function to run the Streamlit app
def main():
    st.title("Twitch Data Feedback App with AI Assistant")

    # Inputs
    st.write("Enter Twitch links (one per line), a parameter for feedback, and define a persona for the AI assistant.")
    twitch_links = st.text_input("Twitch Links:")
    additional_info = st.text_area("Additional Information (optional):")
    # parameter = st.text_input("Parameter for feedback (i.e.):")
    persona = st.text_area("Define the AI Assistant Persona (e.g., 'You are an expert Twitch analyst...'):")

    api_type = st.radio("Select API Type:", options=["Perplexity", "OpenAI"])
    api_key = st.text_input(f"Enter your {api_type} API Key:", type="password")
    # api_key = st.text_input("Enter your Perplexity API Key:", type="password")

    if st.button("Submit"):
        # if not twitch_links.strip() or not parameter.strip() or not persona.strip() or not api_key.strip():
        #     st.error("Please provide all inputs: Twitch links, parameter, persona, and API key.")
        if not twitch_links.strip() or not persona.strip() or not api_key.strip():
            st.error("Please provide all inputs: Twitch links, parameter, persona, and API key.")
        else:
            # Split the input into individual links
            links = [link.strip() for link in twitch_links.splitlines() if link.strip()]
            
            # Process each link and scrape data
            scraped_data = []
            
            for link in links:
                result = scrape_twitch_data(link)
                if "error" in result:
                    st.error(f"Failed to process {result['link']}: {result['error']}")
                else:
                    scraped_data.append(result)
            
            # Prepare messages for AI assistant
            messages = [
                {"role": "system", "content": persona},
                {"role": "user", "content": f"Analyze the following Twitch data and provide feedback based on this information: {scraped_data, additional_info}"}
            ]
            
            # Generate feedback using OpenAI API
            ai_feedback = generate_feedback_with_ai(api_key, messages, api_type=api_type)
            
            # Display results
            st.subheader("Feedback Results")
            if scraped_data:
                for data in scraped_data:
                    st.write(f"**Link:** {data['link']}")
                    st.write(f"**Title:** {data['title']}")
                    st.write(f"**Description:** {data['description']}")
                    # st.write(f"**Followers:** {data['followers']}")
                    # st.write(f"**Viewers:** {data['viewers']}")
                    st.markdown("---")
            
            st.subheader("AI Feedback")
            st.write(ai_feedback)

if __name__ == "__main__":
    main()

import streamlit as st
from scraper.google_maps_scraper import GoogleMapsScraper
import pandas as pd
from io import StringIO

# Function to run the scraper and return results as CSV string
def run_scraper(query, max_results, max_pages):
    scraper = GoogleMapsScraper()
    csv_string = scraper.scrape(query, max_results, max_pages)
    return csv_string

# Streamlit UI
def main():
    st.title('Google Maps Business Scraper')

    # Sidebar input fields
    query = st.text_input('Enter search query (e.g., Consultancies in Mumbai, Maharashtra, India):')
    max_results = st.number_input('Max results per category:', min_value=1, value=100)
    max_pages = st.number_input('Max pages to scrape:', min_value=1, value=5)

    # Initialize session state to keep track of data
    if 'csv_data' not in st.session_state:
        st.session_state.csv_data = None

    # Scrape data when button is clicked
    if st.button('Scrape Data'):
        st.write('Scraping in progress...')
        csv_string = run_scraper(query, max_results, max_pages)
        st.session_state.csv_data = csv_string  # Save data to session state

    # Display scraped data if available
    if st.session_state.csv_data:
        df = pd.read_csv(StringIO(st.session_state.csv_data))
        st.write('### Scraped Data:')
        st.dataframe(df)

        # Download link for CSV
        st.write('### Download CSV:')
        st.download_button(label='Download CSV', data=st.session_state.csv_data, file_name='scraped_data.csv', mime='text/csv')

if __name__ == '__main__':
    main()

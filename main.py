import streamlit as st
from llama_index.llms.groq import Groq
from dotenv import load_dotenv
import os
import requests

# Load the environment variables from .env file
load_dotenv()

# Fetch the API key from the environment variable
api_key = os.getenv("GROQ_API_KEY")

# Initialize the Groq model
llm = Groq(model="llama3-70b-8192", api_key=api_key)

# CoinGecko API endpoint
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"

def get_crypto_price(crypto_id):
    """
    Fetch the current price of a cryptocurrency using CoinGecko API.
    """
    try:
        params = {
            "ids": crypto_id,  # Cryptocurrency ID (e.g., "bitcoin", "ethereum")
            "vs_currencies": "usd",  # Currency to compare against (e.g., USD)
            "include_market_cap": "true",
            "include_24hr_change": "true"
        }
        response = requests.get(COINGECKO_API_URL, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        price_data = response.json()
        if crypto_id in price_data:
            return {
                "price_usd": price_data[crypto_id]["usd"],
                "market_cap": price_data[crypto_id]["usd_market_cap"],
                "price_change_24h": price_data[crypto_id]["usd_24h_change"]
            }
        else:
            return {"error": "Cryptocurrency not found"}
    except requests.exceptions.RequestException as e:
        return {"error": f"CoinGecko API error: {e}"}
    except KeyError:
        return {"error": "Invalid response from CoinGecko API"}

def get_crypto_info(crypto_id):
    """
    Fetch additional information about a cryptocurrency using Groq LLM.
    """
    prompt = f"Provide a brief description of {crypto_id} and its use cases."
    response = llm.complete(prompt)
    return response.text

# Streamlit app
st.title("📊 Real-Time Cryptocurrency Price Tracker 🚀")

# Cryptocurrency input
crypto_id = st.text_input("Enter a cryptocurrency (e.g., bitcoin, ethereum)").lower()

if st.button("Get Price and Info"):
    if crypto_id:
        # Fetch price data
        price_data = get_crypto_price(crypto_id)
        if "error" in price_data:
            st.error(price_data["error"])
        else:
            st.write(f"### Current Price of {crypto_id.capitalize()}")
            st.write(f"**Price (USD):** ${price_data['price_usd']}")
            st.write(f"**Market Cap (USD):** ${price_data['market_cap']:,.2f}")
            st.write(f"**24h Price Change:** {price_data['price_change_24h']:.2f}%")

            # Fetch additional info using Groq LLM
            st.write("### Additional Information")
            crypto_info = get_crypto_info(crypto_id)
            st.write(crypto_info)
    else:
        st.write("Please enter a cryptocurrency name.")

# Add a footer
st.markdown("---")
st.markdown("Made by [Your Name]")

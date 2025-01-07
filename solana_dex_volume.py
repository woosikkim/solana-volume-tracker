import requests
import pandas as pd
import matplotlib.pyplot as plt
import time

def fetch_solana_volume():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids=solana"
    for _ in range(5):  # Retry up to 5 times
        try:
            response = requests.get(url, timeout=10)  # Add timeout
            if response.status_code == 200:
                data = response.json()
                if data and isinstance(data, list):
                    total_volume = data[0].get("total_volume", 0)
                    return total_volume
            else:
                print(f"API returned status code {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        time.sleep(5)  # Wait before retrying
    print("Failed to fetch data after retries.")
    return None

def plot_volume_history():
    timestamps = []
    volumes = []
    
    plt.ion()
    fig, ax = plt.subplots()
    
    while True:
        volume = fetch_solana_volume()
        if volume is not None:
            timestamps.append(pd.Timestamp.now())
            volumes.append(volume)
            
            ax.clear()
            ax.plot(timestamps, volumes, marker='o', linestyle='-', color='b')
            ax.set_xlabel("Time")
            ax.set_ylabel("Volume (USD)")
            ax.set_title("Solana Total Trading Volume Over Time")
            plt.xticks(rotation=45)
            plt.pause(300)  # Update every 5 minutes
        else:
            print("Skipping update due to API failure.")

if __name__ == "__main__":
    plot_volume_history()


import pandas as pd

# Lire le CSV
df = pd.read_csv("./../../nasa_event_thresholds.csv")

# Grouper par Event et créer un dictionnaire {Event: {Indicator: Threshold}}
events_dict = df.groupby('Event')[['Indicator', 'Threshold']].apply(
    lambda x: dict(zip(x['Indicator'], x['Threshold']))
).to_dict()

def get_event(temp: float, soil_moisture: float):
    for event_name, indicators in events_dict.items():
        temp_threshold = indicators.get("Temperature_Minimum")
        soil_threshold = indicators.get("Soil_Moisture_Maximum")
        
        if temp < temp_threshold or soil_moisture < soil_threshold:
            return event_name

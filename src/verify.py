import asyncio
import logging

from src.fetch import fetch_all
from src.models import parse_country, parse_ip, parse_weather
from src.storage import print_benchmark, records_to_df, save_and_benchmark

logging.basicConfig(level=logging.WARNING)                                        
result = asyncio.run(fetch_all())                                                 
                                                                                  
weather_records = parse_weather(result['weather'])                                
country = parse_country(result['country'])                                        
ip_info = parse_ip(result['ip'])                                                  
                                                                                  
print(f'weather records: {len(weather_records)}')                                 
print(f'country: {country}')                                                      
print(f'ip: {ip_info}')                                                           
                                                                                  
weather_df = records_to_df(weather_records)                                       
country_df = records_to_df([country] if country else [])                          
ip_df = records_to_df([ip_info] if ip_info else [])                               
                                                                                  
for name, df in [('weather', weather_df), ('country', country_df), ('ip', ip_df)]:
    bench = save_and_benchmark(df, name)                                          
    print_benchmark(name, bench)
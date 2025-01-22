import requests
from datetime import datetime
from .constants import EXCHANGE_RATE_API_URL

class CurrencyExchangeAPI:
    def __init__(self):
        self.rates_cache = {}
        self.last_updated = None
        
    def get_exchange_rate(self, from_currency, to_currency):
        """Get exchange rate between two currencies"""
        try:
            # Check cache first
            current_time = datetime.now()
            cache_key = f"{from_currency}_{to_currency}"
            
            # If we have a cached rate less than 1 hour old, use it
            if (cache_key in self.rates_cache and self.last_updated and 
                (current_time - self.last_updated).seconds < 3600):
                return {
                    'success': True,
                    'rate': self.rates_cache[cache_key],
                    'last_updated': self.last_updated
                }
            
            # Fetch new rates from API
            response = requests.get(f"{EXCHANGE_RATE_API_URL}{from_currency}")
            if response.status_code == 200:
                data = response.json()
                rate = data['rates'][to_currency]
                
                # Update cache
                self.rates_cache[cache_key] = rate
                self.last_updated = current_time
                
                return {
                    'success': True,
                    'rate': rate,
                    'last_updated': current_time
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: Status code {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error fetching exchange rate: {str(e)}"
            }
    
    def convert_amount(self, amount, from_currency, to_currency):
        """Convert an amount from one currency to another"""
        try:
            # Get exchange rate
            rate_data = self.get_exchange_rate(from_currency, to_currency)
            
            if rate_data['success']:
                converted_amount = amount * rate_data['rate']
                return {
                    'success': True,
                    'amount': converted_amount,
                    'rate': rate_data['rate'],
                    'last_updated': rate_data['last_updated']
                }
            else:
                return rate_data  # Return the error from get_exchange_rate
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Error converting amount: {str(e)}"
            } 
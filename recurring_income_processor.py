from pages.income_tracking.database import process_recurring_income
import time
import sys
from datetime import datetime

def run_processor():
    """Run the recurring income processor service"""
    print("Starting Recurring Income Processor Service")
    print(f"Started at: {datetime.now()}")
    
    try:
        while True:
            try:
                success, message = process_recurring_income()
                if success:
                    print(f"[{datetime.now()}] {message}")
                else:
                    print(f"[{datetime.now()}] Error: {message}")
            except Exception as e:
                print(f"[{datetime.now()}] Error in processor: {e}")
            
            # Sleep for 1 hour before next check
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\nShutting down Recurring Income Processor Service")
        sys.exit(0)

if __name__ == "__main__":
    run_processor() 
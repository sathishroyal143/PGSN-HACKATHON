"""
Script to search for errors in CareBridge logs
Usage: python find_error.py [request_id]
"""

import sys
import os
from pathlib import Path

def search_logs(request_id=None):
    """Search for errors in the log file"""
    log_file = Path(__file__).parent / 'logs' / 'carebridge.log'
    
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        return
    
    print(f"Searching in: {log_file}\n")
    print("=" * 80)
    
    if request_id:
        print(f"Searching for Request ID: {request_id}\n")
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            found = False
            for i, line in enumerate(lines):
                if request_id in line:
                    found = True
                    # Print context (10 lines before and after)
                    start = max(0, i - 10)
                    end = min(len(lines), i + 20)
                    print("Context:\n")
                    for j in range(start, end):
                        prefix = ">>> " if j == i else "    "
                        print(f"{prefix}{lines[j]}", end='')
                    print("\n" + "=" * 80)
            
            if not found:
                print(f"❌ Request ID '{request_id}' not found in logs")
                print("\nThis could mean:")
                print("  1. The error occurred before the fix was applied")
                print("  2. The error hasn't been logged yet")
                print("  3. The log file was rotated/cleared")
    else:
        print("Showing recent ERROR and CRITICAL entries:\n")
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            recent_errors = []
            for line in lines:
                if 'ERROR' in line or 'CRITICAL' in line:
                    recent_errors.append(line)
            
            if recent_errors:
                print(f"Found {len(recent_errors)} error entries:")
                print("\nMost recent 20 errors:\n")
                for line in recent_errors[-20:]:
                    print(line, end='')
            else:
                print("No ERROR or CRITICAL entries found in logs")
    
    print("\n" + "=" * 80)
    print("\nTips:")
    print("  - To search for a specific request ID: python find_error.py <request_id>")
    print("  - Check if services are running:")
    print("    * PostgreSQL database")
    print("    * Redis server")
    print("    * Celery worker")
    print("  - Verify .env configuration")
    print("  - Check database migrations: python manage.py showmigrations")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        search_logs(sys.argv[1])
    else:
        search_logs()

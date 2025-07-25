import time 

RATE_LIMIT = {}

def is_rate_limited(ip, window=60, max_requests=5):
    now = time.time()

    if ip not in RATE_LIMIT:
        RATE_LIMIT[ip] = []
    RATE_LIMIT[ip] = [timestamp for timestamp in RATE_LIMIT[ip] if now - timestamp < window]
    
    if len(RATE_LIMIT[ip]) >= max_requests:
        return True
    
    RATE_LIMIT[ip].append(now)
    return False
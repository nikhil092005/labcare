from werkzeug.security import generate_password_hash, check_password_hash

def generate_hashed_password(plain_password):
    return generate_password_hash(plain_password, method='pbkdf2:sha256', salt_length=16)

def verify_password(hashed_password, candidate_password):
    return check_password_hash(hashed_password, candidate_password)

def calculate_rank_and_stars(credits):
    """
    Calculate rank and stars based on credits
    - Every 40 credits = 1 rank increase
    - Stars based on rank: 5 ranks = 2 stars, 20 ranks = 3 stars, 40 ranks = 4 stars, 100 ranks = 5 stars
    """
    rank = 200 - (credits // 40)  # Start from rank 200, decrease as credits increase
    if rank < 1:
        rank = 1
    
    # Calculate stars based on total ranks achieved
    total_ranks_achieved = 200 - rank
    
    if total_ranks_achieved >= 100:
        stars = 5
    elif total_ranks_achieved >= 40:
        stars = 4
    elif total_ranks_achieved >= 20:
        stars = 3
    elif total_ranks_achieved >= 5:
        stars = 2
    else:
        stars = 1
    
    # Credits reset every rank (40 credits)
    remaining_credits = credits % 40
    
    return rank, stars, remaining_credits

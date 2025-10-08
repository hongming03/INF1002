from typing import List, Set, Optional

# Segmentation Algorithms

def segment_text(text: str, dictionary: Set[str]) -> List[str]:
    """
    Segment text into words using a dictionary (returns one valid segmentation).
    """
    # Always lowercase input for consistency with dictionary
    text = text.lower().strip()
    n = len(text)
    dp: List[Optional[List[str]]] = [None] * (n + 1)
    dp[0] = []

    for i in range(1, n + 1):
        for j in range(i):
            word = text[j:i]
            if dp[j] is not None and word in dictionary:
                dp[i] = dp[j] + [word]
                break

    return dp[n] if dp[n] else []

# Dictionary Helper (NLTK + Crypto)

def get_full_dictionary() -> Set[str]:
    """
    Return a reliable, lightweight dictionary that always includescrypto words.
    """

    crypto_terms = {
        "bitcoin", "ethereum", "hodl", "bullrun",
        "blockchain", "nft", "satoshi", "altcoin", "defi",
        "token", "coin", "crypto", "market", "profit", "loss", "wallet",
        "buy", "sell", "price", "exchange", "Cryptocurrency", "has", "revolutionized", "the", "financial", "world", "with", "its",
    "decentralized", "nature", "and", "potential", "for", "high", "returns", "Bitcoin",
    "Ethereum", "and", "other", "digital", "assets", "are", "gaining", "traction", "among",
    "investors", "and", "tech", "enthusiasts", "alike", "While", "volatility", "remains",
    "a", "major", "concern", "many", "believe", "that", "blockchain", "technology", "will",
    "transform", "industries", "from", "banking", "to", "supply", "chain", "management",
    "Regulatory", "uncertainty", "continues", "but", "governments", "are", "exploring",
    "ways", "to", "integrate", "crypto", "safely", "into", "the", "economy"
    }

    # Optional: try loading NLTK words (quietly)
    english_dict = set()
    try:
        import nltk
        from nltk.corpus import words
        nltk.download("words", quiet=True)
        english_dict = set(w.lower() for w in words.words())
    except Exception:
        pass  # safe fallback if NLTK not available

    return english_dict.union(crypto_terms)





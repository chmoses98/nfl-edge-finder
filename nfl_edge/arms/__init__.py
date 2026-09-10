"""The prospective three-arm game-center experiment (shadow research; zero betting authority).

    CURRENT_MARKET_PRIOR   the incumbent: the market sets the centre, historical residuals make the distribution
    DATA_ONLY              football data sets the centre; the SAME residual machinery makes the distribution
    HYBRID_30_DATA         0.70 x market centre + 0.30 x football centre; the same machinery again

Nothing in this package is imported by the pricer, the handicap packet, the gates or the recommendation
writers. It reads what they wrote and writes into its own corpus.
"""

"""Board Accounting v1: every discovered NFL contract terminates in an explicit state, and the denominator is
the DISCOVERED NFL BOARD -- never the ledger.

    states       terminal states and the funnel v2 stages
    accounting   contract-by-contract classification of a discovery run into stages and a terminal state
    drift        discovery -> registry drift: new series, new structures, unclassified, registry lag, capture gap
    provisional  provisional classification of unknown series so they are captured at a safe tier
"""

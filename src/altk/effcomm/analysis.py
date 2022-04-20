"""Functions for analyzing the results of the simplicity/informativeness trade-off."""

import pandas as pd

def get_report() -> pd.DataFrame:
    """Runs statistical tests and returns a dataframe containing correlations of optimality with degrees of naturalness and means of optimality for each natural language.
    """
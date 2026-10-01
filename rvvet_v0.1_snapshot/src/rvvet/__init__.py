"""rvvet: a vetting ladder for radial-velocity planet signals in long archival time series."""
from .data import Series, load_star, bin_nightly, quality_mask, INDICATORS
from .periodogram import Frame, fit_jitter, frequency_grid, baluev_fap
from .ladder import vet, prewhiten, activity_period, FEATURES

__version__ = "0.1.0"

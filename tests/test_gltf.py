#!/usr/bin/env python
"""Tests for `effibemviewer` gltf."""

import openstudio

from effibemviewer import create_example_model


def test_create_example_model():
    """Test creating an example OpenStudio model."""
    model = create_example_model(include_geometry_diagnostics=True)
    assert isinstance(model, openstudio.model.Model)

#!/usr/bin/env python
"""Tests for `effibemviewer` gltf."""

import sys
from pathlib import Path

# TODO: Remove once geometry diagnostics is in released OpenStudio
sys.path.insert(0, str(Path("~/Software/Others/OS-build-release/Products/python").expanduser()))

import openstudio
import pytest

from effibemviewer import create_example_model
from effibemviewer.gltf import model_to_gltf_html, model_to_gltf_script


@pytest.fixture
def model():
    """Create an example OpenStudio model for testing."""
    return create_example_model()


def test_create_example_model(model):
    """Test creating an example OpenStudio model."""
    assert isinstance(model, openstudio.model.Model)


class TestJSAPI:
    """Tests for the JavaScript API exposed by the viewer."""

    def test_effibemviewer_class_exposed(self, model):
        """Test that EffiBEMViewer class is exposed globally."""
        html = model_to_gltf_html(model)
        assert "class EffiBEMViewer" in html
        assert "window.EffiBEMViewer = EffiBEMViewer" in html

    def test_run_from_json_exposed(self, model):
        """Test that runFromJSON convenience function is exposed."""
        html = model_to_gltf_html(model)
        assert "window.runFromJSON = function(gltfData, options = {})" in html

    def test_run_from_file_exposed(self, model):
        """Test that runFromFile convenience function is exposed."""
        html = model_to_gltf_html(model)
        assert "window.runFromFile = function(url, options = {})" in html

    def test_class_has_load_methods(self, model):
        """Test that EffiBEMViewer class has loadFromJSON and loadFromFile methods."""
        html = model_to_gltf_html(model)
        assert "loadFromJSON(gltfData)" in html
        assert "loadFromFile(url)" in html

    def test_diagnostics_toggle_via_css_class(self, model):
        """Test that diagnostics are toggled via CSS class, not Jinja conditionals."""
        # With diagnostics disabled
        html_no_diag = model_to_gltf_html(model, include_geometry_diagnostics=False)
        assert "diagnostics-section" in html_no_diag  # HTML always present
        assert "includeGeometryDiagnostics: false" in html_no_diag

        # With diagnostics enabled
        html_with_diag = model_to_gltf_html(model, include_geometry_diagnostics=True)
        assert "diagnostics-section" in html_with_diag
        assert "includeGeometryDiagnostics: true" in html_with_diag

    def test_script_fragment_also_has_api(self, model):
        """Test that the script fragment (not full HTML) also exposes the API."""
        script = model_to_gltf_script(model)
        assert "window.EffiBEMViewer" in script
        assert "window.runFromJSON" in script
        assert "window.runFromFile" in script

    def test_load_from_file_object_exposed(self, model):
        """Test that loadFromFileObject method is exposed for local file loading."""
        html = model_to_gltf_html(model)
        assert "loadFromFileObject(file)" in html
        assert "window.runFromFileObject" in html
        assert "FileReader" in html

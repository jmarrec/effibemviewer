#!/usr/bin/env python
"""Tests for `effibemviewer` gltf."""

import openstudio
import pytest

from effibemviewer import create_example_model
from effibemviewer.gltf import get_js_library, model_to_gltf_html, model_to_gltf_script


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

        # With diagnostics enabled (skip if not supported by OpenStudio version)
        has_diag_support = callable(
            getattr(openstudio.gltf.GltfForwardTranslator, "setIncludeGeometryDiagnostics", None)
        )
        if has_diag_support:
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


class TestEmbeddedVsExternal:
    """Tests for embedded vs external JS library modes."""

    def test_embedded_mode_has_importmap(self, model):
        """Test that embedded mode includes importmap and inline JS."""
        html = model_to_gltf_html(model, embedded=True)
        assert '<script type="importmap">' in html
        assert 'import * as THREE from "three"' in html
        assert "class EffiBEMViewer" in html

    def test_external_mode_references_js_file(self, model):
        """Test that external mode references the external JS file."""
        html = model_to_gltf_html(model, embedded=False, js_lib_path="./effibemviewer.js")
        assert '<script type="module" src="./effibemviewer.js">' in html
        assert "class EffiBEMViewer" not in html  # Class should not be inline

    def test_external_mode_custom_js_path(self, model):
        """Test that external mode uses custom JS library path."""
        html = model_to_gltf_html(model, embedded=False, js_lib_path="./js/viewer.js")
        assert '<script type="module" src="./js/viewer.js">' in html

    def test_importmap_always_present(self, model):
        """Test that importmap is present in both embedded and external modes."""
        html_embedded = model_to_gltf_html(model, embedded=True)
        html_external = model_to_gltf_html(model, embedded=False)
        for html in [html_embedded, html_external]:
            assert '<script type="importmap">' in html
            assert '"three": "https://unpkg.com/three@' in html

    def test_get_js_library(self):
        """Test that get_js_library produces JS with bare specifiers (requires importmap)."""
        js = get_js_library()
        assert 'import * as THREE from "three"' in js
        assert 'import { GLTFLoader } from "three/addons/' in js
        assert "class EffiBEMViewer" in js
        assert "export { EffiBEMViewer }" in js

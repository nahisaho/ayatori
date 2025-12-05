"""Tests for MCP Resources definitions."""

import pytest

from graphrag_mcp_server.server.resources import (
    STATIC_RESOURCES,
    RESOURCE_TEMPLATES,
    ENTITIES_RESOURCE,
    RELATIONSHIPS_RESOURCE,
    COMMUNITIES_RESOURCE,
    TEXT_UNITS_RESOURCE,
    STATISTICS_RESOURCE,
    get_resource_by_uri,
    list_resource_uris,
    list_resource_templates,
)


class TestStaticResources:
    """Tests for static resource definitions."""
    
    def test_static_resources_count(self):
        """Should have 7 static resources."""
        assert len(STATIC_RESOURCES) == 7
    
    def test_static_resources_have_required_fields(self):
        """Each static resource should have uri, name, description, mimeType."""
        for resource in STATIC_RESOURCES:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource
    
    def test_all_uris_start_with_graphrag(self):
        """All resource URIs should start with graphrag://."""
        for resource in STATIC_RESOURCES:
            assert resource["uri"].startswith("graphrag://")
    
    def test_all_mime_types_are_json(self):
        """All resources should return application/json."""
        for resource in STATIC_RESOURCES:
            assert resource["mimeType"] == "application/json"
    
    def test_entities_resource(self):
        """ENTITIES_RESOURCE should have correct structure."""
        assert ENTITIES_RESOURCE["uri"] == "graphrag://entities"
        assert ENTITIES_RESOURCE["name"] == "Entities"
    
    def test_relationships_resource(self):
        """RELATIONSHIPS_RESOURCE should have correct structure."""
        assert RELATIONSHIPS_RESOURCE["uri"] == "graphrag://relationships"
        assert RELATIONSHIPS_RESOURCE["name"] == "Relationships"
    
    def test_communities_resource(self):
        """COMMUNITIES_RESOURCE should have correct structure."""
        assert COMMUNITIES_RESOURCE["uri"] == "graphrag://communities"
        assert COMMUNITIES_RESOURCE["name"] == "Communities"
    
    def test_text_units_resource(self):
        """TEXT_UNITS_RESOURCE should have correct structure."""
        assert TEXT_UNITS_RESOURCE["uri"] == "graphrag://text_units"
        assert TEXT_UNITS_RESOURCE["name"] == "Text Units"
    
    def test_statistics_resource(self):
        """STATISTICS_RESOURCE should have correct structure."""
        assert STATISTICS_RESOURCE["uri"] == "graphrag://statistics"
        assert STATISTICS_RESOURCE["name"] == "Index Statistics"


class TestResourceTemplates:
    """Tests for resource template definitions."""
    
    def test_resource_templates_count(self):
        """Should have 4 resource templates."""
        assert len(RESOURCE_TEMPLATES) == 4
    
    def test_templates_have_uri_template(self):
        """Each template should have uriTemplate instead of uri."""
        for template in RESOURCE_TEMPLATES:
            assert "uriTemplate" in template
            assert "uri" not in template
    
    def test_templates_have_required_fields(self):
        """Each template should have required fields."""
        for template in RESOURCE_TEMPLATES:
            assert "name" in template
            assert "description" in template
            assert "mimeType" in template
    
    def test_template_uris_have_parameters(self):
        """Template URIs should contain parameter placeholders."""
        for template in RESOURCE_TEMPLATES:
            assert "{" in template["uriTemplate"]
            assert "}" in template["uriTemplate"]


class TestGetResourceByUri:
    """Tests for get_resource_by_uri function."""
    
    def test_get_existing_resource(self):
        """Should return resource for existing URI."""
        resource = get_resource_by_uri("graphrag://entities")
        assert resource is not None
        assert resource["name"] == "Entities"
    
    def test_get_all_static_resources(self):
        """Should be able to retrieve all static resources."""
        uris = [
            "graphrag://entities",
            "graphrag://relationships",
            "graphrag://communities",
            "graphrag://text_units",
            "graphrag://statistics",
            "graphrag://documents",
            "graphrag://covariates",
        ]
        for uri in uris:
            resource = get_resource_by_uri(uri)
            assert resource is not None
    
    def test_get_nonexistent_resource(self):
        """Should return None for nonexistent URI."""
        resource = get_resource_by_uri("graphrag://nonexistent")
        assert resource is None


class TestListResourceUris:
    """Tests for list_resource_uris function."""
    
    def test_list_returns_all_uris(self):
        """Should return all 7 static resource URIs."""
        uris = list_resource_uris()
        assert len(uris) == 7
    
    def test_list_contains_expected_uris(self):
        """Should contain expected URIs."""
        uris = list_resource_uris()
        expected = [
            "graphrag://entities",
            "graphrag://relationships",
            "graphrag://communities",
            "graphrag://text_units",
            "graphrag://statistics",
        ]
        for uri in expected:
            assert uri in uris
    
    def test_list_returns_strings(self):
        """All items should be strings."""
        uris = list_resource_uris()
        assert all(isinstance(uri, str) for uri in uris)


class TestListResourceTemplates:
    """Tests for list_resource_templates function."""
    
    def test_list_returns_copies(self):
        """Should return a copy of templates list."""
        templates1 = list_resource_templates()
        templates2 = list_resource_templates()
        assert templates1 is not templates2
    
    def test_list_returns_all_templates(self):
        """Should return all 4 templates."""
        templates = list_resource_templates()
        assert len(templates) == 4

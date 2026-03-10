"""
Central version configuration for GeoServer documentation.

This module provides version and release variables to mkdocs-macros-plugin,
ensuring consistent version numbers across all documentation manuals
(user, developer, docguide, and translations).

To update the version for a new release, simply change the values below.
"""


def define_env(env):
    """
    Define macros and variables for mkdocs-macros-plugin.
    
    This function is called by mkdocs-macros-plugin and allows us to
    define variables that will be available in all Markdown files.
    """
    
    # Central version configuration
    # Update these values when releasing a new version
    env.variables['version'] = '3.0'
    env.variables['release'] = '3.0.0'
    env.variables['snapshot'] = '3.0-SNAPSHOT'
    
    # Branch used for nightly build URLs
    branch = 'main'

    # Download URL templates
    # Usage: [geoserver-{{ release }}-war.zip]({{ download_release }}war)
    env.variables['download_release'] = (
        'https://sourceforge.net/projects/geoserver/files/GeoServer/'
        + env.variables['release'] + '/geoserver-' + env.variables['release'] + '-'
    )
    env.variables['download_extension'] = (
        'https://sourceforge.net/projects/geoserver/files/GeoServer/'
        + env.variables['release'] + '/extensions/geoserver-' + env.variables['release'] + '-'
    )
    # Usage: [geoserver-{{ snapshot }}-war.zip]({{ nightly_release }}war)
    env.variables['nightly_release'] = (
        'https://build.geoserver.org/geoserver/'
        + branch + '/geoserver-' + env.variables['snapshot'] + '-'
    )
    env.variables['nightly_extension'] = (
        'https://build.geoserver.org/geoserver/'
        + branch + '/extensions/geoserver-' + env.variables['snapshot'] + '-'
    )
    env.variables['nightly_community'] = (
        'https://build.geoserver.org/geoserver/'
        + branch + '/community-latest/geoserver-' + env.variables['snapshot'] + '-'
    )

    # Additional useful variables
    env.variables['geoserver_repo'] = 'https://github.com/geoserver/geoserver'
    env.variables['docs_url'] = 'https://docs.geoserver.org'
    
    # API base URL for REST API Swagger/OpenAPI specs
    # The Swagger UI is hosted at ../api/ and uses URL fragments to load specific YAML files
    # This resolves to the correct path regardless of where the documentation is deployed
    # Usage in Markdown: [API reference]({{ api_url }}/styles.yaml)
    env.variables['api_url'] = '../api/#1.0.0'
    
    # Load shared doc_switcher configuration
    # The doc_switcher provides navigation between different documentation types
    # (User Manual, Developer Manual, Documentation Guide, Swagger APIs)
    # This configuration is centralized in a single YAML file to avoid duplication
    # across the three mkdocs.yml files
    config_path = Path(__file__).parent / 'themes' / 'geoserver' / 'doc_switcher.yml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Inject doc_switcher into config.extra so it's available to theme templates
    # Theme templates can access this via {{ config.extra.doc_switcher }}
    env.conf['extra']['doc_switcher'] = config['doc_switcher']

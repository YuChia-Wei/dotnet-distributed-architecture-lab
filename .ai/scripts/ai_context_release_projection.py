"""Versioned release metadata used only for package input identity.

Source admission and provider policy still validate the current complete release
record. This projection cannot attest a release phase or authorize publication.
"""
from __future__ import annotations
import hashlib
import json
import re
import yaml

PROJECTION_SCHEMA = 'release-package-input/v1'
SELECTED_SCHEMA = 'package-selected-input/v2'
SOURCE_PROGRESS_FIELDS = frozenset({
    'status', 'tag', 'commit', 'tagged_at', 'recorded_at',
    'created_at', 'updated_at', 'validation',
})

def canonical_projection_bytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode('utf-8')

def projection_required(version: str) -> bool:
    if not isinstance(version, str) or not re.fullmatch(r'v?(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)', version):
        raise ValueError('release projection version is invalid')
    return tuple(map(int, version.lstrip('v').split('.'))) >= (0, 16, 0)

def validate_release_projection(value: dict, version: str) -> None:
    expected_version = 'v' + version.lstrip('v')
    if not projection_required(version):
        raise ValueError('release projection is not supported before v0.16.0')
    if not isinstance(value, dict) or set(value) != {'schema_version', 'source_path', 'fields'}:
        raise ValueError('release projection fields are incomplete or unexpected')
    if value['schema_version'] != PROJECTION_SCHEMA or value['source_path'] != f'.dev/releases/{expected_version}/release.yaml':
        raise ValueError('release projection authority is invalid')
    fields = value['fields']
    if not isinstance(fields, dict) or SOURCE_PROGRESS_FIELDS.intersection(fields):
        raise ValueError('release projection includes source progress fields')
    required = {'schema_version', 'version', 'release_id', 'compatibility', 'distribution'}
    if not required.issubset(fields) or fields['version'] != expected_version or fields['release_id'] != 'REL-' + expected_version:
        raise ValueError('release projection package identity is invalid')
    if not isinstance(fields['compatibility'], dict) or not isinstance(fields['distribution'], dict):
        raise ValueError('release projection contracts are invalid')
    canonical_projection_bytes(value)

def project_release_input(source_path: str, content: bytes) -> dict | None:
    match = re.fullmatch(r'\.dev/releases/(v\d+\.\d+\.\d+)/release\.yaml', source_path)
    if not match or not projection_required(match[1]):
        return None
    def unique_mapping(loader, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError('release input has duplicate or non-string mapping keys')
            result[key] = loader.construct_object(value_node, deep=deep)
        return result
    class ReleaseLoader(yaml.SafeLoader):
        pass
    ReleaseLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)
    release = yaml.load(content, Loader=ReleaseLoader)
    if not isinstance(release, dict):
        raise ValueError('release input must be a mapping')
    projection = {'schema_version': PROJECTION_SCHEMA, 'source_path': source_path,
                  'fields': {key: value for key, value in release.items() if key not in SOURCE_PROGRESS_FIELDS}}
    validate_release_projection(projection, match[1])
    return projection

def validate_selected_release_projection(proof: dict, version: str, package: dict | None = None) -> None:
    required = projection_required(version)
    expected_schema = SELECTED_SCHEMA if required else 'package-selected-input/v1'
    expected_fields = {'schema_version', 'source_inputs', 'payload', 'migration_sources'}
    if required:
        expected_fields.add('release_projection')
    if set(proof) != expected_fields or proof.get('schema_version') != expected_schema:
        raise ValueError('selected-input proof schema or projection boundary is invalid')
    if required:
        projection = proof['release_projection']
        validate_release_projection(projection, version)
        expected_digest = hashlib.sha256(canonical_projection_bytes(projection)).hexdigest()
        sources = proof.get('source_inputs')
        if not isinstance(sources, list):
            raise ValueError('release projection source input is missing')
        matching = [record for record in sources if isinstance(record, dict) and record.get('path') == projection['source_path']]
        if matching != [{'path': projection['source_path'], 'sha256': expected_digest}]:
            raise ValueError('release projection source input digest differs')
        if package is not None:
            fields = projection['fields']
            distribution = fields['distribution']
            compatibility = fields['compatibility']
            expected_compatibility = {
                'minimum_governed_source': compatibility.get('minimum_source_version'),
                'breaking_changes': compatibility.get('breaking_changes'),
                'automatic_upgrade_sources': compatibility.get('automatic_upgrade_sources'),
            }
            if (distribution.get('profile_id') != package.get('profile_id')
                    or distribution.get('package_id') != package.get('package_id')
                    or expected_compatibility != package.get('compatibility')):
                raise ValueError('release projection differs from the incoming package contract')

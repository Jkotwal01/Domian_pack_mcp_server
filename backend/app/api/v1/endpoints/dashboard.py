"""
Dashboard Endpoints - Refactored with OOP

Provides consolidated dashboard views using base endpoint classes.
"""

from fastapi import APIRouter
import yaml

from app.models.dashboard_models import (
    AllSessionsResponse,
    SessionSummary,
    AllVersionsResponse,
    VersionSummary,
    VersionYAMLResponse,
    CompareVersionsRequest,
    CompareVersionsResponse,
    VersionDiff
)
from app.api.base import DashboardEndpoint, VersionEndpoint, extract_domain_name, extract_semantic_version

router = APIRouter()

# Initialize handlers
dashboard_handler = DashboardEndpoint()
version_handler = VersionEndpoint()


@router.get("/sessions", response_model=AllSessionsResponse)
async def get_all_sessions():
    """Get all sessions with summary information."""
    
    @dashboard_handler.handle_db_errors
    async def _get():
        sessions_data = await dashboard_handler.get_all_sessions()
        
        session_summaries = []
        for session in sessions_data:
            # Get latest version to extract domain name
            try:
                latest = await version_handler.get_latest_version(str(session["session_id"]))
                domain_name = extract_domain_name(latest["content"])
            except:
                domain_name = "Unknown"
            
            session_summaries.append(SessionSummary(
                session_id=str(session["session_id"]),
                domain_name=domain_name,
                current_version=session["current_version"],
                total_versions=session["total_versions"],
                file_type=session["file_type"],
                created_at=session["created_at"],
                updated_at=session["updated_at"]
            ))
        
        return AllSessionsResponse(
            sessions=session_summaries,
            total=len(session_summaries)
        )
    
    return await _get()


@router.get("/versions/all", response_model=AllVersionsResponse)
async def get_all_versions():
    """Get all final versions across all sessions."""
    
    @dashboard_handler.handle_db_errors
    async def _get():
        versions_data = await dashboard_handler.get_all_versions()
        
        version_summaries = [
            VersionSummary(
                session_id=str(version["session_id"]),
                domain_name=extract_domain_name(version["content"]),
                version=version["version"],
                semantic_version=extract_semantic_version(version["content"]),
                file_type=version["file_type"],
                created_at=version["created_at"],
                reason=version["reason"]
            )
            for version in versions_data
        ]
        
        return AllVersionsResponse(
            versions=version_summaries,
            total=len(version_summaries)
        )
    
    return await _get()


@router.get("/versions/{session_id}/{version}/yaml", response_model=VersionYAMLResponse)
async def get_version_yaml(session_id: str, version: int):
    """Get a specific version as YAML formatted string."""
    
    @version_handler.handle_db_errors
    async def _get():
        version_data = await version_handler.get_version_data(session_id, version)
        content = version_data["content"]
        
        # Convert to YAML
        yaml_content = yaml.dump(
            content,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True
        )
        
        return VersionYAMLResponse(
            session_id=session_id,
            version=version,
            domain_name=extract_domain_name(content),
            yaml_content=yaml_content,
            created_at=version_data["created_at"]
        )
    
    return await _get()


@router.post("/compare", response_model=CompareVersionsResponse)
async def compare_versions(request: CompareVersionsRequest):
    """Compare two versions and return differences."""
    
    @version_handler.handle_db_errors
    async def _compare():
        # Get both versions
        version1_data = await version_handler.get_version_data(
            request.session_id_1,
            request.version_1
        )
        version2_data = await version_handler.get_version_data(
            request.session_id_2,
            request.version_2
        )
        
        content1 = version1_data["content"]
        content2 = version2_data["content"]
        
        # Compute differences
        differences = _compute_diff(content1, content2)
        
        # Generate YAML diff
        yaml_diff = _generate_yaml_diff(
            differences,
            request.version_1,
            request.version_2,
            extract_domain_name(content1),
            extract_domain_name(content2)
        )
        
        return CompareVersionsResponse(
            session_1=request.session_id_1,
            version_1=request.version_1,
            domain_1=extract_domain_name(content1),
            session_2=request.session_id_2,
            version_2=request.version_2,
            domain_2=extract_domain_name(content2),
            differences=differences,
            yaml_diff=yaml_diff,
            total_changes=len(differences)
        )
    
    return await _compare()


# ============================================================================
# Helper Functions
# ============================================================================

def _compute_diff(content1: dict, content2: dict, path: str = "") -> list[VersionDiff]:
    """Recursively compute differences between two content dictionaries."""
    diffs = []
    
    if isinstance(content1, dict) and isinstance(content2, dict):
        all_keys = set(content1.keys()) | set(content2.keys())
        
        for key in all_keys:
            current_path = f"{path}.{key}" if path else key
            
            if key not in content1:
                diffs.append(VersionDiff(
                    field=current_path,
                    old_value=None,
                    new_value=content2[key],
                    change_type="added"
                ))
            elif key not in content2:
                diffs.append(VersionDiff(
                    field=current_path,
                    old_value=content1[key],
                    new_value=None,
                    change_type="removed"
                ))
            elif content1[key] != content2[key]:
                if isinstance(content1[key], (dict, list)) and isinstance(content2[key], (dict, list)):
                    diffs.extend(_compute_diff(content1[key], content2[key], current_path))
                else:
                    diffs.append(VersionDiff(
                        field=current_path,
                        old_value=content1[key],
                        new_value=content2[key],
                        change_type="modified"
                    ))
    
    elif isinstance(content1, list) and isinstance(content2, list):
        max_len = max(len(content1), len(content2))
        for i in range(max_len):
            current_path = f"{path}[{i}]"
            
            if i >= len(content1):
                diffs.append(VersionDiff(
                    field=current_path,
                    old_value=None,
                    new_value=content2[i],
                    change_type="added"
                ))
            elif i >= len(content2):
                diffs.append(VersionDiff(
                    field=current_path,
                    old_value=content1[i],
                    new_value=None,
                    change_type="removed"
                ))
            elif content1[i] != content2[i]:
                if isinstance(content1[i], (dict, list)) and isinstance(content2[i], (dict, list)):
                    diffs.extend(_compute_diff(content1[i], content2[i], current_path))
                else:
                    diffs.append(VersionDiff(
                        field=current_path,
                        old_value=content1[i],
                        new_value=content2[i],
                        change_type="modified"
                    ))
    
    elif content1 != content2:
        diffs.append(VersionDiff(
            field=path or "root",
            old_value=content1,
            new_value=content2,
            change_type="modified"
        ))
    
    return diffs


def _generate_yaml_diff(
    differences: list[VersionDiff],
    version1: int,
    version2: int,
    domain1: str,
    domain2: str
) -> str:
    """Generate a YAML-formatted diff string."""
    yaml_diff = f"--- Version {version1} ({domain1})\n"
    yaml_diff += f"+++ Version {version2} ({domain2})\n\n"
    
    for diff in differences:
        if diff.change_type == "added":
            yaml_diff += f"+ {diff.field}: {diff.new_value}\n"
        elif diff.change_type == "removed":
            yaml_diff += f"- {diff.field}: {diff.old_value}\n"
        elif diff.change_type == "modified":
            yaml_diff += f"- {diff.field}: {diff.old_value}\n"
            yaml_diff += f"+ {diff.field}: {diff.new_value}\n"
    
    return yaml_diff

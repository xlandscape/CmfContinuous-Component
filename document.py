"""
Script for documenting the code of the CmfContinuous component.
"""
import os
import base.documentation
import CmfContinuous

root_folder = os.path.abspath(os.path.join(os.path.dirname(base.__file__), ".."))
base.documentation.document_component(
    CmfContinuous.CmfContinuous("CascadeToxswa", None, None),
    os.path.join(root_folder, "..", "variant", "CmfContinuous", "README.md"),
    os.path.join(root_folder, "..", "variant", "mc.xml")
)
base.documentation.write_changelog(
    "CmfContinuous component",
    CmfContinuous.CmfContinuous.VERSION,
    os.path.join(root_folder, "..", "variant", "CmfContinuous", "CHANGELOG.md")
)
base.documentation.write_contribution_notes(
    os.path.join(root_folder, "..", "variant", "CmfContinuous", "CONTRIBUTING.md"))
base.documentation.write_repository_info(
    os.path.join(root_folder, "..", "variant", "CmfContinuous"),
    os.path.join(root_folder, "..", "variant", "CmfContinuous", "repository.json"),
    os.path.join(root_folder, "..", "..", "..", "versions.json"),
    "component"
)

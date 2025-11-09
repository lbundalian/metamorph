import argparse
from typing import Dict, Set, List, Union
from pathlib import Path

from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS, OWL

OBOINOWL = Namespace("http://www.geneontology.org/formats/oboInOwl#")

def _extract_orpha_id_from_uri(uri: URIRef) -> Union[str, None]:

    s = str(uri)
    if s.rsplit("/", 1)[-1].startswith("Orphanet_"):
        try:
            num = s.rsplit("_", 1)[-1]
            int(num)  # validate it's numeric
            return f"ORPHA:{num}"
        except Exception:
            return None
    return None

def _extract_omim_from_xref(x: str) -> Union[str, None]:
   
    x = x.strip()
    if x.upper().startswith("OMIM:"):
        suffix = x.split(":", 1)[1].strip()
        if suffix.isdigit():
            return f"OMIM:{suffix}"
    if x.upper().startswith("MIM:"):
        suffix = x.split(":", 1)[1].strip()
        if suffix.isdigit():
            return f"OMIM:{suffix}"
    return None

class ORDOVersion:
    def __init__(self, owl_path: Union[str, Path]):
        self.owl_path = str(owl_path)
        self.graph = Graph()
        self.orpha_to_omim: Dict[str, Set[str]] = {}
        self._load()

    def _load(self):
        self.graph.parse(self.owl_path)
        # Iterate classes
        for cls in self.graph.subjects(RDF.type, OWL.Class):
            orpha_id = _extract_orpha_id_from_uri(cls)
            if not orpha_id:
                continue
            # collect OMIM xrefs from annotations oboInOwl:hasDbXref
            omims: Set[str] = set()
            for _, _, xref in self.graph.triples((cls, OBOINOWL.hasDbXref, None)):
                # xref can be Literal or URI; handle Literal strings
                if isinstance(xref, Literal):
                    omim = _extract_omim_from_xref(str(xref))
                    if omim:
                        omims.add(omim)
                else:
                    # Sometimes xrefs might be URIs; try to parse tail
                    omim = _extract_omim_from_xref(str(xref))
                    if omim:
                        omims.add(omim)
            if omims:
                self.orpha_to_omim[orpha_id] = omims

class ORDOMapper:
    def __init__(self, v14_path: Union[str, Path] = None, v47_path: Union[str, Path] = None):
        """
        Initialize ORDOMapper with ORDO OWL file paths.
        
        Args:
            v14_path: Path to ORDO v1.4 OWL file. If None, uses default path in workspace.
            v47_path: Path to ORDO v4.7 OWL file. If None, uses default path in workspace.
        """
        # Get the directory containing this file (ordolib.py)
        current_dir = Path(__file__).parent
        
        # Default paths relative to ordolib.py location
        # ordolib.py is in: src/metamorph/utils/
        # ORDO files are in: src/metamorph/utils/ordo/
        if v14_path is None:
            v14_path = current_dir / "ordo" / "ORDO_en_1.4.owl"
        if v47_path is None:
            v47_path = current_dir / "ordo" / "ORDO_en_4.7.owl"
        
        self.v14 = ORDOVersion(v14_path)
        self.v47 = ORDOVersion(v47_path)
        # Invert v4.7 mapping: OMIM -> set(ORPHA IDs v4.7)
        self.omim_to_v47_orpha: Dict[str, Set[str]] = {}
        for orpha, omims in self.v47.orpha_to_omim.items():
            for omim in omims:
                self.omim_to_v47_orpha.setdefault(omim, set()).add(orpha)

    # --- Function 1 ---
    def present_in_both(self, orpha_id: str) -> bool:
        """
        Return True if ORPHA ID exists (as a class) in both v1.4 and v4.7,
        based on the presence of OMIM xrefs in those versions.
        Note: If a term has no OMIM in a version, it might not be present in the map.
        To be safer, we also check raw presence as a class URI if possible.
        """
        def _exists(version: ORDOVersion, orpha_id: str) -> bool:
            # try via the stored mapping
            if orpha_id in version.orpha_to_omim:
                return True
            # fallback: try to find class URI directly in the graph even if no OMIM
            num = orpha_id.split(":", 1)[1] if ":" in orpha_id else orpha_id
            uri = URIRef(f"http://www.orpha.net/ORDO/Orphanet_{num}")
            return (uri, RDF.type, OWL.Class) in version.graph

        return _exists(self.v14, orpha_id) and _exists(self.v47, orpha_id)

    # --- Function 2 ---
    def map_via_omim(self, orpha_id_v14: str) -> Union[List[str], str]:
        """
        Given an ORPHA ID from v1.4, use its OMIM xrefs to find corresponding
        v4.7 ORPHA IDs. Return a list of ORPHA IDs (possibly multiple if
        v1.4 term split across multiple v4.7 terms). If none found, return 'NOT VALID'.
        """
        omims = self.v14.orpha_to_omim.get(orpha_id_v14, set())
        results: Set[str] = set()
        for omim in omims:
            results.update(self.omim_to_v47_orpha.get(omim, set()))
        if results:
            return sorted(results)
        return "NOT VALID"

def _build_arg_parser():
    p = argparse.ArgumentParser(description="ORDO ORPHA mapper using OMIM cross-references.")
    p.add_argument("--v14", required=True, help="Path to ORDO v1.4 OWL file")
    p.add_argument("--v47", required=True, help="Path to ORDO v4.7 OWL file")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--present", help="ORPHA ID to test presence in both versions (e.g., ORPHA:1234)")
    g.add_argument("--map", dest="map_orpha", help="ORPHA ID from v1.4 to map to v4.7 via OMIM")
    return p

def main():
    args = _build_arg_parser().parse_args()
    mapper = ORDOMapper(args.v14, args.v47)
    if args.present:
        print(mapper.present_in_both(args.present))
    else:
        print(mapper.map_via_omim(args.map_orpha))

if __name__ == "__main__":
    main()

from custom_service.scanner import facescanner

_ALL_SCANNERS = [facescanner.MockScanner, facescanner.ScannerWithPluggins]

id_2_face_scanner_cls = {backend.ID: backend for backend in _ALL_SCANNERS}
TESTED_SCANNERS = [facescanner.ScannerWithPluggins]


scanner = facescanner.ScannerWithPluggins()

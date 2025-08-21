"""
PDF Text Extraction Module - pdfplumber/fitz based extraction
"""
import fitz  # PyMuPDF
import logging
from typing import List, Dict, Optional
import unicodedata
import re

logger = logging.getLogger(__name__)

class PDFExtractor:
    """PDF text extraction with position and font information"""
    
    def __init__(self):
        self.logger = logger
    
    def _normalize_for_pdf_search(self, s: str) -> str:
        """Normalize text for PDF search operations"""
        s = unicodedata.normalize("NFKC", s)
        s = s.replace("\u00A0", " ").replace("\u2009", " ").replace("\u202F", " ")
        s = re.sub(r"[ \t]+", " ", s).strip()
        return s
    
    def _candidate_queries(self, orig: str) -> List[str]:
        """Generate candidate search queries for PDF text"""
        base = self._normalize_for_pdf_search(orig or "")
        cand = {base}

        # Space/punctuation normalizations
        cand.add(re.sub(r"\s*([./-])\s*", r"\1", base))
        cand.add(re.sub(r"\s+", " ", base))
        if len(base) <= 64:
            cand.add(base.replace(" ", ""))

        # Case variants
        cand.add(base.upper())
        cand.add(base.lower())
        cand.add(base.title())

        return [c for c in cand if c]
    
    def extract_text_with_positions(self, pdf_path: str) -> List[Dict]:
        """
        Extract text from PDF with position and font information
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of text blocks with position and formatting info
        """
        try:
            doc = fitz.open(pdf_path)
            text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                blocks = page.get_text("dict")
                
                for block in blocks.get("blocks", []):
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line.get("spans", []):
                                text = (span.get("text") or "").strip()
                                if text:
                                    bbox_raw = span.get("bbox", (0, 0, 0, 0))
                                    if hasattr(bbox_raw, "__iter__"):
                                        bbox = tuple(float(x) for x in bbox_raw)
                                    else:
                                        try:
                                            bbox = (float(bbox_raw.x0), float(bbox_raw.y0),
                                                    float(bbox_raw.x1), float(bbox_raw.y1))
                                        except Exception:
                                            bbox = (0.0, 0.0, 0.0, 0.0)

                                    text_blocks.append({
                                        'page': int(page_num),
                                        'text': text,
                                        'bbox': bbox,
                                        'font': str(span.get("font") or "Unknown"),
                                        'size': float(span.get("size", 12)),
                                        'flags': int(span.get("flags", 0)),
                                        'color': int(span.get("color", 0)) if isinstance(span.get("color", 0), (int, float)) else 0,
                                        'start_char': 0,
                                        'end_char': 0
                                    })
            
            doc.close()

            # Calculate global positions
            char_position = 0
            for block in text_blocks:
                block['start_char'] = int(char_position)
                char_position += len(block['text']) + 1
                block['end_char'] = int(char_position - 1)

            return text_blocks
            
        except Exception as e:
            self.logger.error(f"Text extraction error: {e}")
            return []
    
    def find_text_block_for_position(self, start_pos: int, end_pos: int, 
                                   text_blocks: List[Dict], full_text: str) -> Dict:
        """
        Find text block information for given position
        
        Args:
            start_pos: Start position in full text
            end_pos: End position in full text
            text_blocks: List of text blocks
            full_text: Full extracted text
            
        Returns:
            Dict with block information
        """
        current_pos = 0

        for block in text_blocks:
            block_text = block['text']
            block_start = current_pos
            block_end = current_pos + len(block_text)

            if start_pos >= block_start and end_pos <= block_end + 1:
                relative_start = start_pos - block_start
                relative_end = end_pos - block_start

                return {
                    'page': block['page'],
                    'bbox': block['bbox'],
                    'font': block['font'],
                    'size': block['size'],
                    'flags': block['flags'],
                    'color': block['color'],
                    'relative_start': relative_start,
                    'relative_end': relative_end,
                    'block_text': block_text
                }

            current_pos = block_end + 1

        # Fallback
        return {
            'page': 0,
            'bbox': (0, 0, 100, 20),
            'font': 'Arial',
            'size': 12,
            'flags': 0,
            'color': 0,
            'relative_start': 0,
            'relative_end': 0,
            'block_text': ''
        }
    
    def search_quads_near(self, page, query: str, ref_bbox, max_hits=64):
        """Search for text quads near reference bounding box"""
        try:
            tp = page.get_textpage()

            flags = 0
            for name in ("TEXT_SEARCH_IGNORE_CASE", "TEXT_IGNORECASE"):
                if hasattr(fitz, name):
                    flags |= getattr(fitz, name)

            try:
                hits = tp.search(query, hit_max=max_hits, quads=True, flags=flags)
            except TypeError:
                hits = tp.search(query, hit_max=max_hits, quads=True)

            if not hits:
                return None

            rx0, ry0, rx1, ry1 = ref_bbox
            best, best_dist = None, float("inf")
            for h in hits:
                q = h[0] if isinstance(h, (list, tuple)) else h
                rect = fitz.Rect(q.rect) if hasattr(q, "rect") else fitz.Rect(q)
                dist = abs(rect.x0 - rx0) + abs(rect.y0 - ry0)
                if dist < best_dist:
                    best, best_dist = h, dist
            return best
        except Exception:
            return None
    
    def rect_from_block_slice_chars(self, page, text_block_info) -> Optional[fitz.Rect]:
        """Get rectangle from character bboxes in block slice"""
        try:
            block_text = text_block_info.get('block_text', '')
            rel_s = int(text_block_info.get('relative_start', 0))
            rel_e = int(text_block_info.get('relative_end', 0))
            if not block_text or rel_e <= rel_s:
                return None

            target_text_norm = self._normalize_for_pdf_search(block_text)
            bx0, by0, bx1, by1 = text_block_info.get('bbox', (0,0,0,0))

            raw = page.get_text("rawdict")
            for b in raw.get("blocks", []):
                for l in b.get("lines", []):
                    for s in l.get("spans", []):
                        span_text = (s.get("text") or "")
                        span_bbox = s.get("bbox", None)
                        if not span_bbox:
                            continue

                        span_text_norm = self._normalize_for_pdf_search(span_text)
                        sx0, sy0, sx1, sy1 = span_bbox
                        bbox_dist = abs(sx0 - bx0) + abs(sy0 - by0)

                        if span_text_norm == target_text_norm and bbox_dist < 10.0:
                            chars = s.get("chars")
                            if not chars:
                                total_w = sx1 - sx0
                                if total_w <= 0:
                                    return fitz.Rect(span_bbox)
                                frac_s = rel_s / max(len(span_text), 1)
                                frac_e = rel_e / max(len(span_text), 1)
                                x0 = sx0 + total_w * frac_s
                                x1 = sx0 + total_w * frac_e
                                return fitz.Rect(min(x0,x1), sy0, max(x0,x1), sy1)

                            xs, ys = [], []
                            N = len(chars)
                            a = max(0, min(rel_s, N-1))
                            bnd = max(a+1, min(rel_e, N))
                            for ch in chars[a:bnd]:
                                cb = ch.get("bbox")
                                if not cb:
                                    continue
                                cx0, cy0, cx1, cy1 = cb
                                xs.extend([cx0, cx1]); ys.extend([cy0, cy1])

                            if xs and ys:
                                return fitz.Rect(min(xs), min(ys), max(xs), max(ys))
                            return fitz.Rect(span_bbox)
            return None
        except Exception:
            return None
    
    def rects_from_hit(self, hit) -> List[fitz.Rect]:
        """Extract rectangles from search hit"""
        rects = []
        def to_rect(obj):
            if isinstance(obj, fitz.Rect):
                return obj
            if hasattr(obj, "rect"):
                try: return fitz.Rect(obj.rect)
                except Exception: pass
            if isinstance(obj, (list, tuple)) and len(obj) == 4 and all(hasattr(p, "x") and hasattr(p, "y") for p in obj):
                xs = [p.x for p in obj]; ys = [p.y for p in obj]
                return fitz.Rect(min(xs), min(ys), max(xs), max(ys))
            return None
        def walk(o):
            r = to_rect(o)
            if r is not None:
                rects.append(r); return
            if isinstance(o, (list, tuple)):
                for it in o: walk(it)
        walk(hit)
        return [fitz.Rect(r) for r in rects if r is not None]
"""
PDF Redaction Module - Real deletion/censoring operations
"""
import fitz  # PyMuPDF
import logging
import numpy as np
from typing import List, Dict

logger = logging.getLogger(__name__)

class PDFRedactor:
    """PDF redaction operations - real deletion and censoring"""
    
    def __init__(self):
        self.logger = logger
    
    def sample_background_color(self, page, rect, margin=1.5, ring=4) -> tuple:
        """
        Sample background color around rectangle
        
        Args:
            page: PDF page object
            rect: Rectangle to sample around
            margin: Inner margin
            ring: Outer ring width
            
        Returns:
            RGB color tuple (0-1 range)
        """
        try:
            r = fitz.Rect(rect)
            outer = fitz.Rect(r).inflate(margin + ring)
            inner = fitz.Rect(r).inflate(margin)

            pm = page.get_pixmap(clip=outer, alpha=False)
            w, h, n = pm.width, pm.height, pm.n

            arr = np.frombuffer(pm.samples, dtype=np.uint8).reshape(h, w, n)
            rgb = arr[:, :, :3] if n >= 3 else np.repeat(arr, 3, axis=2)

            sx = w / max(outer.width, 1e-6)
            sy = h / max(outer.height, 1e-6)
            ix0 = max(0, min(w, int((inner.x0 - outer.x0) * sx)))
            iy0 = max(0, min(h, int((inner.y0 - outer.y0) * sy)))
            ix1 = max(0, min(w, int((inner.x1 - outer.x1) * sx)))
            iy1 = max(0, min(h, int((inner.y1 - outer.y0) * sy)))

            mask = np.ones((h, w), dtype=bool)
            mask[iy0:iy1, ix0:ix1] = False

            samples = rgb[mask]
            if samples.size == 0:
                samples = rgb.reshape(-1, 3)

            # Filter very dark pixels
            lum = 0.2126 * samples[:, 0] + 0.7152 * samples[:, 1] + 0.0722 * samples[:, 2]
            use = lum > 60
            if np.sum(use) >= 50:
                samples = samples[use]

            med = np.median(samples, axis=0)
            return (float(med[0] / 255.0), float(med[1] / 255.0), float(med[2] / 255.0))
        except Exception:
            return (0.96, 0.96, 0.96)
    
    def apply_redaction_to_rects(self, page, rects: List[fitz.Rect], 
                                background_color: tuple = None) -> bool:
        """
        Apply redaction (deletion) to list of rectangles
        
        Args:
            page: PDF page object
            rects: List of rectangles to redact
            background_color: Background color (auto-sampled if None)
            
        Returns:
            True if successful
        """
        try:
            if not rects:
                return False
            
            # Sample background color if not provided
            if background_color is None:
                background_color = self.sample_background_color(page, rects[0])
            
            # Add redaction annotations
            for rect in rects:
                page.add_redact_annot(rect, fill=background_color)
            
            # Apply redactions (permanently removes text)
            page.apply_redactions()
            return True
            
        except Exception as e:
            self.logger.error(f"Redaction error: {e}")
            return False
    
    def censor_text_with_stars(self, original_text: str) -> str:
        """
        Create censored text with asterisks
        
        Args:
            original_text: Original text to censor
            
        Returns:
            Text with same length but asterisks
        """
        return '*' * len(original_text.strip())
    
    def redact_entity_locations(self, page, entity: Dict, extractor) -> bool:
        """
        Redact entity at specific locations in PDF
        
        Args:
            page: PDF page object
            entity: Entity information dict
            extractor: PDFExtractor instance for helper methods
            
        Returns:
            True if successful
        """
        try:
            original_text = (entity.get('word') or '').strip()
            if not original_text:
                return False

            text_block_info = entity.get('text_block_info') or {}
            bbox = text_block_info.get('bbox')
            if not bbox:
                return False

            block_text = text_block_info.get('block_text', '')
            rel_s = int(text_block_info.get('relative_start', 0))
            rel_e = int(text_block_info.get('relative_end', 0))
            block_slice = block_text[rel_s:rel_e] if (0 <= rel_s <= len(block_text) and 0 <= rel_e <= len(block_text)) else ''
            search_text = (block_slice or original_text).strip()

            # Generate candidate search queries
            candidates = extractor._candidate_queries(search_text) or [search_text]

            # Search for text quads
            hit_quads = None
            for q in candidates:
                hit_quads = extractor.search_quads_near(page, q, bbox)
                if hit_quads:
                    break

            # Fallback to character-based rectangle
            if not hit_quads:
                char_rect = extractor.rect_from_block_slice_chars(page, text_block_info)
                if char_rect:
                    rects = [char_rect]
                else:
                    return False
            else:
                rects = extractor.rects_from_hit(hit_quads)

            if not rects:
                return False

            # Apply redaction
            return self.apply_redaction_to_rects(page, rects)

        except Exception as e:
            self.logger.error(f"Entity redaction error: {e}")
            return False
    
    def process_pdf_redaction(self, input_path: str, entities: List[Dict], 
                             output_path: str, extractor, progress_callback=None) -> bool:
        """
        Process PDF with redaction (complete removal)
        
        Args:
            input_path: Input PDF path
            entities: List of entities to redact
            output_path: Output PDF path
            extractor: PDFExtractor instance
            progress_callback: Progress callback function
            
        Returns:
            True if successful
        """
        try:
            doc = fitz.open(input_path)
            total_redactions = 0

            if progress_callback:
                progress_callback(0.6, desc="Applying redactions...")

            # Group entities by page
            entities_by_page = {}
            for entity in entities:
                page_num = entity.get('text_block_info', {}).get('page', 0)
                if page_num not in entities_by_page:
                    entities_by_page[page_num] = []
                entities_by_page[page_num].append(entity)

            # Process each page
            for page_num in range(len(doc)):
                if page_num not in entities_by_page:
                    continue

                page = doc.load_page(page_num)
                page_entities = entities_by_page[page_num]

                if progress_callback:
                    progress_callback(0.6 + (page_num / len(doc)) * 0.3, 
                                    desc=f"Redacting page {page_num + 1}/{len(doc)}...")

                # Sort entities by position (reverse order for proper processing)
                page_entities.sort(key=lambda x: x.get('start', 0), reverse=True)

                for entity in page_entities:
                    success = self.redact_entity_locations(page, entity, extractor)
                    if success:
                        total_redactions += 1

            doc.save(output_path)
            doc.close()

            self.logger.info(f"Redaction complete: {total_redactions} items redacted")
            return total_redactions > 0

        except Exception as e:
            self.logger.error(f"PDF redaction processing error: {e}")
            return False
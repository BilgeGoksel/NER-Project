"""
PDF Replacement Module - Font-preserving text replacement
"""
import fitz  # PyMuPDF
import logging
import random
from typing import List, Dict, Optional
from pdf.redact import PDFRedactor

logger = logging.getLogger(__name__)

class PDFReplacer:
    """PDF text replacement with font preservation"""
    
    def __init__(self):
        self.logger = logger
        self.redactor = PDFRedactor()
    
    def calculate_optimal_font_size(self, replacement_text: str, target_rect: fitz.Rect, 
                                  original_font_size: float) -> float:
        """
        Calculate optimal font size to fit replacement text in target rectangle
        
        Args:
            replacement_text: Text to fit
            target_rect: Target rectangle
            original_font_size: Original font size
            
        Returns:
            Optimal font size
        """
        try:
            rect_width = target_rect.width
            text_width = fitz.get_text_length(replacement_text, fontname='helv', 
                                            fontsize=original_font_size)
            
            if text_width > rect_width * 1.1:
                optimal_size = max(original_font_size * (rect_width / max(text_width, 1e-6)) * 0.9, 6)
                return optimal_size
            
            return original_font_size
            
        except Exception:
            return max(original_font_size * 0.8, 6)
    
    def convert_color_to_rgb(self, font_color) -> tuple:
        """
        Convert font color to RGB tuple
        
        Args:
            font_color: Font color (various formats)
            
        Returns:
            RGB tuple (0-1 range)
        """
        try:
            if isinstance(font_color, int):
                return (
                    ((font_color >> 16) & 255) / 255.0,
                    ((font_color >> 8) & 255) / 255.0,
                    (font_color & 255) / 255.0
                )
            elif isinstance(font_color, (list, tuple)) and len(font_color) >= 3:
                return tuple(font_color[:3])
            else:
                return (0, 0, 0)  # Black default
        except Exception:
            return (0, 0, 0)
    
    def replace_entity_with_font_preservation(self, page, entity: Dict, extractor) -> bool:
        """
        Replace entity while preserving font characteristics
        
        Args:
            page: PDF page object
            entity: Entity information dict
            extractor: PDFExtractor instance
            
        Returns:
            True if successful
        """
        try:
            original_text = (entity.get('word') or '').strip()
            replacement_text = (entity.get('replacement') or original_text).strip()
            
            if not original_text or replacement_text == original_text:
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

            # Step 1: Redact original text
            success = self.redactor.apply_redaction_to_rects(page, rects)
            if not success:
                return False

            # Step 2: Insert replacement text with font preservation
            first_rect = rects[0]
            font_size = float(text_block_info.get('size', 12.0))
            font_color = text_block_info.get('color', 0)

            # Convert color
            rgb_color = self.convert_color_to_rgb(font_color)

            # Calculate optimal font size
            font_size = self.calculate_optimal_font_size(replacement_text, first_rect, font_size)

            # Insert replacement text
            insert_point = (first_rect.x0, first_rect.y1 - 2)
            page.insert_text(
                insert_point,
                replacement_text,
                fontsize=font_size,
                fontname='helv',
                color=rgb_color,
                render_mode=0
            )

            return True

        except Exception as e:
            self.logger.error(f"Entity replacement error: {e}")
            return False
    
    def process_pdf_replacement(self, input_path: str, entities: List[Dict], 
                               output_path: str, extractor, progress_callback=None) -> bool:
        """
        Process PDF with font-preserving replacement
        
        Args:
            input_path: Input PDF path
            entities: List of entities to replace
            output_path: Output PDF path
            extractor: PDFExtractor instance
            progress_callback: Progress callback function
            
        Returns:
            True if successful
        """
        try:
            doc = fitz.open(input_path)
            total_replacements = 0

            if progress_callback:
                progress_callback(0.6, desc="Applying font-preserving replacements...")

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
                                    desc=f"Replacing page {page_num + 1}/{len(doc)}...")

                # Sort entities by position (reverse order for proper processing)
                page_entities.sort(key=lambda x: x.get('start', 0), reverse=True)

                for entity in page_entities:
                    success = self.replace_entity_with_font_preservation(page, entity, extractor)
                    if success:
                        total_replacements += 1

            doc.save(output_path)
            doc.close()

            self.logger.info(f"Font-preserving replacement complete: {total_replacements} replacements")
            return total_replacements > 0

        except Exception as e:
            self.logger.error(f"PDF replacement processing error: {e}")
            return False
    
    def process_pdf_censoring(self, input_path: str, entities: List[Dict], 
                             output_path: str, extractor, progress_callback=None) -> bool:
        """
        Process PDF with censoring (star replacement)
        
        Args:
            input_path: Input PDF path
            entities: List of entities to censor
            output_path: Output PDF path
            extractor: PDFExtractor instance
            progress_callback: Progress callback function
            
        Returns:
            True if successful
        """
        try:
            # Apply censoring strategy to entities
            for entity in entities:
                original = entity.get('word', '').strip()
                entity['replacement'] = self.redactor.censor_text_with_stars(original)
            
            # Use regular replacement process with star text
            return self.process_pdf_replacement(input_path, entities, output_path, 
                                              extractor, progress_callback)
            
        except Exception as e:
            self.logger.error(f"PDF censoring processing error: {e}")
            return False
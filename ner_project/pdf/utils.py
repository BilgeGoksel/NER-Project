"""
PDF Utils Module - Common utilities and helper functions
"""
import os
import logging
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import unicodedata
import re

logger = logging.getLogger(__name__)

class PDFUtils:
    """Common utilities for PDF processing"""
    
    @staticmethod
    def ensure_directories_exist(directories: List[str]) -> None:
        """
        Ensure directories exist, create if not
        
        Args:
            directories: List of directory paths
        """
        for dir_name in directories:
            os.makedirs(dir_name, exist_ok=True)
    
    @staticmethod
    def generate_timestamp_filename(prefix: str, original_filename: str, suffix: str = "") -> str:
        """
        Generate timestamped filename
        
        Args:
            prefix: Filename prefix
            original_filename: Original filename
            suffix: Optional suffix
            
        Returns:
            Timestamped filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = os.path.basename(original_filename)
        
        if suffix:
            return f"{prefix}_{timestamp}_{suffix}_{base_name}"
        else:
            return f"{prefix}_{timestamp}_{base_name}"
    
    @staticmethod
    def copy_uploaded_file(source_file, target_directory: str, new_filename: str) -> str:
        """
        Copy uploaded file to target directory
        
        Args:
            source_file: Source file object
            target_directory: Target directory path
            new_filename: New filename
            
        Returns:
            Target file path
        """
        source_path = source_file.name if hasattr(source_file, "name") else str(source_file)
        target_path = os.path.join(target_directory, new_filename)
        
        shutil.copy2(source_path, target_path)
        return target_path
    
    @staticmethod
    def normalize_text_for_search(text: str) -> str:
        """
        Normalize text for PDF search operations
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Unicode normalization
        text = unicodedata.normalize("NFKC", text)
        
        # Replace various space characters with regular space
        text = text.replace("\u00A0", " ").replace("\u2009", " ").replace("\u202F", " ")
        
        # Normalize multiple spaces to single space
        text = re.sub(r"[ \t]+", " ", text).strip()
        
        return text
    
    @staticmethod
    def split_text_into_chunks(text: str, max_length: int = 512, overlap: int = 50) -> List[Dict]:
        """
        Split text into overlapping chunks for processing
        
        Args:
            text: Input text
            max_length: Maximum chunk length
            overlap: Overlap between chunks
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + max_length, len(text))
            
            # Try to break at word boundary
            if end < len(text):
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_text = text[start:end]
            chunks.append({
                'text': chunk_text,
                'start_offset': start,
                'end_offset': end
            })
            
            start = max(start + 1, end - overlap)
        
        return chunks
    
    @staticmethod
    def calculate_text_similarity(text1: str, text2: str) -> float:
        """
        Calculate simple text similarity based on character overlap
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # Normalize texts
        t1 = PDFUtils.normalize_text_for_search(text1.lower())
        t2 = PDFUtils.normalize_text_for_search(text2.lower())
        
        if t1 == t2:
            return 1.0
        
        # Simple character-based similarity
        set1 = set(t1)
        set2 = set(t2)
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def validate_file_path(file_path: str, allowed_extensions: List[str] = None) -> bool:
        """
        Validate file path and extension
        
        Args:
            file_path: File path to validate
            allowed_extensions: List of allowed extensions (e.g., ['.pdf'])
            
        Returns:
            True if valid
        """
        if not file_path or not os.path.exists(file_path):
            return False
        
        if allowed_extensions:
            file_ext = os.path.splitext(file_path)[1].lower()
            return file_ext in [ext.lower() for ext in allowed_extensions]
        
        return True
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """
        Create safe filename by removing/replacing problematic characters
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Remove or replace problematic characters
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove multiple underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        
        # Trim and ensure not empty
        safe_name = safe_name.strip('_')
        
        if not safe_name:
            safe_name = "unnamed"
        
        return safe_name
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        Get file size in MB
        
        Args:
            file_path: Path to file
            
        Returns:
            File size in MB
        """
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except OSError:
            return 0.0
    
    @staticmethod
    def cleanup_temp_files(directory: str, max_age_hours: int = 24) -> int:
        """
        Cleanup temporary files older than specified age
        
        Args:
            directory: Directory to clean
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of files deleted
        """
        if not os.path.exists(directory):
            return 0
        
        deleted_count = 0
        current_time = datetime.now()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                if os.path.isfile(file_path):
                    file_age = current_time - datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_age.total_seconds() > max_age_seconds:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Deleted old temp file: {filename}")
        
        except Exception as e:
            logger.error(f"Error during temp file cleanup: {e}")
        
        return deleted_count
    
    @staticmethod
    def log_processing_stats(operation: str, entities_count: int, processing_time: float, 
                           input_file: str, output_file: str) -> None:
        """
        Log processing statistics
        
        Args:
            operation: Operation name
            entities_count: Number of entities processed
            processing_time: Processing time in seconds
            input_file: Input file path
            output_file: Output file path
        """
        input_size = PDFUtils.get_file_size_mb(input_file)
        output_size = PDFUtils.get_file_size_mb(output_file) if os.path.exists(output_file) else 0
        
        logger.info(f"""
        Processing Statistics:
        - Operation: {operation}
        - Entities processed: {entities_count}
        - Processing time: {processing_time:.2f} seconds
        - Input file size: {input_size:.2f} MB
        - Output file size: {output_size:.2f} MB
        - Input file: {os.path.basename(input_file)}
        - Output file: {os.path.basename(output_file)}
        """)
    
    @staticmethod
    def create_processing_report(entities: List[Dict], operation: str) -> Dict:
        """
        Create processing report
        
        Args:
            entities: List of processed entities
            operation: Operation name
            
        Returns:
            Report dictionary
        """
        # Count entities by type
        entity_counts = {}
        total_confidence = 0
        
        for entity in entities:
            entity_type = entity.get('entity', 'unknown')
            entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1
            total_confidence += entity.get('score', 0)
        
        avg_confidence = total_confidence / len(entities) if entities else 0
        
        return {
            'operation': operation,
            'total_entities': len(entities),
            'entity_types': entity_counts,
            'average_confidence': avg_confidence,
            'timestamp': datetime.now().isoformat()
        }
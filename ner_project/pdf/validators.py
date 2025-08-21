"""
Enhanced PDF Validators - Updated with Consistency and Performance Improvements
"""
import random
import re
import logging
from typing import List, Dict, Optional, Any, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ReplacementStats:
    """Statistics for replacement operations"""
    total_processed: int = 0
    successful_replacements: int = 0
    fallback_used: int = 0
    no_replacement_found: int = 0
    exact_length_matches: int = 0
    closest_length_matches: int = 0


class PDFValidators:
    def __init__(self, organized_data: Dict):
        self.organized_data = organized_data
        self.replacement_cache = {}
        self.used_replacements = set()  # Track used replacements globally
        self.used_replacements_by_type = defaultdict(set)  # Track per entity type
        self.logger = logging.getLogger(__name__)
        self.replacement_stats = ReplacementStats()
        self.consistent_mappings = {}  # Orijinal -> değişiklik eşlemelerini takip et
        # Pre-calculate available data for performance
        self._preprocess_data()

    def _preprocess_data(self) -> None:
        """Pre-calculate available data counts for better performance"""
        self.available_counts = {}
        self.total_available_by_type = {}
        
        for entity_type, length_data in self.organized_data.items():
            self.available_counts[entity_type] = {}
            total_count = 0
            
            for length, samples in length_data.items():
                count = len(samples) if samples else 0
                self.available_counts[entity_type][length] = count
                total_count += count
            
            self.total_available_by_type[entity_type] = total_count
            
        self.logger.info(f"Preprocessed data for {len(self.organized_data)} entity types")

    def apply_replacement_strategy_consistent(self, entities: List[Dict]) -> List[Dict]:
        """
        Apply replacement strategy using ONLY custom lists
        Each replacement can only be used once across all entities
        Enhanced with better error handling and statistics
        """
        if not entities:
            self.logger.warning("No entities provided for replacement")
            return []

        processed_entities = []
        self.replacement_stats = ReplacementStats()  # Reset stats
        
        # Reset used replacements for this batch
        self.used_replacements.clear()
        self.used_replacements_by_type.clear()
        
        # Group entities by type for better processing
        entities_by_type = defaultdict(list)
        for entity in entities:
            entity_type = entity.get('entity', 'UNKNOWN')
            entities_by_type[entity_type].append(entity)
        
        self.logger.info(f"Processing {len(entities)} entities across {len(entities_by_type)} types")
        
        for entity_type, type_entities in entities_by_type.items():
            self.logger.debug(f"Processing {len(type_entities)} entities of type '{entity_type}'")
            
            for entity in type_entities:
                self.replacement_stats.total_processed += 1
                processed_entity = self._process_single_entity(entity, entity_type)
                processed_entities.append(processed_entity)
        
        self._log_replacement_statistics()
        return processed_entities

    def _process_single_entity(self, entity: Dict, entity_type: str) -> Dict:
        """Process a single entity for replacement"""
        try:
            original_text = entity.get('word', '')
            if not original_text:
                self.logger.warning(f"Empty word in entity: {entity}")
                entity['replacement'] = ''
                return entity

            original_length = len(original_text)
            
            # Get unique replacement from custom lists only
            replacement = self._get_unique_custom_list_replacement(
                entity_type, original_text, original_length
            )
            
            if replacement and replacement != original_text:
                entity['replacement'] = replacement
                # Mark as used
                self.used_replacements.add(replacement.lower())
                self.used_replacements_by_type[entity_type].add(replacement.lower())
                self.replacement_stats.successful_replacements += 1
                
                self.logger.debug(f"Replaced '{original_text}' with '{replacement}' (type: {entity_type})")
            else:
                # If no unique replacement found, keep original
                entity['replacement'] = original_text
                self.replacement_stats.no_replacement_found += 1
                
                if not replacement:
                    self.logger.warning(f"No unique replacement found for '{original_text}' (type: {entity_type}, length: {original_length})")
                else:
                    self.logger.debug(f"Using original text for '{original_text}' (no different replacement available)")
            
            return entity
                
        except Exception as e:
            self.logger.error(f"Error processing entity {entity}: {e}")
            entity['replacement'] = entity.get('word', '')  # Keep original on error
            return entity

    def _get_unique_custom_list_replacement(self, entity_type: str, original_text: str, target_length: int) -> Optional[str]:
        """
        Get unique replacement from custom lists only with improved caching
        Each replacement can only be used once
        """
        # Check cache first, but only if it's not already used
        cache_key = f"{entity_type}_{original_text}_{target_length}"
        if cache_key in self.replacement_cache:
            cached_replacement = self.replacement_cache[cache_key]
            if cached_replacement.lower() not in self.used_replacements:
                return cached_replacement
            else:
                # Remove from cache since it's already used
                del self.replacement_cache[cache_key]
        
        # Validate entity type availability
        if not self._is_entity_type_available(entity_type):
            return None
        
        type_data = self.organized_data[entity_type]
        replacement = None
        
        # Strategy 1: Exact length match with unique replacements
        if target_length in type_data and type_data[target_length]:
            replacement = self._get_unique_replacement_from_length(
                type_data[target_length], original_text, entity_type, target_length
            )
            if replacement:
                self.replacement_stats.exact_length_matches += 1
                self.logger.debug(f"Exact length match found for {entity_type} (length: {target_length})")
        
        # Strategy 2: Closest length with unique replacements
        if not replacement:
            replacement = self._find_closest_length_unique_replacement(
                type_data, target_length, original_text, entity_type
            )
            if replacement:
                self.replacement_stats.closest_length_matches += 1
        
        # Cache the result if found and valid
        if replacement and replacement != original_text:
            self.replacement_cache[cache_key] = replacement
        
        return replacement

    def _is_entity_type_available(self, entity_type: str) -> bool:
        """Check if entity type has available data"""
        if entity_type not in self.organized_data:
            self.logger.warning(f"No data available for entity type: {entity_type}")
            return False
        
        if entity_type not in self.total_available_by_type or self.total_available_by_type[entity_type] == 0:
            self.logger.warning(f"Empty data for entity type: {entity_type}")
            return False
        
        return True

    def _get_unique_replacement_from_length(self, candidates: List[str], original_text: str, 
                                          entity_type: str, length: int) -> Optional[str]:
        """
        Get unique replacement from candidates list for specific length
        Improved with better filtering and fallback strategies
        """
        if not candidates:
            return None
        
        # Primary strategy: Different from original and unused
        available_replacements = [
            r for r in candidates 
            if (r.lower() != original_text.lower() and 
                r.lower() not in self.used_replacements)
        ]
        
        if available_replacements:
            replacement = random.choice(available_replacements)
            self.logger.debug(f"Found unique replacement from length {length}: '{replacement}'")
            return replacement
        
        # Fallback strategy: Allow same as original but must be unused
        fallback_replacements = [
            r for r in candidates 
            if r.lower() not in self.used_replacements
        ]
        
        if fallback_replacements:
            replacement = random.choice(fallback_replacements)
            self.replacement_stats.fallback_used += 1
            self.logger.debug(f"Using fallback replacement: '{replacement}' (length: {length})")
            return replacement
        
        self.logger.warning(f"No unique replacements available for length {length} in entity type {entity_type}")
        return None
    
    def generate_valid_tc_kimlik(self) -> str:
        """
        Geçerli bir TC Kimlik numarası üretir
        Resmi algoritma kullanarak matematiksel olarak doğru TC numarası oluşturur
        
        Returns:
            11 haneli geçerli TC kimlik numarası
        """
        import random
        
        # İlk 9 haneyi rastgele üret (ilk hane 0 olamaz)
        first_digit = random.randint(1, 9)
        digits = [first_digit]
        
        for _ in range(8):
            digits.append(random.randint(0, 9))
        
        # 10. haneyi hesapla
        sum_odd = sum(digits[i] for i in range(0, 9, 2))  # 1,3,5,7,9. haneler
        sum_even = sum(digits[i] for i in range(1, 8, 2))  # 2,4,6,8. haneler
        
        tenth_digit = (sum_odd * 7 - sum_even) % 10
        digits.append(tenth_digit)
        
        # 11. haneyi hesapla
        sum_first_ten = sum(digits)
        eleventh_digit = sum_first_ten % 10
        digits.append(eleventh_digit)
        
        tc_number = ''.join(map(str, digits))
        
        # Doğrulama kontrolü
        if self.validate_turkish_id(tc_number):
            return tc_number
        else:
            # Eğer bir hata varsa tekrar dene (nadiren gerekir)
            return self.generate_valid_tc_kimlik()

    # Ana replacement metodunda TC Kimlik için özel kontrol ekleyin:
    # _get_unique_custom_list_replacement metodunun başında şunu ekleyin:

    def _get_unique_custom_list_replacement(self, entity_type: str, original_text: str, target_length: int) -> Optional[str]:
            """
            Get unique replacement from custom lists only with improved caching
            Each replacement can only be used once
            """
            # Check cache first, but only if it's not already used
            if entity_type == 'tc_kimlik':
                return self._get_tc_kimlik_replacement(original_text)
            
            cache_key = f"{entity_type}_{original_text}_{target_length}"
            if cache_key in self.replacement_cache:
                cached_replacement = self.replacement_cache[cache_key]
                if cached_replacement.lower() not in self.used_replacements:
                    return cached_replacement
                else:
                    # Remove from cache since it's already used
                    del self.replacement_cache[cache_key]
            
            # Validate entity type availability
            if not self._is_entity_type_available(entity_type):
                return None
            
            type_data = self.organized_data[entity_type]
            replacement = None
            
            # Strategy 1: Exact length match with unique replacements
            if target_length in type_data and type_data[target_length]:
                replacement = self._get_unique_replacement_from_length(
                    type_data[target_length], original_text, entity_type, target_length
                )
                if replacement:
                    self.replacement_stats.exact_length_matches += 1
                    self.logger.debug(f"Exact length match found for {entity_type} (length: {target_length})")
            
            # Strategy 2: Closest length with unique replacements
            if not replacement:
                replacement = self._find_closest_length_unique_replacement(
                    type_data, target_length, original_text, entity_type
                )
                if replacement:
                    self.replacement_stats.closest_length_matches += 1
            
            # Cache the result if found and valid
            if replacement and replacement != original_text:
                self.replacement_cache[cache_key] = replacement
            
            return replacement

    def _get_tc_kimlik_replacement(self, original_tc: str) -> str:
        """
        TC Kimlik için özel replacement üretir
        Önce organized_data'dan arar, bulamazsa yeni üretir
        
        Args:
            original_tc: Orijinal TC kimlik numarası
            
        Returns:
            Replacement TC kimlik numarası
        """
        # Önce mevcut listeden dene
        if 'tc_kimlik' in self.organized_data:
            tc_data = self.organized_data['tc_kimlik']
            if 11 in tc_data and tc_data[11]:  # TC her zaman 11 haneli
                # Kullanılmamış TC'leri bul
                available_tcs = [
                    tc for tc in tc_data[11] 
                    if (tc.lower() not in self.used_replacements and 
                        tc != original_tc)
                ]
                
                if available_tcs:
                    replacement = random.choice(available_tcs)
                    self.logger.info(f"TC Kimlik listeden değiştirildi: {original_tc} -> {replacement}")
                    return replacement
        
        # Liste boşsa veya yoksa yeni üret
        new_tc = self.generate_valid_tc_kimlik()
        
        # Orijinalle aynı olmadığından ve kullanılmadığından emin ol
        max_attempts = 10
        attempts = 0
        
        while (new_tc == original_tc or new_tc.lower() in self.used_replacements) and attempts < max_attempts:
            new_tc = self.generate_valid_tc_kimlik()
            attempts += 1
        
        self.logger.info(f"Yeni TC Kimlik üretildi: {original_tc} -> {new_tc}")
        return new_tc

    def _find_closest_length_unique_replacement(self, type_data: Dict, target_length: int, 
                                              original_text: str, entity_type: str) -> Optional[str]:
        """
        Find unique replacement with closest available length
        Enhanced with better length selection strategy
        """
        available_lengths = [length for length, samples in type_data.items() if samples]
        if not available_lengths:
            self.logger.error(f"No available lengths for entity type: {entity_type}")
            return None
        
        # Sort lengths by distance from target, prefer longer over shorter for readability
        def length_preference(x):
            distance = abs(x - target_length)
            # Slight preference for longer replacements (more natural looking)
            length_bonus = 0.1 if x >= target_length else 0
            return distance - length_bonus
        
        closest_lengths = sorted(available_lengths, key=length_preference)
        
        self.logger.debug(f"Target length: {target_length}, Available lengths: {available_lengths[:10]}")
        
        # Try each length starting from closest
        for length in closest_lengths:
            if length in type_data and type_data[length]:
                replacement = self._get_unique_replacement_from_length(
                    type_data[length], original_text, entity_type, length
                )
                
                if replacement:
                    self.logger.debug(f"Closest length replacement: '{original_text}' (target: {target_length}) -> '{replacement}' (actual: {length})")
                    return replacement
        
        self.logger.error(f"No unique replacement found for {entity_type} with target length {target_length}")
        return None

    def apply_censoring_strategy(self, entities: List[Dict]) -> List[Dict]:
        """
        Apply censoring strategy - replace with asterisks
        Enhanced with better structure preservation
        """
        if not entities:
            return []
            
        processed_entities = []
        
        for entity in entities:
            try:
                original_text = entity.get('word', '')
                if not original_text:
                    entity['replacement'] = ''
                    processed_entities.append(entity)
                    continue
                
                # Create asterisk replacement matching length and structure
                censored = self._create_asterisk_replacement(original_text)
                
                entity['replacement'] = censored
                processed_entities.append(entity)
                
                self.logger.debug(f"Censored '{original_text}' -> '{censored}'")
                
            except Exception as e:
                self.logger.error(f"Error censoring entity {entity}: {e}")
                original_text = entity.get('word', '')
                entity['replacement'] = '*' * len(original_text) if original_text else ''
                processed_entities.append(entity)
        
        return processed_entities

    def _create_asterisk_replacement(self, original_text: str) -> str:
        """
        Create asterisk replacement preserving word structure
        Enhanced to handle various character types
        """
        if not original_text:
            return ''
            
        result = []
        
        for char in original_text:
            if char.isalnum():  # Letters and numbers become asterisks
                result.append('*')
            elif char.isspace():  # Preserve spaces
                result.append(' ')
            elif char in '.,;:!?-_':  # Preserve common punctuation
                result.append(char)
            else:  # Other special characters become asterisks
                result.append('*')
        
        return ''.join(result)

    def merge_and_clean_entities(self, entities: List[Dict], confidence_threshold: float = 0.5) -> List[Dict]:
        """
        Merge and clean entities, removing overlaps
        Enhanced with better overlap detection and validation
        """
        if not entities:
            return []
        
        # Validate confidence threshold
        if not (0.0 <= confidence_threshold <= 1.0):
            self.logger.warning(f"Invalid confidence threshold: {confidence_threshold}, using 0.5")
            confidence_threshold = 0.5
        
        # Filter by confidence and validate required fields
        filtered_entities = []
        for entity in entities:
            score = entity.get('score', 0)
            start = entity.get('start')
            end = entity.get('end')
            
            if score >= confidence_threshold and start is not None and end is not None:
                if start < end:  # Valid span
                    filtered_entities.append(entity)
                else:
                    self.logger.warning(f"Invalid entity span: start={start}, end={end}")
        
        if not filtered_entities:
            self.logger.info("No entities passed filtering criteria")
            return []
        
        # Sort by start position, then by score (descending) for stable sorting
        sorted_entities = sorted(filtered_entities, key=lambda x: (x['start'], -x['score']))
        
        # Remove overlapping entities (keep higher confidence)
        cleaned_entities = []
        
        for entity in sorted_entities:
            is_overlapping = False
            
            for i, existing in enumerate(cleaned_entities):
                # Check for overlap
                if self._entities_overlap(entity, existing):
                    if entity['score'] > existing['score']:
                        # Replace existing with new (higher confidence)
                        cleaned_entities[i] = entity
                        self.logger.debug(f"Replaced overlapping entity with higher confidence: {existing['score']:.3f} -> {entity['score']:.3f}")
                    
                    is_overlapping = True
                    break
            
            if not is_overlapping:
                cleaned_entities.append(entity)
        
        # Sort final result by start position
        cleaned_entities.sort(key=lambda x: x['start'])
        
        self.logger.info(f"Entity cleaning: {len(entities)} -> {len(filtered_entities)} (after filtering) -> {len(cleaned_entities)} (after deduplication)")
        return cleaned_entities

    def _entities_overlap(self, entity1: Dict, entity2: Dict) -> bool:
        """Check if two entities overlap"""
        return (entity1['start'] < entity2['end'] and entity1['end'] > entity2['start'])

    def validate_turkish_id(self, tc_no: str) -> bool:
        """
        Validate Turkish ID number using official algorithm
        Enhanced with better input validation
        """
        if not tc_no:
            return False
            
        # Clean input (remove spaces, dashes, etc.)
        tc_clean = re.sub(r'[^\d]', '', str(tc_no))
        
        if len(tc_clean) != 11 or not tc_clean.isdigit():
            return False
        
        try:
            digits = [int(d) for d in tc_clean]
        except ValueError:
            return False
        
        # First digit cannot be 0
        if digits[0] == 0:
            return False
        
        # Check sum algorithm
        sum_odd = sum(digits[i] for i in range(0, 9, 2))  # 1st, 3rd, 5th, 7th, 9th digits
        sum_even = sum(digits[i] for i in range(1, 8, 2))  # 2nd, 4th, 6th, 8th digits
        
        # 10th digit check
        tenth_digit = (sum_odd * 7 - sum_even) % 10
        if tenth_digit != digits[9]:
            return False
        
        # 11th digit check
        sum_first_ten = sum(digits[:10])
        if sum_first_ten % 10 != digits[10]:
            return False
        
        return True

    def _log_replacement_statistics(self) -> None:
        """Log detailed replacement statistics"""
        stats = self.replacement_stats
        total = stats.total_processed
        
        if total == 0:
            return
        
        self.logger.info(f"Replacement Statistics:")
        self.logger.info(f"  Total processed: {total}")
        self.logger.info(f"  Successful replacements: {stats.successful_replacements} ({stats.successful_replacements/total*100:.1f}%)")
        self.logger.info(f"  Exact length matches: {stats.exact_length_matches} ({stats.exact_length_matches/total*100:.1f}%)")
        self.logger.info(f"  Closest length matches: {stats.closest_length_matches} ({stats.closest_length_matches/total*100:.1f}%)")
        self.logger.info(f"  Fallback used: {stats.fallback_used} ({stats.fallback_used/total*100:.1f}%)")
        self.logger.info(f"  No replacement found: {stats.no_replacement_found} ({stats.no_replacement_found/total*100:.1f}%)")
        
        self.logger.info(f"Global unique replacements used: {len(self.used_replacements)}")
        for entity_type, used_set in self.used_replacements_by_type.items():
            self.logger.info(f"  {entity_type}: {len(used_set)} unique replacements")

    def get_replacement_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about replacements"""
        stats = {
            'processing_stats': {
                'total_processed': self.replacement_stats.total_processed,
                'successful_replacements': self.replacement_stats.successful_replacements,
                'exact_length_matches': self.replacement_stats.exact_length_matches,
                'closest_length_matches': self.replacement_stats.closest_length_matches,
                'fallback_used': self.replacement_stats.fallback_used,
                'no_replacement_found': self.replacement_stats.no_replacement_found
            },
            'cache_stats': {
                'total_cached_replacements': len(self.replacement_cache),
                'cache_hit_ratio': 0.0  # Could be implemented with additional tracking
            },
            'usage_stats': {
                'total_used_replacements': len(self.used_replacements),
                'entity_type_counts': dict(self.used_replacements_by_type),
                'entity_type_used_counts': {k: len(v) for k, v in self.used_replacements_by_type.items()}
            },
            'availability_stats': {
                'total_available_by_type': dict(self.total_available_by_type),
                'available_counts_by_length': dict(self.available_counts)
            }
        }
        
        return stats

    def clear_cache_and_usage(self) -> None:
        """Clear replacement cache and usage tracking"""
        self.replacement_cache.clear()
        self.used_replacements.clear()
        self.used_replacements_by_type.clear()
        self.replacement_stats = ReplacementStats()
        self.logger.info("Replacement cache, usage tracking, and statistics cleared")

    def get_available_replacements_count(self, entity_type: str, length: int) -> int:
        """Get count of available (unused) replacements for given entity type and length"""
        if entity_type not in self.organized_data:
            return 0
        
        type_data = self.organized_data[entity_type]
        if length not in type_data or not type_data[length]:
            return 0
        
        # Count available (unused) replacements
        available_count = len([
            r for r in type_data[length]
            if r.lower() not in self.used_replacements
        ])
        
        return available_count

    def get_usage_report(self) -> Dict[str, Any]:
        """Get detailed usage report showing available vs used replacements"""
        report = {
            'summary': {
                'total_used_globally': len(self.used_replacements),
                'total_entity_types': len(self.organized_data),
                'processing_stats': {
                    'total_processed': self.replacement_stats.total_processed,
                    'success_rate': (self.replacement_stats.successful_replacements / max(1, self.replacement_stats.total_processed)) * 100
                }
            },
            'entity_type_details': {}
        }
        
        for entity_type, length_data in self.organized_data.items():
            type_report = {
                'total_available': sum(len(samples) for samples in length_data.values()),
                'total_used': len(self.used_replacements_by_type.get(entity_type, set())),
                'available_by_length': {},
                'used_by_length': {}
            }
            
            for length, samples in length_data.items():
                if not samples:
                    continue
                    
                # Calculate available (unused) for this length
                available = [r for r in samples if r.lower() not in self.used_replacements]
                type_report['available_by_length'][str(length)] = len(available)
                
                # Calculate used for this length
                used = [r for r in samples if r.lower() in self.used_replacements]
                type_report['used_by_length'][str(length)] = len(used)
            
            # Calculate usage percentage
            total_available = type_report['total_available']
            total_used = type_report['total_used']
            type_report['usage_percentage'] = (total_used / max(1, total_available)) * 100
            
            # Add availability status
            if total_used / max(1, total_available) > 0.8:
                type_report['status'] = 'HIGH_USAGE'
            elif total_used / max(1, total_available) > 0.5:
                type_report['status'] = 'MEDIUM_USAGE'
            else:
                type_report['status'] = 'LOW_USAGE'
            
            report['entity_type_details'][entity_type] = type_report
        
        return report

    def validate_entity_data_integrity(self) -> Dict[str, Any]:
        """
        Validate the integrity of organized data
        Enhanced with more comprehensive checks
        """
        integrity_report = {
            'summary': {
                'total_entity_types': len(self.organized_data),
                'total_samples': sum(self.total_available_by_type.values()),
                'validation_passed': True
            },
            'entity_type_details': {},
            'issues': [],
            'recommendations': [],
            'warnings': []
        }
        
        for entity_type, length_data in self.organized_data.items():
            type_info = {
                'total_lengths': len(length_data),
                'total_samples': sum(len(samples) for samples in length_data.values()),
                'length_distribution': {str(length): len(samples) for length, samples in length_data.items()},
                'sample_stats': {}
            }
            
            # Calculate sample statistics
            sample_counts = [len(samples) for samples in length_data.values() if samples]
            if sample_counts:
                type_info['sample_stats'] = {
                    'min_samples_per_length': min(sample_counts),
                    'max_samples_per_length': max(sample_counts),
                    'avg_samples_per_length': sum(sample_counts) / len(sample_counts)
                }
            
            integrity_report['entity_type_details'][entity_type] = type_info
            
            # Issue detection
            if not length_data:
                issue = f"{entity_type}: No length data available"
                integrity_report['issues'].append(issue)
                integrity_report['summary']['validation_passed'] = False
                continue
            
            # Check for empty lengths
            empty_lengths = [length for length, samples in length_data.items() if not samples]
            if empty_lengths:
                integrity_report['warnings'].append(f"{entity_type}: Empty data for lengths {empty_lengths}")
            
            # Check for lengths with very few samples (uniqueness risk)
            low_sample_lengths = [length for length, samples in length_data.items() if 0 < len(samples) < 3]
            if low_sample_lengths:
                integrity_report['issues'].append(f"{entity_type}: Low sample count (<3) for lengths {low_sample_lengths}")
                integrity_report['recommendations'].append(f"Add more samples for {entity_type} lengths {low_sample_lengths}")
                
            # Check for duplicate samples within entity type
            all_samples = []
            for samples in length_data.values():
                all_samples.extend([s.lower() for s in samples])
            
            unique_samples = set(all_samples)
            if len(all_samples) != len(unique_samples):
                duplicate_count = len(all_samples) - len(unique_samples)
                integrity_report['warnings'].append(f"{entity_type}: {duplicate_count} duplicate samples found")
                
            # Check sample quality (basic validation)
            invalid_samples = []
            for length, samples in length_data.items():
                for sample in samples:
                    if not sample or not sample.strip():
                        invalid_samples.append(f"length {length}: empty sample")
                    elif len(sample) != length:
                        invalid_samples.append(f"length {length}: '{sample}' has wrong length ({len(sample)})")
            
            if invalid_samples:
                integrity_report['issues'].extend([f"{entity_type}: {issue}" for issue in invalid_samples[:5]])  # Limit to first 5
                if len(invalid_samples) > 5:
                    integrity_report['issues'].append(f"{entity_type}: ... and {len(invalid_samples) - 5} more invalid samples")
                integrity_report['summary']['validation_passed'] = False
        
        # Global recommendations
        if integrity_report['issues']:
            integrity_report['recommendations'].append("Review and fix data quality issues before production use")
        
        return integrity_report
    
    def verify_consistency(self, entities: List[Dict]) -> Dict[str, Any]:
        """
        Aynı orijinal metnin aynı değişikliği alıp almadığını kontrol eder
        
        Args:
            entities: 'word' ve 'replacement' alanları olan işlenmiş varlık listesi
            
        Returns:
            Tutarlılık doğrulama sonuçlarını içeren sözlük
        """
        consistency_check = {
            'is_consistent': True,
            'violations': [],
            'total_violations': 0,
            'consistent_mappings': {},
            'mapping_stats': {}
        }
        
        # Orijinal -> değişiklik eşlemelerini takip et
        mappings = {}
        violations = []
        
        for entity in entities:
            original = entity.get('word', '')
            replacement = entity.get('replacement', '')
            
            if not original:
                continue
                
            original_lower = original.lower()
            
            # Bu orijinal metni daha önce gördük mü kontrol et
            if original_lower in mappings:
                # Aynı değişikliği aldığını doğrula
                previous_replacement = mappings[original_lower]['replacement']
                if replacement.lower() != previous_replacement.lower():
                    violation = {
                        'original': original,
                        'expected_replacement': previous_replacement,
                        'actual_replacement': replacement,
                        'entity_type': entity.get('entity', 'bilinmiyor')
                    }
                    violations.append(violation)
                    consistency_check['is_consistent'] = False
                    
                    self.logger.warning(
                        f"Tutarlılık ihlali: '{original}' hem "
                        f"'{previous_replacement}' hem de '{replacement}' ile eşleştirildi"
                    )
            else:
                # Bu orijinal metni ilk kez görüyoruz, eşlemeyi kaydet
                mappings[original_lower] = {
                    'original': original,
                    'replacement': replacement,
                    'entity_type': entity.get('entity', 'bilinmiyor'),
                    'first_seen_index': len(mappings)
                }
        
        consistency_check['violations'] = violations
        consistency_check['total_violations'] = len(violations)
        consistency_check['consistent_mappings'] = mappings
        
        # Eşleme istatistikleri oluştur
        mapping_stats = {
            'total_unique_originals': len(mappings),
            'total_violations': len(violations),
            'consistency_rate': ((len(mappings) - len(violations)) / max(1, len(mappings))) * 100
        }
        
        # Eşlemeleri varlık türüne göre gruplandır
        mappings_by_type = {}
        for mapping_info in mappings.values():
            entity_type = mapping_info['entity_type']
            if entity_type not in mappings_by_type:
                mappings_by_type[entity_type] = []
            mappings_by_type[entity_type].append(mapping_info)
        
        mapping_stats['mappings_by_type'] = {
            entity_type: len(type_mappings) 
            for entity_type, type_mappings in mappings_by_type.items()
        }
        
        consistency_check['mapping_stats'] = mapping_stats
        
        # Tutarlılık sonuçlarını logla
        if consistency_check['is_consistent']:
            self.logger.info(
                f"Tutarlılık kontrolü başarılı: {len(mappings)} benzersiz eşleme, "
                f"ihlal yok"
            )
        else:
            self.logger.error(
                f"Tutarlılık kontrolü başarısız: {len(violations)} ihlal bulundu "
                f"({len(mappings)} benzersiz eşleme içinden)"
            )
            
            # Hata ayıklama için ilk birkaç ihlali logla
            for violation in violations[:3]:
                self.logger.error(
                    f"  İhlal: '{violation['original']}' -> "
                    f"'{violation['expected_replacement']}' ile "
                    f"'{violation['actual_replacement']}' karışıklığı"
                )
        
        return consistency_check

    def optimize_data_distribution(self) -> Dict[str, Any]:
        """Analyze and suggest optimizations for data distribution"""
        optimization_report = {
            'current_distribution': {},
            'recommendations': [],
            'optimization_opportunities': []
        }
        
        for entity_type, length_data in self.organized_data.items():
            type_analysis = {
                'length_coverage': list(length_data.keys()),
                'sample_distribution': {},
                'coverage_gaps': [],
                'optimization_potential': 'LOW'
            }
            
            # Analyze sample distribution
            for length, samples in length_data.items():
                type_analysis['sample_distribution'][str(length)] = len(samples)
            
            # Find coverage gaps
            if length_data:
                min_length = min(length_data.keys())
                max_length = max(length_data.keys())
                
                for length in range(min_length, max_length + 1):
                    if length not in length_data or not length_data[length]:
                        type_analysis['coverage_gaps'].append(length)
            
            # Determine optimization potential
            sample_counts = [len(samples) for samples in length_data.values() if samples]
            if sample_counts:
                min_samples = min(sample_counts)
                max_samples = max(sample_counts)
                variance = max_samples - min_samples
                
                if variance > 10:
                    type_analysis['optimization_potential'] = 'HIGH'
                    optimization_report['recommendations'].append(
                        f"{entity_type}: Balance sample distribution (range: {min_samples}-{max_samples})"
                    )
                elif variance > 5:
                    type_analysis['optimization_potential'] = 'MEDIUM'
            
            # Check for critical gaps
            if type_analysis['coverage_gaps']:
                optimization_report['recommendations'].append(
                    f"{entity_type}: Fill coverage gaps for lengths {type_analysis['coverage_gaps'][:5]}"
                )
            
            optimization_report['current_distribution'][entity_type] = type_analysis
        
        return optimization_report
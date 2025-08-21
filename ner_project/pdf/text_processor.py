"""
Text Processing Module for Manual Text Input
Handles AI-based entity detection and anonymization for manually entered text
Enhanced with unique replacement system
"""
import logging
import re
from typing import List, Dict, Tuple, Optional
import torch
from transformers import pipeline


class TextProcessor:
    def __init__(self, ner_pipeline, validators, organized_data):
        """
        Initialize TextProcessor with required dependencies
        
        Args:
            ner_pipeline: Loaded NER model pipeline
            validators: PDFValidators instance with unique replacement system
            organized_data: Organized replacement data
        """
        self.logger = logging.getLogger(__name__)
        self.ner_pipeline = ner_pipeline
        self.validators = validators
        self.organized_data = organized_data

    def process_manual_text(self, text: str, confidence_threshold: float, 
                          processing_mode: str) -> Dict:
        """
        Process manually entered text with AI model and unique replacement system
        
        Args:
            text: Input text to process
            confidence_threshold: Confidence threshold for entity detection
            processing_mode: 'replace' or 'censor'
            
        Returns:
            Dict containing processed text and statistics
        """
        try:
            if not text.strip():
                return {
                    'success': False,
                    'message': '❌ Lütfen işlenecek metni girin.',
                    'original_text': text,
                    'processed_text': '',
                    'entities_found': [],
                    'statistics': {},
                    'replacement_usage': {}
                }

            self.logger.info(f"Processing text with {processing_mode} mode")

            # Extract entities from text
            entities = self.extract_entities_from_text(text, confidence_threshold)

            if not entities:
                return {
                    'success': True,
                    'message': '⚠️ Metinde kişisel bilgi tespit edilmedi.',
                    'original_text': text,
                    'processed_text': text,
                    'entities_found': [],
                    'statistics': self._generate_statistics([]),
                    'replacement_usage': {}
                }

            # Apply processing based on mode
            if processing_mode == 'replace':
                # Use unique replacement system
                processed_entities = self.validators.apply_replacement_strategy_consistent(entities)
                
                # VERIFY CONSISTENCY
                consistency_check = self.validators.verify_consistency(processed_entities)
                if not consistency_check['is_consistent']:
                    self.logger.error(f"CONSISTENCY VIOLATION DETECTED: {consistency_check['violations']}")
                
                processed_text = self._apply_replacements_to_text(text, processed_entities)
                
                # Count successful replacements (excluding ones that stayed the same)
                successful_replacements = sum(1 for e in processed_entities 
                                            if e.get('replacement') != e.get('word'))
                
                # Get replacement usage statistics
                replacement_stats = self.validators.get_replacement_statistics()
                usage_report = self.validators.get_usage_report()
                
                success_message = f"✅ Metin başarıyla işlendi! {successful_replacements}/{len(processed_entities)} benzersiz ve tutarlı değişiklik yapıldı."
                
                # Add consistency info
                if consistency_check['is_consistent']:
                    success_message += " Tutarlılık sağlandı."
                else:
                    success_message += f" ⚠️ {consistency_check['total_violations']} tutarlılık ihlali tespit edildi!"
                
                if successful_replacements < len(processed_entities):
                    remaining = len(processed_entities) - successful_replacements
                    success_message += f" {remaining} öğe için benzersiz replacement bulunamadı."

            else:  # censor
                processed_entities = self.validators.apply_censoring_strategy(entities)
                processed_text = self._apply_censoring_to_text(text, processed_entities)
                success_message = f"✅ Metin başarıyla sansürlendi! {len(processed_entities)} kişisel bilgi sansürlendi."
                replacement_stats = {}
                usage_report = {}

            return {
                'success': True,
                'message': success_message,
                'original_text': text,
                'processed_text': processed_text,
                'entities_found': processed_entities,
                'statistics': self._generate_statistics(processed_entities),
                'replacement_usage': {
                    'replacement_stats': replacement_stats,
                    'usage_report': usage_report
                }
            }

        except Exception as e:
            self.logger.error(f"Text processing error: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Metin işleme hatası: {str(e)}",
                'original_text': text,
                'processed_text': '',
                'entities_found': [],
                'statistics': {},
                'replacement_usage': {}
            }

    def process_batch_texts(self, texts: List[str], confidence_threshold: float, 
                           processing_mode: str, reset_consistency: bool = True) -> Dict:
        """
        Process multiple texts maintaining unique replacements across all texts
        
        Args:
            texts: List of input texts to process
            confidence_threshold: Confidence threshold for entity detection
            processing_mode: 'replace' or 'censor'
            reset_consistency: Whether to reset consistent mappings (False to maintain consistency across batches)
            
        Returns:
            Dict containing all processed texts and global statistics
        """
        try:
            if not texts:
                return {
                    'success': False,
                    'message': '❌ İşlenecek metin listesi boş.',
                    'results': []
                }

            # Optionally clear usage tracking for new batch (but keep consistency)
            if reset_consistency:
                self.validators.clear_cache_and_usage()
            else:
                # Only clear usage, keep consistent mappings
                self.validators.used_replacements.clear()
                self.validators.used_replacements_by_type.clear()
                self.validators.replacement_cache.clear()
            
            results = []
            all_entities = []
            
            for i, text in enumerate(texts):
                self.logger.info(f"Processing text {i+1}/{len(texts)}")
                
                # Extract entities
                entities = self.extract_entities_from_text(text, confidence_threshold)
                all_entities.extend(entities)
                
                if processing_mode == 'replace':
                    # Apply unique replacements (will maintain uniqueness and consistency across all texts)
                    processed_entities = self.validators.apply_replacement_strategy_consistent(entities)
                    processed_text = self._apply_replacements_to_text(text, processed_entities)
                else:  # censor
                    processed_entities = self.validators.apply_censoring_strategy(entities)
                    processed_text = self._apply_censoring_to_text(text, processed_entities)
                
                results.append({
                    'original_text': text,
                    'processed_text': processed_text,
                    'entities_found': processed_entities,
                    'statistics': self._generate_statistics(processed_entities)
                })

            # Generate global statistics
            global_stats = self._generate_statistics(all_entities)
            replacement_stats = self.validators.get_replacement_statistics()
            usage_report = self.validators.get_usage_report()
            consistency_report = self.validators.get_consistency_report()

            successful_texts = len([r for r in results if r['entities_found']])
            total_entities = sum(len(r['entities_found']) for r in results)
            
            if processing_mode == 'replace':
                total_successful_replacements = sum(
                    len([e for e in r['entities_found'] if e.get('replacement') != e.get('word')])
                    for r in results
                )
                message = f"✅ {len(texts)} metin işlendi! {total_successful_replacements}/{total_entities} benzersiz ve tutarlı değişiklik yapıldı."
                
                # Add consistency info
                if consistency_report['total_consistent_mappings'] > 0:
                    message += f" {consistency_report['total_consistent_mappings']} tutarlı eşleme kullanıldı."
            else:
                message = f"✅ {len(texts)} metin sansürlendi! {total_entities} kişisel bilgi sansürlendi."

            return {
                'success': True,
                'message': message,
                'results': results,
                'global_statistics': global_stats,
                'replacement_usage': {
                    'replacement_stats': replacement_stats,
                    'usage_report': usage_report,
                    'consistency_report': consistency_report
                }
            }

        except Exception as e:
            self.logger.error(f"Batch text processing error: {e}", exc_info=True)
            return {
                'success': False,
                'message': f"❌ Toplu metin işleme hatası: {str(e)}",
                'results': []
            }

    def extract_entities_from_text(self, text: str, confidence_threshold: float) -> List[Dict]:
        """
        Extract entities from text using NER model and regex
        
        Args:
            text: Input text
            confidence_threshold: Minimum confidence for entity detection
            
        Returns:
            List of detected entities
        """
        try:
            entities = []

            # Process text in chunks if too long
            max_length = 512
            if len(text) <= max_length:
                chunks = [{'text': text, 'start_offset': 0}]
            else:
                chunks = self._split_text_into_chunks(text, max_length)

            # Run NER on each chunk
            for chunk in chunks:
                try:
                    results = self.ner_pipeline(chunk['text'])
                    
                    for result in results:
                        if result['score'] >= confidence_threshold:
                            entity = {
                                'entity': self._map_model_label_to_type(result['entity_group']),
                                'word': result['word'],
                                'start': chunk['start_offset'] + result['start'],
                                'end': chunk['start_offset'] + result['end'],
                                'score': result['score'],
                                'method': 'custom_ner'
                            }
                            entities.append(entity)

                except Exception as e:
                    self.logger.warning(f"Chunk processing error: {e}")
                    continue

            # Add TC Kimlik detection with regex
            tc_entities = self._detect_tc_kimlik(text)
            entities.extend(tc_entities)

            # Clean and merge overlapping entities
            cleaned_entities = self._clean_overlapping_entities(entities)
            
            self.logger.info(f"Detected {len(cleaned_entities)} entities in text")
            return cleaned_entities

        except Exception as e:
            self.logger.error(f"Entity extraction error: {e}")
            return []

    def _split_text_into_chunks(self, text: str, max_length: int) -> List[Dict]:
        """Split text into chunks for processing"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + max_length, len(text))
            
            # Try to break at word boundary
            if end < len(text):
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunks.append({
                'text': text[start:end],
                'start_offset': start
            })
            start = end
            
        return chunks

    def _detect_tc_kimlik(self, text: str) -> List[Dict]:
        """Detect Turkish ID numbers with regex validation"""
        tc_entities = []
        tc_pattern = r'\b[1-9][0-9]{9}[02468]\b'
        
        for match in re.finditer(tc_pattern, text):
            tc_no = match.group()
            if self.validators.validate_turkish_id(tc_no):
                tc_entities.append({
                    'entity': 'tc_kimlik',
                    'word': tc_no,
                    'start': match.start(),
                    'end': match.end(),
                    'score': 0.95,
                    'method': 'regex_validated'
                })
        
        return tc_entities

    def _map_model_label_to_type(self, model_label: str) -> str:
        """Map model labels to application types"""
        label_mapping = {
            'PERSON': 'ad_soyad',
            'PER': 'ad_soyad',
            'B-PERSON': 'ad_soyad',
            'I-PERSON': 'ad_soyad',
            'PHONE': 'telefon',
            'PHONE_NUMBER': 'telefon',
            'EMAIL': 'email',
            'ADDRESS': 'adres',
            'ORGANIZATION': 'sirket',
            'ORG': 'sirket',
            'MONEY': 'para',
            'DATE': 'tarih',
            'ID_NUMBER': 'tc_kimlik',
            'NATIONAL_ID': 'tc_kimlik'
        }
        return label_mapping.get(model_label.upper(), model_label.lower())

    def _clean_overlapping_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove overlapping entities, keeping the one with higher confidence"""
        if not entities:
            return entities

        # Sort by start position
        sorted_entities = sorted(entities, key=lambda x: x['start'])
        cleaned = []

        for entity in sorted_entities:
            # Check for overlap with already added entities
            overlapping = False
            for existing in cleaned:
                if (entity['start'] < existing['end'] and entity['end'] > existing['start']):
                    # There's an overlap - keep the one with higher score
                    if entity['score'] > existing['score']:
                        cleaned.remove(existing)
                        break
                    else:
                        overlapping = True
                        break

            if not overlapping:
                cleaned.append(entity)

        return cleaned

    def _apply_replacements_to_text(self, text: str, entities: List[Dict]) -> str:
        """Apply replacements to text"""
        # Sort entities by start position in reverse order to avoid position shifts
        sorted_entities = sorted(entities, key=lambda x: x['start'], reverse=True)
        
        processed_text = text
        for entity in sorted_entities:
            if 'replacement' in entity and entity['replacement']:
                processed_text = (
                    processed_text[:entity['start']] + 
                    entity['replacement'] + 
                    processed_text[entity['end']:]
                )
        
        return processed_text

    def _apply_censoring_to_text(self, text: str, entities: List[Dict]) -> str:
        """Apply censoring to text"""
        # Sort entities by start position in reverse order to avoid position shifts
        sorted_entities = sorted(entities, key=lambda x: x['start'], reverse=True)
        
        processed_text = text
        for entity in sorted_entities:
            if 'replacement' in entity and entity['replacement']:
                processed_text = (
                    processed_text[:entity['start']] + 
                    entity['replacement'] + 
                    processed_text[entity['end']:]
                )
        
        return processed_text

    def _generate_statistics(self, entities: List[Dict]) -> Dict:
        """Generate statistics about detected entities"""
        if not entities:
            return {
                'total_entities': 0,
                'entity_types': {},
                'confidence_stats': {},
                'replacement_success_rate': 0.0
            }

        # Count by entity type
        entity_types = {}
        confidence_scores = []
        successful_replacements = 0

        for entity in entities:
            entity_type = entity['entity']
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            confidence_scores.append(entity['score'])
            
            # Check if replacement was successful (different from original)
            if entity.get('replacement') and entity['replacement'] != entity['word']:
                successful_replacements += 1

        # Calculate confidence statistics
        if confidence_scores:
            confidence_stats = {
                'min_confidence': min(confidence_scores),
                'max_confidence': max(confidence_scores),
                'avg_confidence': sum(confidence_scores) / len(confidence_scores)
            }
        else:
            confidence_stats = {}

        # Calculate replacement success rate
        replacement_success_rate = (successful_replacements / len(entities)) * 100 if entities else 0

        return {
            'total_entities': len(entities),
            'entity_types': entity_types,
            'confidence_stats': confidence_stats,
            'successful_replacements': successful_replacements,
            'replacement_success_rate': replacement_success_rate
        }

    def format_entities_for_display(self, entities: List[Dict], show_uniqueness_info: bool = True) -> str:
        """Format entities for display in the interface with uniqueness information"""
        if not entities:
            return "Tespit edilen kişisel bilgi bulunmamaktadır."

        formatted_lines = []
        formatted_lines.append("### 🔍 Tespit Edilen Kişisel Bilgiler:\n")

        # Group by entity type
        grouped = {}
        for entity in entities:
            entity_type = entity['entity']
            if entity_type not in grouped:
                grouped[entity_type] = []
            grouped[entity_type].append(entity)

        # Turkish names for entity types
        type_names = {
            'ad_soyad': '👤 Ad Soyad',
            'telefon': '📞 Telefon',
            'email': '📧 E-mail',
            'adres': '🏠 Adres',
            'sirket': '🏢 Şirket',
            'iban': '💳 IBAN',
            'tarih': '📅 Tarih',
            'para': '💰 Para',
            'tc_kimlik': '🆔 TC Kimlik'
        }

        for entity_type, type_entities in grouped.items():
            type_name = type_names.get(entity_type, entity_type.title())
            formatted_lines.append(f"**{type_name}** ({len(type_entities)} adet):")
            
            for entity in type_entities:
                original = entity['word']
                replacement = entity.get('replacement', 'N/A')
                confidence = entity['score']
                
                # Check if replacement actually changed
                if replacement != original and replacement != 'N/A':
                    status_icon = "✅"
                    change_info = f"`{original}` → `{replacement}`"
                    if show_uniqueness_info:
                        change_info += " (benzersiz)"
                else:
                    status_icon = "⚠️"
                    change_info = f"`{original}` (değiştirilmedi - benzersiz replacement bulunamadı)"
                
                formatted_lines.append(f"  {status_icon} {change_info} (Güven: {confidence:.2f})")
            
            formatted_lines.append("")

        # Add uniqueness summary if requested
        if show_uniqueness_info:
            replacement_stats = self.validators.get_replacement_statistics()
            if replacement_stats.get('total_used_replacements', 0) > 0:
                formatted_lines.append("### 📊 Benzersizlik Özeti:")
                formatted_lines.append(f"- Toplam kullanılan benzersiz replacement: {replacement_stats['total_used_replacements']}")
                
                for entity_type, count in replacement_stats.get('entity_type_used_counts', {}).items():
                    type_name = type_names.get(entity_type, entity_type.title())
                    formatted_lines.append(f"- {type_name}: {count} benzersiz replacement")
                
                formatted_lines.append("")

        return "\n".join(formatted_lines)

    def get_replacement_availability_report(self) -> str:
        """Get a report about replacement availability for each entity type"""
        usage_report = self.validators.get_usage_report()
        
        if not usage_report or not usage_report.get('entity_type_details'):
            return "Henüz replacement kullanımı bulunmamaktadır."

        formatted_lines = []
        formatted_lines.append("### 📈 Replacement Kullanım Raporu:\n")

        type_names = {
            'ad_soyad': '👤 Ad Soyad',
            'telefon': '📞 Telefon',
            'email': '📧 E-mail',
            'adres': '🏠 Adres',
            'sirket': '🏢 Şirket',
            'iban': '💳 IBAN',
            'tarih': '📅 Tarih',
            'para': '💰 Para',
            'tc_kimlik': '🆔 TC Kimlik'
        }

        for entity_type, details in usage_report['entity_type_details'].items():
            type_name = type_names.get(entity_type, entity_type.title())
            formatted_lines.append(f"**{type_name}:**")
            formatted_lines.append(f"  - Toplam mevcut: {details['total_available']}")
            formatted_lines.append(f"  - Kullanılan: {details['total_used']}")
            formatted_lines.append(f"  - Kalan: {details['total_available'] - details['total_used']}")
            formatted_lines.append(f"  - Kullanım oranı: {details['usage_percentage']:.1f}%")
            formatted_lines.append("")

        return "\n".join(formatted_lines)

    def get_consistency_report(self) -> str:
        """Get a detailed consistency report showing same original -> same replacement mappings"""
        consistency_report = self.validators.get_consistency_report()
        
        if not consistency_report or consistency_report['total_consistent_mappings'] == 0:
            return "Henüz tutarlı eşleme bulunmamaktadır."

        formatted_lines = []
        formatted_lines.append("### 🔄 Tutarlılık Raporu:\n")
        formatted_lines.append(f"**Toplam tutarlı eşleme:** {consistency_report['total_consistent_mappings']}\n")

        # Group by length for better readability
        for length, mappings in consistency_report['mappings_by_length'].items():
            formatted_lines.append(f"**{length} karakter uzunluğu ({len(mappings)} eşleme):**")
            
            for mapping in mappings:
                length_indicator = "✅" if mapping['length_match'] else "⚠️"
                formatted_lines.append(f"  {length_indicator} `{mapping['original']}` → `{mapping['replacement']}`")
            
            formatted_lines.append("")

        return "\n".join(formatted_lines)
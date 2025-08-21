"""
Enhanced PDF Anonymization App - Refactored Main Module with Text Processing
"""
import gradio as gr
import os
import shutil
from datetime import datetime
import logging
from typing import List, Dict, Tuple, Optional
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
import re

# Import refactored modules
from pdf.extractor import PDFExtractor
from pdf.redact import PDFRedactor
from pdf.replace import PDFReplacer
from pdf.validators import PDFValidators
from pdf.text_processor import TextProcessor  # New import

# Import custom data lists
from samplelists import (
    iban_samples, email_samples, adres_len_samples, ad_soyad_len_samples,
    sirket_len_samples, tarih_samples, telefon_samples, adres_samples,
    para_samples, ad_soyad_samples, sirket_samples
)


class EnhancedAnonymizationApp:
    def __init__(self):
        # Logger setup
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Model path
        self.model_path = r"your_model_path"

        # Initialize components
        self.extractor = PDFExtractor()
        self.redactor = PDFRedactor()
        self.replacer = PDFReplacer()
        
        # Organize custom data and initialize validators
        self.organized_data = self._organize_data_by_length()
        self.validators = PDFValidators(self.organized_data)

        # Load NER model
        self.ner_pipeline = self.load_custom_ner_model()

        # Initialize text processor
        self.text_processor = TextProcessor(self.ner_pipeline, self.validators, self.organized_data)

        # Create directories
        for dir_name in ["uploads", "outputs"]:
            os.makedirs(dir_name, exist_ok=True)

    def _organize_data_by_length(self):
        """Organize data lists by character length"""
        organized = {
            'ad_soyad': {},
            'telefon': {},
            'email': {},
            'adres': {},
            'sirket': {},
            'iban': {},
            'tarih': {},
            'para': {}
        }

        # Helper function to organize samples by length
        def add_to_organized(data_type, samples):
            for item in samples:
                length = len(item)
                if length not in organized[data_type]:
                    organized[data_type][length] = []
                organized[data_type][length].append(item)

        # Organize all data types
        add_to_organized('ad_soyad', ad_soyad_samples)
        add_to_organized('telefon', telefon_samples)
        add_to_organized('email', email_samples)
        add_to_organized('adres', adres_samples)
        add_to_organized('sirket', sirket_samples)
        add_to_organized('iban', iban_samples)
        add_to_organized('tarih', tarih_samples)
        add_to_organized('para', para_samples)

        # Add length-specific samples
        for length_data in ad_soyad_len_samples:
            length = length_data['length']
            if length not in organized['ad_soyad']:
                organized['ad_soyad'][length] = []
            organized['ad_soyad'][length].extend(length_data['samples'])

        for length_data in adres_len_samples:
            length = length_data['length']
            if length not in organized['adres']:
                organized['adres'][length] = []
            organized['adres'][length].extend(length_data['samples'])

        for length_data in sirket_len_samples:
            length = length_data['length']
            if length not in organized['sirket']:
                organized['sirket'][length] = []
            organized['sirket'][length].extend(length_data['samples'])

        return organized

    def load_custom_ner_model(self):
        """Load custom NER model"""
        try:
            if not os.path.exists(self.model_path):
                self.logger.error(f"Model not found: {self.model_path}")
                return None

            self.logger.info(f"Loading model: {self.model_path}")

            tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            model = AutoModelForTokenClassification.from_pretrained(self.model_path)

            ner_pipeline = pipeline(
                "ner",
                model=model,
                tokenizer=tokenizer,
                aggregation_strategy="simple",
                device=0 if torch.cuda.is_available() else -1
            )

            self.logger.info("Model loaded successfully!")
            return ner_pipeline

        except Exception as e:
            self.logger.error(f"Model loading error: {e}")
            return None

    def extract_entities_with_custom_model(self, full_text: str, text_blocks: List[Dict], 
                                         confidence_threshold: float, progress) -> List[Dict]:
        """Extract entities using custom NER model + regex for TC kimlik"""
        try:
            # Split text into chunks
            max_length = 512
            text_chunks = []
            chunk_start = 0

            while chunk_start < len(full_text):
                chunk_end = min(chunk_start + max_length, len(full_text))

                if chunk_end < len(full_text):
                    last_space = full_text.rfind(' ', chunk_start, chunk_end)
                    if last_space > chunk_start:
                        chunk_end = last_space

                chunk_text = full_text[chunk_start:chunk_end]
                text_chunks.append({
                    'text': chunk_text,
                    'start_offset': chunk_start,
                    'end_offset': chunk_end
                })
                chunk_start = chunk_end

            progress(0.25, desc=f"NER analysis ({len(text_chunks)} chunks)...")

            all_entities = []

            # Run NER on each chunk
            for i, chunk in enumerate(text_chunks):
                try:
                    results = self.ner_pipeline(chunk['text'])

                    for result in results:
                        if result['score'] >= confidence_threshold:
                            entity_start = chunk['start_offset'] + result['start']
                            entity_end = chunk['start_offset'] + result['end']

                            text_block_info = self.extractor.find_text_block_for_position(
                                entity_start, entity_end, text_blocks, full_text
                            )

                            entity_dict = {
                                'entity': self.map_model_label_to_type(result['entity_group']),
                                'word': result['word'],
                                'start': entity_start,
                                'end': entity_end,
                                'score': result['score'],
                                'method': 'custom_ner',
                                'text_block_info': text_block_info
                            }
                            all_entities.append(entity_dict)

                except Exception as e:
                    self.logger.warning(f"Chunk {i} processing error: {e}")
                    continue

            progress(0.3, desc="TC kimlik regex check...")

            # TC kimlik regex detection
            tc_entities = self.detect_tc_kimlik_with_blocks(full_text, text_blocks)

            # Merge and clean
            combined_entities = self.validators.merge_and_clean_entities(
                all_entities + tc_entities, confidence_threshold
            )

            self.logger.info(f"Total {len(combined_entities)} entities detected")
            return combined_entities

        except Exception as e:
            self.logger.error(f"Custom NER analysis error: {e}")
            return []

    def detect_tc_kimlik_with_blocks(self, full_text: str, text_blocks: List[Dict]) -> List[Dict]:
        """Detect TC kimlik with regex validation"""
        tc_entities = []
        tc_pattern = r'\b[1-9][0-9]{9}[02468]\b'
        
        for match in re.finditer(tc_pattern, full_text):
            tc_no = match.group()
            if self.validators.validate_turkish_id(tc_no):
                text_block_info = self.extractor.find_text_block_for_position(
                    match.start(), match.end(), text_blocks, full_text
                )

                tc_entities.append({
                    'entity': 'tc_kimlik',
                    'word': tc_no,
                    'start': match.start(),
                    'end': match.end(),
                    'score': 0.95,
                    'method': 'regex_validated',
                    'text_block_info': text_block_info
                })

        return tc_entities

    def map_model_label_to_type(self, model_label: str) -> str:
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

    def process_pdf_with_real_replacement(self, pdf_file, confidence_threshold: float, 
                                        progress=gr.Progress()) -> Tuple[Optional[str], str]:
        """Process PDF with real replacement using custom lists"""
        if pdf_file is None:
            return None, " Please upload a PDF file."

        if self.ner_pipeline is None:
            return None, " NER model could not be loaded. Check model path."

        # Clear cache for each new processing
        self.validators.replacement_cache.clear()

        try:
            progress(0.05, desc="Preparing file...")

            # File paths
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_in = os.path.basename(pdf_file.name if hasattr(pdf_file, "name") else str(pdf_file))
            input_filename = f"input_{timestamp}_{base_in}"
            output_filename = f"anonymized_{timestamp}_{base_in}"

            input_path = os.path.join("uploads", input_filename)
            output_path = os.path.join("outputs", output_filename)

            # Copy uploaded file
            shutil.copy2(pdf_file.name if hasattr(pdf_file, "name") else str(pdf_file), input_path)

            progress(0.1, desc="Analyzing PDF...")

            # Extract text and positions from PDF
            text_blocks = self.extractor.extract_text_with_positions(input_path)
            full_text = " ".join([block['text'] for block in text_blocks])

            if not full_text.strip():
                return None, " No text could be extracted from PDF."

            progress(0.2, desc="Running NER analysis...")

            # Custom NER model analysis
            entities_detected = self.extract_entities_with_custom_model(
                full_text, text_blocks, confidence_threshold, progress
            )

            if not entities_detected:
                return None, " No personal information detected in PDF."

            progress(0.4, desc="Applying replacement strategy...")

            # Apply consistent replacement
            processed_entities = self.validators.apply_replacement_strategy_consistent(entities_detected)

            progress(0.5, desc="Applying changes to PDF...")

            # Font-preserving PDF replacement
            success = self.replacer.process_pdf_replacement(
                input_path, processed_entities, output_path, self.extractor, progress
            )

            if not success:
                return None, " PDF replacement operation failed."

            progress(1.0, desc="Completed!")

            status_msg = f" Operation completed! {len(processed_entities)} replacements made."
            
            return output_path, status_msg

        except Exception as e:
            self.logger.error(f"PDF processing error: {e}", exc_info=True)
            return None, f" Critical error: {str(e)}"

    def process_pdf_with_censoring(self, pdf_file, confidence_threshold: float, 
                                 progress=gr.Progress()) -> Tuple[Optional[str], str]:
        """Process PDF with censoring (asterisk characters)"""
        if pdf_file is None:
            return None, " Please upload a PDF file."

        if self.ner_pipeline is None:
            return None, " NER model could not be loaded. Check model path."

        # Clear cache for each new processing
        self.validators.replacement_cache.clear()

        try:
            progress(0.05, desc="Preparing file...")

            # File paths
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            base_in = os.path.basename(pdf_file.name if hasattr(pdf_file, "name") else str(pdf_file))
            input_filename = f"input_{timestamp}_{base_in}"
            output_filename = f"censored_{timestamp}_{base_in}"

            input_path = os.path.join("uploads", input_filename)
            output_path = os.path.join("outputs", output_filename)

            # Copy uploaded file
            shutil.copy2(pdf_file.name if hasattr(pdf_file, "name") else str(pdf_file), input_path)

            progress(0.1, desc="Analyzing PDF...")

            # Extract text and positions from PDF
            text_blocks = self.extractor.extract_text_with_positions(input_path)
            full_text = " ".join([block['text'] for block in text_blocks])

            if not full_text.strip():
                return None, "⚠No text could be extracted from PDF."

            progress(0.2, desc="Running NER analysis...")

            # Custom NER model analysis
            entities_detected = self.extract_entities_with_custom_model(
                full_text, text_blocks, confidence_threshold, progress
            )

            if not entities_detected:
                return None, " No personal information detected in PDF."

            progress(0.4, desc="Applying censoring strategy...")

            # Apply censoring
            processed_entities = self.validators.apply_censoring_strategy(entities_detected)

            progress(0.5, desc="Applying censoring to PDF...")

            # Font-preserving PDF censoring
            success = self.replacer.process_pdf_censoring(
                input_path, processed_entities, output_path, self.extractor, progress
            )

            if not success:
                return None, " PDF censoring operation failed."

            progress(1.0, desc="Completed!")

            status_msg = f" Censoring completed! {len(processed_entities)} personal information censored."
            
            return output_path, status_msg

        except Exception as e:
            self.logger.error(f"PDF censoring error: {e}", exc_info=True)
            return None, f" Critical error: {str(e)}"

    # NEW METHODS FOR TEXT PROCESSING
    def process_manual_text_replacement(self, text: str, confidence_threshold: float) -> Tuple[str, str, str]:
        """Process manual text with replacement strategy"""
        if self.ner_pipeline is None:
            return "", " NER modeli yüklenemedi. Model yolunu kontrol edin.", ""
        
        # Clear cache for each processing
        self.validators.replacement_cache.clear()
        
        result = self.text_processor.process_manual_text(text, confidence_threshold, 'replace')
        
        processed_text = result['processed_text']
        status_message = result['message']
        entities_info = self.text_processor.format_entities_for_display(result['entities_found'])
        
        return processed_text, status_message, entities_info

    def process_manual_text_censoring(self, text: str, confidence_threshold: float) -> Tuple[str, str, str]:
        """Process manual text with censoring strategy"""
        if self.ner_pipeline is None:
            return "", " NER modeli yüklenemedi. Model yolunu kontrol edin.", ""
        
        # Clear cache for each processing
        self.validators.replacement_cache.clear()
        
        result = self.text_processor.process_manual_text(text, confidence_threshold, 'censor')
        
        processed_text = result['processed_text']
        status_message = result['message']
        entities_info = self.text_processor.format_entities_for_display(result['entities_found'])
        
        return processed_text, status_message, entities_info

    def create_enhanced_interface(self):
        """Three-tab Gradio interface - Replacement, Censoring, and Text Processing"""
        css = """
        .gradio-container { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .tab-nav { margin-bottom: 20px; }
        .text-input { min-height: 200px; }
        .text-output { min-height: 150px; }
        """

        try:
            theme = gr.themes.Soft()
        except Exception:
            theme = None

        with gr.Blocks(css=css, title="PDF Personal Information Anonymizer - Advanced", theme=theme) as interface:
            gr.Markdown("""
            #  PDF Personal Information Anonymizer — Advanced Version
            **Anonymize personal information in PDFs and text with AI-powered detection**
            """)

            with gr.Tabs():
                # TAB 1: Replacement (with Custom Lists)
                with gr.Tab(" PDF Replacement (Custom Lists)", elem_classes="tab-nav"):
                    gr.Markdown("""
                    ### PDF Replacement with Custom Lists
                    Personal information is replaced with similar realistic data while preserving length.
                    """)

                    with gr.Row():
                        with gr.Column(scale=1):
                            pdf_input_replace = gr.File(
                                label=" Upload PDF File",
                                file_types=[".pdf"],
                                type="filepath"
                            )

                            confidence_threshold_replace = gr.Slider(
                                minimum=0.1, maximum=1.0, value=0.7, step=0.1,
                                label=" Confidence Threshold"
                            )

                            process_btn_replace = gr.Button(
                                " Start Replacement Process",
                                variant="primary",
                                interactive=bool(self.ner_pipeline)
                            )

                            if not self.ner_pipeline:
                                gr.Markdown(" **Warning**: Process cannot start because model could not be loaded.")

                        with gr.Column(scale=1):
                            output_pdf_replace = gr.File(label="📤 Replaced PDF", file_count="single")
                            status_text_replace = gr.Markdown("")

                # TAB 2: Censoring (with asterisk characters)
                with gr.Tab(" PDF Censoring (Asterisk)", elem_classes="tab-nav"):
                    gr.Markdown("""
                    ### PDF Censoring with Asterisk (*) Characters
                    Personal information is detected and replaced with asterisks matching character count.
                    **Example:** "Ahmet Yılmaz" → "***** ******"
                    """)

                    with gr.Row():
                        with gr.Column(scale=1):
                            pdf_input_censor = gr.File(
                                label=" Upload PDF File",
                                file_types=[".pdf"],
                                type="filepath"
                            )

                            confidence_threshold_censor = gr.Slider(
                                minimum=0.1, maximum=1.0, value=0.7, step=0.1,
                                label=" Confidence Threshold"
                            )

                            process_btn_censor = gr.Button(
                                " Start Censoring Process",
                                variant="secondary",
                                interactive=bool(self.ner_pipeline)
                            )

                            if not self.ner_pipeline:
                                gr.Markdown(" **Warning**: Process cannot start because model could not be loaded.")

                        with gr.Column(scale=1):
                            output_pdf_censor = gr.File(label="📤 Censored PDF", file_count="single")
                            status_text_censor = gr.Markdown("")

                # TAB 3: Text Processing (NEW)
                with gr.Tab(" Text Processing", elem_classes="tab-nav"):
                    gr.Markdown("""
                    ### Manual Text Processing with AI
                    Enter text manually and choose between replacement or censoring strategies.
                    The AI model will detect and anonymize personal information in your text.
                    """)

                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("####  Input Text")
                            
                            manual_text_input = gr.Textbox(
                                label="Enter text to process",
                                placeholder="Paste or type your text here...\n\nExample:\nMerhaba, ben Ahmet Yılmaz. Telefon numaram 0555 123 45 67 ve email adresim ahmet@email.com",
                                lines=8,
                                elem_classes="text-input"
                            )

                            confidence_threshold_text = gr.Slider(
                                minimum=0.1, maximum=1.0, value=0.7, step=0.1,
                                label=" Confidence Threshold"
                            )

                            with gr.Row():
                                text_replace_btn = gr.Button(
                                    " Replace with Fake Data",
                                    variant="primary",
                                    interactive=bool(self.ner_pipeline),
                                    scale=1
                                )

                                text_censor_btn = gr.Button(
                                    " Censor with Asterisks",
                                    variant="secondary",
                                    interactive=bool(self.ner_pipeline),
                                    scale=1
                                )

                            if not self.ner_pipeline:
                                gr.Markdown(" **Warning**: Processing cannot start because model could not be loaded.")

                        with gr.Column(scale=1):
                            gr.Markdown("####  Processed Output")
                            
                            processed_text_output = gr.Textbox(
                                label="Processed Text",
                                lines=8,
                                elem_classes="text-output",
                                interactive=False
                            )

                            status_text_manual = gr.Markdown("")

                    # Entities information section
                    with gr.Row():
                        entities_info_display = gr.Markdown(
                            label="Detected Entities Information",
                            value="Process text to see detected entities..."
                        )

            # EVENT HANDLERS

            def _run_replacement(pdf, thr, progress=gr.Progress()):
                out_path, status = self.process_pdf_with_real_replacement(
                    pdf_file=pdf,
                    confidence_threshold=thr,
                    progress=progress
                )
                return out_path, (status or "")

            def _run_censoring(pdf, thr, progress=gr.Progress()):
                out_path, status = self.process_pdf_with_censoring(
                    pdf_file=pdf,
                    confidence_threshold=thr,
                    progress=progress
                )
                return out_path, (status or "")

            def _run_text_replacement(text, thr):
                processed, status, entities = self.process_manual_text_replacement(text, thr)
                return processed, status, entities

            def _run_text_censoring(text, thr):
                processed, status, entities = self.process_manual_text_censoring(text, thr)
                return processed, status, entities

            # PDF Event Handlers
            process_btn_replace.click(
                _run_replacement,
                inputs=[pdf_input_replace, confidence_threshold_replace],
                outputs=[output_pdf_replace, status_text_replace],
                api_name="process_pdf_replacement"
            )

            process_btn_censor.click(
                _run_censoring,
                inputs=[pdf_input_censor, confidence_threshold_censor],
                outputs=[output_pdf_censor, status_text_censor],
                api_name="process_pdf_censoring"
            )

            # Text Processing Event Handlers
            text_replace_btn.click(
                _run_text_replacement,
                inputs=[manual_text_input, confidence_threshold_text],
                outputs=[processed_text_output, status_text_manual, entities_info_display],
                api_name="process_text_replacement"
            )

            text_censor_btn.click(
                _run_text_censoring,
                inputs=[manual_text_input, confidence_threshold_text],
                outputs=[processed_text_output, status_text_manual, entities_info_display],
                api_name="process_text_censoring"
            )

        return interface


if __name__ == "__main__":
    app = EnhancedAnonymizationApp()
    demo = app.create_enhanced_interface()

    demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)

import importlib
import gmft
import gmft.table_detection
import gmft.table_visualization
import gmft.table_function
import gmft.table_function_algorithm
import gmft.table_captioning
import gmft.pdf_bindings.bindings_pdfium
import gmft.pdf_bindings
import gmft.common
import matplotlib.pyplot as plt
import os
import json
from gmft import AutoTableFormatter
from gmft.detectors.tatr import TATRDetector
from gmft.formatters.common import FormattedTable, TableFormatter
from gmft.table_visualization import display_html_and_image
from gmft.auto import AutoFormatConfig

from gmft.pdf_bindings import PyPDFium2Document
from gmft.auto import CroppedTable, AutoTableDetector
from PIL import Image

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'outputs')

importlib.reload(gmft)
importlib.reload(gmft.common)
importlib.reload(gmft.table_captioning)
importlib.reload(gmft.table_detection)
importlib.reload(gmft.table_visualization)
importlib.reload(gmft.table_function)
importlib.reload(gmft.table_function_algorithm)
importlib.reload(gmft.pdf_bindings.bindings_pdfium)
importlib.reload(gmft.pdf_bindings)


detector = AutoTableDetector()
config_hdr = AutoFormatConfig(enable_multi_header=True) # config may be passed like so
config_hdr.verbosity = 3
config_hdr.enable_multi_header = True
config_hdr.semantic_spanning_cells = True 
formatter = AutoTableFormatter(config_hdr)



import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PDFTableProcessor:
    def __init__(self, pdf_path):
        logger.info(f"Initializing PDFTableProcessor with file: {pdf_path}")
        
        # Validate PDF path
        if not pdf_path:
            logger.error("PDF path is empty or None")
            raise ValueError("PDF path cannot be empty")
            
        # Normalize path
        pdf_path = os.path.abspath(pdf_path)
        logger.debug(f"Normalized PDF path: {pdf_path}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            raise ValueError(f"PDF file not found: {pdf_path}")
            
        # Check if it's really a file
        if not os.path.isfile(pdf_path):
            logger.error(f"Path exists but is not a file: {pdf_path}")
            raise ValueError(f"Path exists but is not a file: {pdf_path}")
            
        # Check file size
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            logger.error(f"PDF file is empty: {pdf_path}")
            raise ValueError(f"PDF file is empty")
        logger.debug(f"PDF file size: {file_size} bytes")
            
        # Check read permissions
        if not os.access(pdf_path, os.R_OK):
            logger.error(f"No read permission for PDF file: {pdf_path}")
            raise ValueError(f"No read permission for PDF file")
        
        self.pdf_path = pdf_path
        self.config_hdr = config_hdr
        
        try:
            # Open and validate PDF file
            logger.info("Starting PDF ingestion...")
            with open(pdf_path, 'rb') as f:
                # Check if it's actually a PDF by reading the header
                header = f.read(4)
                if header != b'%PDF':
                    logger.error(f"File is not a valid PDF: {pdf_path}")
                    raise ValueError("File is not a valid PDF")
            
            # Process the PDF
            self.per_page_tables, self.doc = self.ingest_pdf(pdf_path)
            logger.info("PDF ingestion completed successfully")
            
            # total pages and total tables
            self.total_pages = len(self.per_page_tables)
            self.total_tables = sum(len(p) for p in self.per_page_tables)
            print(f"PDF analysis complete: {self.total_pages} pages, {self.total_tables} tables detected")
            
        except Exception as e:
            print(f"Error during PDF initialization: {str(e)}")
            raise

    def ingest_pdf(self, pdf_path):
        try:
            # Initialize PyPDFium2Document with additional error checks
            logger.debug(f"Creating PyPDFium2Document for {pdf_path}")
            
            try:
                doc = PyPDFium2Document(pdf_path)
                logger.debug("PyPDFium2Document instance created")
                
                if doc is None:
                    logger.error("PyPDFium2Document returned None")
                    raise ValueError("Failed to create PDF document object")
                    
                page_count = len(doc)
                logger.info(f"Successfully opened PDF with {page_count} pages")
                
                if page_count == 0:
                    logger.error("PDF document has no pages")
                    raise ValueError("PDF document has no pages")
                    
            except Exception as pdf_error:
                logger.error(f"Failed to open PDF: {str(pdf_error)}")
                raise ValueError(f"Failed to open PDF: {str(pdf_error)}")
            
            # Process pages and extract tables
            per_page = []
            for page_idx, page in enumerate(doc):
                try:
                    logger.debug(f"Processing page {page_idx + 1}")
                    
                    # Verify page object
                    if page is None:
                        logger.error(f"Got None page object for page {page_idx + 1}")
                        continue
                        
                    # Extract tables with error handling
                    try:
                        page_tables = detector.extract(page)
                        if page_tables is None:
                            logger.warning(f"Table detector returned None for page {page_idx + 1}")
                            page_tables = []
                    except Exception as detect_error:
                        logger.error(f"Table detection failed for page {page_idx + 1}: {str(detect_error)}")
                        raise
                        
                    logger.info(f"Page {page_idx + 1}: Detected {len(page_tables)} tables")
                    per_page.append(page_tables)
                    
                except Exception as page_error:
                    logger.error(f"Error processing page {page_idx + 1}: {str(page_error)}")
                    logger.error("Stack trace:", exc_info=True)
                    raise
            
            return per_page, doc
            
        except Exception as e:
            logger.error(f"Error in ingest_pdf: {str(e)}")
            logger.error("Stack trace:", exc_info=True)
            raise

    def tablo_sayisi(self, input_path):
        per_page, doc = self.ingest_pdf(input_path)
        return sum(len(p) for p in per_page)

    def save_as_json(self,df, output_dir, table_index):
        """DataFrame'i JSON formatında kaydeder."""
        json_output = df.to_json(orient='records', force_ascii=False)
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'output_{table_index}.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json.loads(json_output), f, ensure_ascii=False, indent=4)
        print(f"JSON dosyası {output_file} olarak kaydedildi.")
        return output_file

    def save_as_csv(self,df, output_dir, table_index):
        """DataFrame'i CSV formatında kaydeder."""
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'output_{table_index}.csv')
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"CSV dosyası {output_file} olarak kaydedildi.")
        return output_file

    def process_single_table(self, page_index, table_index_in_page, output_format='json'):
        """
        Process a single table identified by its page and index within the page.
        """
        try:
            print(f"Starting to process single table: page {page_index}, table {table_index_in_page}")
            
            # Get table object
            print("Accessing table object from per_page_tables...")
            table_obj = self.per_page_tables[page_index][table_index_in_page]
            print("Successfully got table object")
            
            # Extract table with formatter
            print("Extracting table with formatter...")
            ft = formatter.extract(table_obj, margin='auto', padding=None)
            print("Table extraction successful")
            
            # Visualize table
            print("Generating table visualization...")
            image = ft.visualize()
            print("Table visualization successful")
            
            # Save image
            output_dir = OUTPUT_DIR
            os.makedirs(output_dir, exist_ok=True)
            print(f"Output directory ensured: {output_dir}")
            
            image_output_path = os.path.join(output_dir, f'page_{page_index}_table_{table_index_in_page}.png')
            print(f"Saving image to: {image_output_path}")
            image.save(image_output_path)
            print("Image saved successfully")

            df = ft.df(config_overrides=config_hdr).fillna("")
            df.columns = [
                f"{col}_{i}" if df.columns.tolist().count(col) > 1 else col 
                for i, col in enumerate(df.columns)
            ]

            if output_format == 'json':
                json_file = self.save_as_json(df, output_dir, f'page_{page_index}_table_{table_index_in_page}')
                return json_file, image_output_path
            elif output_format == 'csv':
                csv_file = self.save_as_csv(df, output_dir, f'page_{page_index}_table_{table_index_in_page}')
                return csv_file, image_output_path
            elif output_format == 'both':
                json_file = self.save_as_json(df, output_dir, f'page_{page_index}_table_{table_index_in_page}')
                csv_file = self.save_as_csv(df, output_dir, f'page_{page_index}_table_{table_index_in_page}')
                return json_file, csv_file, image_output_path
            else:
                raise ValueError("Invalid output_format. Should be 'json', 'csv' or 'both'.")
        except Exception as e:
            print(f"Error processing table at page {page_index}, index {table_index_in_page}: {e}")
            raise

    def process_tables(self, output_format='json', pages_limit: int | None = None):
        """
        Iterate over tables page by page, honoring an optional pages_limit which limits how many pages to process.
        Yields the same tuple shapes as before depending on output_format.
        """
        try:
            print(f"Starting to process tables with format: {output_format}, pages_limit: {pages_limit}")
            max_pages = self.total_pages if pages_limit is None else min(self.total_pages, pages_limit)
            print(f"Will process up to {max_pages} pages")
            
            for page_idx in range(max_pages):
                print(f"Processing page {page_idx + 1}/{max_pages}")
                tables_on_page = self.per_page_tables[page_idx]
                print(f"Found {len(tables_on_page)} tables on page {page_idx + 1}")
                
                for tbl_idx in range(len(tables_on_page)):
                    print(f"Processing table {tbl_idx + 1}/{len(tables_on_page)} on page {page_idx + 1}")
                    try:
                        result = self.process_single_table(page_idx, tbl_idx, output_format)
                        print(f"Successfully processed table {tbl_idx + 1} on page {page_idx + 1}")
                        yield result
                    except Exception as table_error:
                        print(f"Error processing table {tbl_idx + 1} on page {page_idx + 1}: {str(table_error)}")
                        raise
                        
        except Exception as e:
            print(f"Error in process_tables: {str(e)}")
            raise


if __name__ == "__main__":
    pdf_path = input("Lütfen PDF dosyasının tam yolunu girin: ")


    processor = PDFTableProcessor(pdf_path)
    output_format = input("Lütfen formatı girin (json, csv, both): ")
    table_processor = processor.process_tables(output_format=output_format)

    for table_file, image_file in table_processor:
        print(f"İşlenen dosya: {table_file}")
        print(f"Görsel dosyası: {image_file}")

        input("Sonraki tabloyu işlemek için Enter'a basın...")

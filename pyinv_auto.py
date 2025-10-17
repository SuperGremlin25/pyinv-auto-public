#!/usr/bin/env python3
"""
PyInv-Auto: Python Invoice Automation Tool
A CLI tool for watching folders and parsing invoices into CSV format.
"""

import os
import sys
import time
import json
import csv
import argparse
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import PyPDF2
import re
from threading import Lock


class InvoiceParser:
    """Parse invoice data from PDF files."""
    
    def __init__(self):
        # Improved regex patterns for better accuracy
        self.invoice_patterns = {
            # Matches: Invoice #123, INV-2024-001, Invoice: 12345
            'invoice_number': r'Invoice\s*(?:#|No\.?|Number)?\s*:?\s*([A-Z0-9][-A-Z0-9/]*)',
            # Matches: 01/15/2024, 15-01-2024, 2024-01-15
            'date': r'(?:Invoice\s+)?Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            # Matches: $1,250.00, 1250.00, Total: $890.50
            'total': r'(?:Total|Amount\s+Due|Balance)\s*:?\s*\$?\s*([\d,]+\.\d{2})',
            # Matches vendor name until newline or specific delimiters
            'vendor': r'(?:From|Vendor|Bill\s+From)\s*:?\s*([A-Za-z0-9][A-Za-z0-9\s&.,\'\-]*?)(?=\n|\r|$|\s{2,})',
        }
        self.logger = logging.getLogger(__name__)
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from a PDF file."""
        try:
            # Check if file is accessible and not locked
            if not os.access(pdf_path, os.R_OK):
                self.logger.error(f"File not readable: {pdf_path}")
                return None
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Check if PDF is encrypted
                if pdf_reader.is_encrypted:
                    self.logger.warning(f"PDF is encrypted: {pdf_path}")
                    return None
                
                if len(pdf_reader.pages) == 0:
                    self.logger.warning(f"PDF has no pages: {pdf_path}")
                    return None
                
                text = ''
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
                
                return text.strip() if text else None
                
        except FileNotFoundError:
            self.logger.error(f"File not found: {pdf_path}")
            return None
        except PermissionError:
            self.logger.error(f"Permission denied: {pdf_path}")
            return None
        except PyPDF2.errors.PdfReadError as e:
            self.logger.error(f"PDF read error for {pdf_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error extracting text from {pdf_path}: {e}")
            return None
    
    def _clean_value(self, value, field_type):
        """Clean and validate extracted values."""
        if not value or value == 'N/A':
            return 'N/A'
        
        value = value.strip()
        
        if field_type == 'total':
            # Remove currency symbols and clean up number
            value = value.replace('$', '').replace(',', '').strip()
            # Validate it's a valid number
            try:
                float(value)
                return value
            except ValueError:
                return 'N/A'
        
        elif field_type == 'vendor':
            # Remove trailing punctuation and extra whitespace
            value = re.sub(r'\s+', ' ', value)  # Normalize whitespace
            value = value.rstrip('.,;:')
            # Limit length to reasonable vendor name
            if len(value) > 100:
                value = value[:100]
        
        elif field_type == 'invoice_number':
            # Remove extra whitespace
            value = re.sub(r'\s+', '', value)
        
        return value
    
    def parse_invoice(self, pdf_path):
        """Parse invoice data from a PDF file."""
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            self.logger.warning(f"No text extracted from {pdf_path}")
            return None
        
        # Validate minimum text length
        if len(text) < 50:
            self.logger.warning(f"Insufficient text content in {pdf_path} (only {len(text)} chars)")
            return None
        
        invoice_data = {
            'filename': os.path.basename(pdf_path),
            'filepath': pdf_path,
            'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Extract data using regex patterns
        for field, pattern in self.invoice_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                raw_value = match.group(1).strip()
                invoice_data[field] = self._clean_value(raw_value, field)
            else:
                invoice_data[field] = 'N/A'
                self.logger.debug(f"Field '{field}' not found in {pdf_path}")
        
        return invoice_data


class InvoiceWatcher(FileSystemEventHandler):
    """Watch for new invoice files and process them."""
    
    def __init__(self, watch_folder, output_csv, config):
        self.watch_folder = watch_folder
        self.output_csv = output_csv
        self.config = config
        self.parser = InvoiceParser()
        self.processed_files = set()
        self.csv_lock = Lock()  # Thread-safe CSV writing
        self.logger = logging.getLogger(__name__)
        
        # Load previously processed files if CSV exists
        if os.path.exists(output_csv):
            self._load_processed_files()
    
    def _load_processed_files(self):
        """Load list of previously processed files from CSV."""
        try:
            with open(self.output_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'filename' in row and row['filename']:
                        self.processed_files.add(row['filename'])
            self.logger.info(f"Loaded {len(self.processed_files)} previously processed files")
        except FileNotFoundError:
            self.logger.info("No existing CSV file found, starting fresh")
        except Exception as e:
            self.logger.error(f"Error loading processed files: {e}")
    
    def _write_to_csv(self, invoice_data):
        """Write invoice data to CSV file (thread-safe)."""
        with self.csv_lock:
            file_exists = os.path.exists(self.output_csv)
            
            try:
                # Ensure output directory exists
                output_dir = os.path.dirname(self.output_csv)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                
                with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                    fieldnames = ['filename', 'filepath', 'invoice_number', 'date', 
                                 'total', 'vendor', 'processed_date']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    
                    if not file_exists:
                        writer.writeheader()
                    
                    writer.writerow(invoice_data)
                
                print(f"✓ Saved to CSV: {invoice_data['filename']}")
                self.logger.info(f"Successfully wrote {invoice_data['filename']} to CSV")
                
            except PermissionError:
                error_msg = f"Permission denied writing to CSV: {self.output_csv}"
                print(f"✗ {error_msg}")
                self.logger.error(error_msg)
            except Exception as e:
                error_msg = f"Error writing to CSV: {e}"
                print(f"✗ {error_msg}")
                self.logger.error(error_msg)
    
    def _is_file_ready(self, file_path, max_wait=5):
        """Check if file is fully written and ready to process."""
        # Wait for file to be stable (no size changes)
        try:
            initial_size = os.path.getsize(file_path)
            time.sleep(0.5)
            
            for _ in range(max_wait * 2):  # Check every 0.5 seconds
                current_size = os.path.getsize(file_path)
                if current_size == initial_size and current_size > 0:
                    return True
                initial_size = current_size
                time.sleep(0.5)
            
            return False
        except (OSError, FileNotFoundError):
            return False
    
    def process_file(self, file_path):
        """Process a single invoice file."""
        filename = os.path.basename(file_path)
        
        # Check if already processed
        if filename in self.processed_files:
            self.logger.debug(f"Skipping already processed file: {filename}")
            return
        
        # Check file extension
        if not file_path.lower().endswith('.pdf'):
            return
        
        # Verify file exists and is ready
        if not os.path.exists(file_path):
            self.logger.warning(f"File no longer exists: {filename}")
            return
        
        # Check if file is ready (fully written)
        if not self._is_file_ready(file_path):
            self.logger.warning(f"File not ready or still being written: {filename}")
            return
        
        print(f"Processing: {filename}")
        self.logger.info(f"Processing file: {file_path}")
        
        invoice_data = self.parser.parse_invoice(file_path)
        
        if invoice_data:
            self._write_to_csv(invoice_data)
            self.processed_files.add(filename)
        else:
            print(f"✗ Failed to parse: {filename}")
            self.logger.error(f"Failed to parse invoice: {file_path}")
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            self.logger.debug(f"File created: {event.src_path}")
            # File readiness check is now in process_file
            self.process_file(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            self.logger.debug(f"File modified: {event.src_path}")
            # File readiness check is now in process_file
            self.process_file(event.src_path)


def load_config(config_path):
    """Load configuration from JSON file."""
    logger = logging.getLogger(__name__)
    
    # Get script directory for relative paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    default_config = {
        'watch_folder': os.path.join(script_dir, 'invoices'),
        'output_csv': os.path.join(script_dir, 'invoices_parsed.csv'),
        'file_extensions': ['.pdf'],
        'watch_mode': True,
        'log_level': 'INFO'  # New: configurable log level
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
            logger.info(f"Loaded configuration from {config_path}")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            print("Using default configuration")
            logger.error(f"Invalid JSON in config file {config_path}: {e}")
        except Exception as e:
            print(f"Error loading config file: {e}")
            print("Using default configuration")
            logger.error(f"Error loading config file {config_path}: {e}")
    else:
        logger.info(f"Config file not found: {config_path}, using defaults")
    
    return default_config


def process_existing_files(watch_folder, output_csv, config):
    """Process all existing files in the watch folder."""
    watcher = InvoiceWatcher(watch_folder, output_csv, config)
    
    if not os.path.exists(watch_folder):
        print(f"Creating watch folder: {watch_folder}")
        os.makedirs(watch_folder, exist_ok=True)
        return
    
    pdf_files = list(Path(watch_folder).glob('*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in {watch_folder}")
        return
    
    print(f"\nProcessing {len(pdf_files)} existing PDF files...")
    for pdf_file in pdf_files:
        watcher.process_file(str(pdf_file))
    
    print("\nExisting files processed.")


def watch_folder(watch_folder, output_csv, config):
    """Watch folder for new invoice files."""
    print(f"\nWatching folder: {watch_folder}")
    print(f"Output CSV: {output_csv}")
    print("Press Ctrl+C to stop watching...\n")
    
    event_handler = InvoiceWatcher(watch_folder, output_csv, config)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping watcher...")
    
    observer.join()


def setup_logging(log_level='INFO'):
    """Configure logging for the application."""
    # Create logs directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(script_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f'pyinv_auto_{datetime.now().strftime("%Y%m%d")}.log')
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout) if log_level.upper() == 'DEBUG' else logging.NullHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")
    return logger


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description='PyInv-Auto: Watch folders and parse invoices into CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch folder for new invoices (default mode)
  python pyinv_auto.py
  
  # Process existing files only
  python pyinv_auto.py --process-only
  
  # Use custom config file
  python pyinv_auto.py --config my_config.json
  
  # Specify watch folder and output file
  python pyinv_auto.py --watch-folder ./my_invoices --output ./output.csv
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '--watch-folder', '-w',
        help='Folder to watch for invoice files (overrides config)'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output CSV file path (overrides config)'
    )
    
    parser.add_argument(
        '--process-only', '-p',
        action='store_true',
        help='Process existing files only, do not watch for new files'
    )
    
    args = parser.parse_args()
    
    # Load configuration first (before logging setup)
    config = load_config(args.config)
    
    # Setup logging
    logger = setup_logging(config.get('log_level', 'INFO'))
    logger.info("PyInv-Auto started")
    logger.info(f"Python version: {sys.version}")
    
    # Override config with command-line arguments
    watch_folder = args.watch_folder or config['watch_folder']
    output_csv = args.output or config['output_csv']
    
    # Ensure watch folder exists
    if not os.path.exists(watch_folder):
        print(f"Creating watch folder: {watch_folder}")
        os.makedirs(watch_folder, exist_ok=True)
    
    print("=" * 60)
    print("PyInv-Auto: Invoice Automation Tool")
    print("=" * 60)
    
    logger.info(f"Watch folder: {watch_folder}")
    logger.info(f"Output CSV: {output_csv}")
    logger.info(f"Process-only mode: {args.process_only}")
    
    try:
        # Process existing files first
        process_existing_files(watch_folder, output_csv, config)
        
        # Watch for new files if not in process-only mode
        if not args.process_only and config.get('watch_mode', True):
            watch_folder(watch_folder, output_csv, config)
        else:
            print("\nDone. Exiting.")
            logger.info("Processing completed successfully")
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        logger.info("Application interrupted by user")
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        logger.exception(f"Fatal error in main: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

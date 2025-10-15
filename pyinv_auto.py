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
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import PyPDF2
import re


class InvoiceParser:
    """Parse invoice data from PDF files."""
    
    def __init__(self):
        self.invoice_patterns = {
            'invoice_number': r'Invoice\s*#?\s*:?\s*(\w+[-/]?\w+)',
            'date': r'Date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            'total': r'Total\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})',
            'vendor': r'(?:From|Vendor)\s*:?\s*([A-Za-z0-9\s&.,]+)',
        }
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return None
    
    def parse_invoice(self, pdf_path):
        """Parse invoice data from a PDF file."""
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return None
        
        invoice_data = {
            'filename': os.path.basename(pdf_path),
            'filepath': pdf_path,
            'processed_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Extract data using regex patterns
        for field, pattern in self.invoice_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_data[field] = match.group(1).strip()
            else:
                invoice_data[field] = 'N/A'
        
        return invoice_data


class InvoiceWatcher(FileSystemEventHandler):
    """Watch for new invoice files and process them."""
    
    def __init__(self, watch_folder, output_csv, config):
        self.watch_folder = watch_folder
        self.output_csv = output_csv
        self.config = config
        self.parser = InvoiceParser()
        self.processed_files = set()
        
        # Load previously processed files if CSV exists
        if os.path.exists(output_csv):
            self._load_processed_files()
    
    def _load_processed_files(self):
        """Load list of previously processed files from CSV."""
        try:
            with open(self.output_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'filename' in row:
                        self.processed_files.add(row['filename'])
        except Exception as e:
            print(f"Error loading processed files: {e}")
    
    def _write_to_csv(self, invoice_data):
        """Write invoice data to CSV file."""
        file_exists = os.path.exists(self.output_csv)
        
        try:
            with open(self.output_csv, 'a', newline='', encoding='utf-8') as f:
                fieldnames = ['filename', 'filepath', 'invoice_number', 'date', 
                             'total', 'vendor', 'processed_date']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(invoice_data)
            print(f"✓ Saved to CSV: {invoice_data['filename']}")
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def process_file(self, file_path):
        """Process a single invoice file."""
        filename = os.path.basename(file_path)
        
        # Check if already processed
        if filename in self.processed_files:
            print(f"Skipping already processed file: {filename}")
            return
        
        # Check file extension
        if not file_path.lower().endswith('.pdf'):
            return
        
        print(f"Processing: {filename}")
        invoice_data = self.parser.parse_invoice(file_path)
        
        if invoice_data:
            self._write_to_csv(invoice_data)
            self.processed_files.add(filename)
        else:
            print(f"Failed to parse: {filename}")
    
    def on_created(self, event):
        """Handle file creation events."""
        if not event.is_directory:
            # Wait a moment to ensure file is fully written
            time.sleep(1)
            self.process_file(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification events."""
        if not event.is_directory:
            # Wait a moment to ensure file is fully written
            time.sleep(1)
            self.process_file(event.src_path)


def load_config(config_path):
    """Load configuration from JSON file."""
    default_config = {
        'watch_folder': './invoices',
        'output_csv': './invoices_parsed.csv',
        'file_extensions': ['.pdf'],
        'watch_mode': True
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except Exception as e:
            print(f"Error loading config file: {e}")
            print("Using default configuration")
    
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
    
    # Load configuration
    config = load_config(args.config)
    
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
    
    # Process existing files first
    process_existing_files(watch_folder, output_csv, config)
    
    # Watch for new files if not in process-only mode
    if not args.process_only and config.get('watch_mode', True):
        watch_folder(watch_folder, output_csv, config)
    else:
        print("\nDone. Exiting.")


if __name__ == '__main__':
    main()

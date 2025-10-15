# PyInv-Auto: Invoice Automation Tool

A powerful Python-based CLI tool for automatically watching folders and parsing invoice PDFs into structured CSV format. Perfect for automating invoice processing workflows!

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Features

- **Automatic Folder Watching**: Monitors specified folders for new invoice PDFs
- **PDF Parsing**: Extracts key invoice data (invoice number, date, total, vendor)
- **CSV Export**: Outputs parsed data to structured CSV format
- **Duplicate Detection**: Automatically skips already-processed files
- **Windows Scheduler Integration**: Includes PowerShell script for automatic execution on login
- **Configurable**: JSON-based configuration for easy customization
- **CLI Interface**: Simple command-line interface with multiple operating modes

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Windows Scheduler Setup](#windows-scheduler-setup)
- [How It Works](#how-it-works)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Repository

```bash
# Clone the repository
git clone https://github.com/SuperGremlin25/pyinv-auto-public.git
cd pyinv-auto-public
```

Or download and extract the ZIP file from GitHub.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `watchdog` - For folder monitoring
- `PyPDF2` - For PDF text extraction

### Step 3: Verify Installation

```bash
python pyinv_auto.py --help
```

You should see the help message with available options.

## ⚡ Quick Start

### Basic Usage (Process Existing Files Only)

```bash
# Create the invoices folder
mkdir invoices

# Place some PDF invoices in the invoices folder
# Then run:
python pyinv_auto.py --process-only
```

This will process all PDF files in the `invoices` folder and create `invoices_parsed.csv`.

### Watch Mode (Monitor for New Files)

```bash
python pyinv_auto.py
```

The tool will:
1. Process all existing PDFs in the `invoices` folder
2. Continue watching for new files
3. Automatically process new PDFs as they appear
4. Press `Ctrl+C` to stop watching

## ⚙️ Configuration

### config.json

The tool uses a `config.json` file for default settings:

```json
{
    "watch_folder": "./invoices",
    "output_csv": "./invoices_parsed.csv",
    "file_extensions": [".pdf"],
    "watch_mode": true
}
```

**Configuration Options:**

- `watch_folder`: Directory to monitor for invoice PDFs
- `output_csv`: Path to the output CSV file
- `file_extensions`: List of file extensions to process (default: [".pdf"])
- `watch_mode`: Enable/disable continuous monitoring (true/false)

### Custom Configuration

Create your own config file:

```bash
python pyinv_auto.py --config my_custom_config.json
```

## 📖 Usage

### Command-Line Options

```
python pyinv_auto.py [OPTIONS]

Options:
  -h, --help            Show help message and exit
  -c, --config FILE     Path to configuration file (default: config.json)
  -w, --watch-folder DIR  Folder to watch for invoice files (overrides config)
  -o, --output FILE     Output CSV file path (overrides config)
  -p, --process-only    Process existing files only, do not watch for new files
```

### Usage Examples

#### Process Existing Files Only
```bash
python pyinv_auto.py --process-only
```

#### Watch Specific Folder
```bash
python pyinv_auto.py --watch-folder "C:\Documents\Invoices"
```

#### Custom Output Location
```bash
python pyinv_auto.py --output "C:\Reports\invoices_2024.csv"
```

#### Combine Multiple Options
```bash
python pyinv_auto.py --watch-folder "./my_invoices" --output "./reports/output.csv" --process-only
```

## 🪟 Windows Scheduler Setup

PyInv-Auto includes a PowerShell script to automatically run the tool when you log in to Windows.

### Automatic Setup (Recommended)

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Navigate to the PyInv-Auto Directory**
   ```powershell
   cd C:\path\to\pyinv-auto-public
   ```

3. **Run the Setup Script**
   ```powershell
   .\setup_scheduler.ps1
   ```

The script will:
- ✅ Verify Python installation
- ✅ Install required dependencies
- ✅ Create a scheduled task
- ✅ Configure it to run at login

### Manual Setup (Alternative)

If you prefer manual setup or the script doesn't work:

1. Open **Task Scheduler** (`Win + R`, type `taskschd.msc`)
2. Click **Create Basic Task**
3. Name: `PyInv-Auto-Invoice-Processor`
4. Trigger: **When I log on**
5. Action: **Start a program**
   - Program: `python.exe` (or full path like `C:\Python39\python.exe`)
   - Arguments: `"C:\path\to\pyinv_auto.py" --process-only`
   - Start in: `C:\path\to\pyinv-auto-public`
6. Click **Finish**

### Verify Scheduled Task

```powershell
# View the task
Get-ScheduledTask -TaskName "PyInv-Auto-Invoice-Processor"

# Test run the task manually
Start-ScheduledTask -TaskName "PyInv-Auto-Invoice-Processor"
```

### Custom Scheduler Options

To customize the scheduler script:

```powershell
# Specify custom paths
.\setup_scheduler.ps1 -ScriptPath "C:\MyPath\pyinv_auto.py" -PythonPath "C:\Python39\python.exe"

# View help
.\setup_scheduler.ps1 -Help
```

## 🔍 How It Works

### Invoice Parsing

The tool uses regular expressions to extract key data from invoice PDFs:

1. **Invoice Number**: Patterns like "Invoice #12345" or "Invoice: INV-2024-001"
2. **Date**: Common date formats (MM/DD/YYYY, DD-MM-YYYY, etc.)
3. **Total Amount**: Dollar amounts with optional currency symbols
4. **Vendor Name**: Extracted from "From:" or "Vendor:" fields

### Output Format

The CSV file includes the following columns:

| Column | Description |
|--------|-------------|
| `filename` | Original PDF filename |
| `filepath` | Full path to the PDF file |
| `invoice_number` | Extracted invoice/reference number |
| `date` | Invoice date |
| `total` | Total amount |
| `vendor` | Vendor/company name |
| `processed_date` | When the file was processed |

### Example CSV Output

```csv
filename,filepath,invoice_number,date,total,vendor,processed_date
invoice_001.pdf,./invoices/invoice_001.pdf,INV-2024-001,01/15/2024,1250.00,Acme Corp,2024-10-15 10:30:45
invoice_002.pdf,./invoices/invoice_002.pdf,INV-2024-002,01/16/2024,890.50,Tech Solutions Inc,2024-10-15 10:30:46
```

## 💡 Examples

### Example 1: Basic Setup

```bash
# 1. Create invoices folder
mkdir invoices

# 2. Copy your invoice PDFs to the invoices folder
cp /path/to/invoices/*.pdf invoices/

# 3. Run the tool
python pyinv_auto.py --process-only

# 4. View results
cat invoices_parsed.csv
```

### Example 2: Continuous Monitoring

```bash
# Start watching for new invoices
python pyinv_auto.py

# In another terminal/window, add new PDFs:
cp new_invoice.pdf invoices/

# The tool will automatically detect and process the new file
```

### Example 3: Custom Folder Structure

```bash
# Create custom config
cat > custom_config.json << EOF
{
    "watch_folder": "./company_invoices",
    "output_csv": "./reports/processed_invoices.csv",
    "watch_mode": true
}
EOF

# Create folders
mkdir -p company_invoices reports

# Run with custom config
python pyinv_auto.py --config custom_config.json
```

## 🔧 Troubleshooting

### Problem: "Python not found"

**Solution**: Make sure Python is installed and added to your PATH.

```bash
# Check Python installation
python --version

# If not found, download from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
```

### Problem: "Module not found" errors

**Solution**: Install dependencies.

```bash
pip install -r requirements.txt

# Or install individually:
pip install watchdog PyPDF2
```

### Problem: No data extracted from PDFs

**Possible causes:**
1. PDF is scanned image (not text-based) - Consider using OCR tools
2. Invoice format doesn't match regex patterns - Check the PDF content
3. PDF is encrypted or password-protected

**Solution**: 
- Ensure PDFs contain extractable text (not just images)
- Check if text can be selected/copied in a PDF viewer
- For scanned invoices, use OCR preprocessing (e.g., Tesseract)

### Problem: Scheduled task not running

**Solutions:**
1. Check Task Scheduler (`taskschd.msc`) for error messages
2. Verify Python path is correct in the task
3. Ensure the working directory is set correctly
4. Check Windows Event Viewer for error details

```powershell
# View task history
Get-ScheduledTask -TaskName "PyInv-Auto-Invoice-Processor" | Get-ScheduledTaskInfo
```

### Problem: Permission denied errors on Windows

**Solution**: Run PowerShell as Administrator when setting up the scheduled task.

```powershell
# Set execution policy if needed
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## 🤝 Contributing

Contributions are welcome! This is a public repository. Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions

- Support for additional invoice formats
- OCR integration for scanned documents
- Email integration (auto-download attachments)
- Web dashboard for viewing parsed data
- Export to other formats (JSON, Excel, database)
- Machine learning for better data extraction
- Support for other document types (receipts, bills, etc.)

## 📄 License

This project is open source and available for personal and commercial use.

## 👤 Author

**SuperGremlin25**

- GitHub: [@SuperGremlin25](https://github.com/SuperGremlin25)

## 🙏 Acknowledgments

- Built with [watchdog](https://github.com/gorakhargosh/watchdog) for file system monitoring
- Uses [PyPDF2](https://github.com/py-pdf/pypdf2) for PDF parsing
- Inspired by the need to automate tedious invoice processing tasks

---

**Need help?** Open an issue on GitHub or check the [Troubleshooting](#troubleshooting) section.

**Enjoy automating your invoice processing!** 🚀

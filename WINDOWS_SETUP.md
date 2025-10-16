# 🪟 Windows Setup Guide - PyInv-Auto

Quick guide for Windows users to get started with PyInv-Auto.

---

## 📦 Quick Installation

### Step 1: Install Python

1. Download Python from https://www.python.org/downloads/
2. **Important**: Check "Add Python to PATH" during installation
3. Restart your terminal after installation

### Step 2: Clone or Download

```bash
git clone https://github.com/SuperGremlin25/pyinv-auto-public.git
cd pyinv-auto-public
```

Or download ZIP from GitHub and extract it.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start Options

### Option 1: Double-Click to Run (Easiest)

**For continuous watching**:
- Double-click `start-pyinv-auto.bat`
- A window will open and start processing
- Leave it running to watch for new invoices
- Press Ctrl+C to stop

**For one-time processing**:
- Double-click `process-existing-only.bat`
- Processes all PDFs in the `invoices` folder
- Closes automatically when done

**For silent background mode**:
- Double-click `start-hidden.vbs`
- Runs completely hidden (no window)
- Check Task Manager to see it running
- End the `python.exe` process to stop it

### Option 2: Command Line

```bash
# Process existing files only
python pyinv_auto.py --process-only

# Watch for new files (continuous)
python pyinv_auto.py

# Custom folder
python pyinv_auto.py --watch-folder "C:\MyInvoices" --output "C:\Results\output.csv"
```

### Option 3: Auto-Start at Login (Recommended)

1. Double-click `setup-scheduler-admin.bat`
2. Click "Yes" when prompted for admin access
3. Follow the prompts
4. PyInv-Auto will start automatically when you log in

---

## 📁 Folder Structure

After installation, your folder will look like this:

```
pyinv-auto-public/
├── pyinv_auto.py              # Main script
├── config.json                # Configuration
├── requirements.txt           # Dependencies
│
├── start-pyinv-auto.bat       # Double-click to start
├── process-existing-only.bat  # One-time processing
├── start-hidden.vbs           # Silent mode
├── setup-scheduler-admin.bat  # Auto-start setup
├── setup_scheduler.ps1        # PowerShell setup script
│
├── invoices/                  # Put your PDFs here (auto-created)
└── invoices_parsed.csv        # Output file (auto-created)
```

---

## 🎯 How to Use

### Basic Workflow

1. **Place PDF invoices** in the `invoices` folder
2. **Run one of the scripts** (see Quick Start above)
3. **Check results** in `invoices_parsed.csv`

### What Gets Extracted

The tool extracts:
- Invoice number
- Date
- Total amount
- Vendor name

### Example Output

```csv
filename,filepath,invoice_number,date,total,vendor,processed_date
invoice_001.pdf,C:\...\invoices\invoice_001.pdf,INV-2024-001,01/15/2024,1250.00,Acme Corp,2024-10-16 05:45:00
```

---

## ⚙️ Configuration

### Using Default Settings

By default, the tool:
- Watches the `invoices` folder (in the same directory as the script)
- Outputs to `invoices_parsed.csv`
- Processes `.pdf` files only

**No configuration needed!** Just put PDFs in the `invoices` folder.

### Custom Configuration

Edit `config.json` to customize:

```json
{
    "watch_folder": "./invoices",
    "output_csv": "./invoices_parsed.csv",
    "file_extensions": [".pdf"],
    "watch_mode": true
}
```

Or use command-line options:

```bash
python pyinv_auto.py --watch-folder "C:\MyFolder" --output "C:\Results\output.csv"
```

---

## 🔧 Troubleshooting

### "Python is not recognized"

**Solution**: 
1. Install Python from python.org
2. During installation, check "Add Python to PATH"
3. Restart your terminal
4. Test: `python --version`

### "No module named 'watchdog'" or "No module named 'PyPDF2'"

**Solution**:
```bash
pip install -r requirements.txt
```

### Script doesn't find invoices folder

**Solution**: The script now automatically uses its own directory. Make sure:
1. The `invoices` folder is in the same directory as `pyinv_auto.py`
2. Or use `--watch-folder` to specify a different location

### Scheduled task not running

**Solutions**:
1. Open Task Scheduler (`Win + R`, type `taskschd.msc`)
2. Find "PyInv-Auto-Invoice-Processor"
3. Right-click → Properties
4. Check "Run whether user is logged on or not" is NOT checked
5. Verify the path to python.exe is correct

### No data extracted from PDFs

**Possible causes**:
1. PDF is a scanned image (not text-based)
2. Invoice format doesn't match expected patterns
3. PDF is encrypted

**Solution**: 
- Ensure PDFs contain selectable text
- For scanned invoices, consider using OCR preprocessing

---

## 📝 Tips

1. **Test first**: Use `process-existing-only.bat` to test with a few invoices before setting up auto-start
2. **Check the CSV**: Open `invoices_parsed.csv` in Excel to verify data
3. **Organize invoices**: Create subfolders by month/year if needed
4. **Backup data**: The CSV file is appended to, so back it up regularly

---

## 🎓 Advanced Usage

### Run from any directory

The scripts now work from any location! You can:
- Create shortcuts on your desktop
- Run from different folders
- Use in scheduled tasks

All paths are automatically relative to the script location.

### Silent background mode

Use `start-hidden.vbs` for completely silent operation:
- No console window
- Runs in background
- Check Task Manager to verify it's running
- Stop by ending the `python.exe` process

### Custom Python path

If you have multiple Python versions:

```bash
C:\Python39\python.exe pyinv_auto.py
```

Or edit the `.bat` files to use a specific Python path.

---

## ❓ Need Help?

- **GitHub Issues**: https://github.com/SuperGremlin25/pyinv-auto-public/issues
- **README**: See main README.md for detailed documentation
- **Examples**: See EXAMPLES.md for more usage examples

---

**Happy automating!** 🚀

# Example Configuration Files

This directory contains example configuration files you can use as templates.

## config_custom.json

Example of a custom configuration:

```json
{
    "watch_folder": "C:\\Documents\\Invoices",
    "output_csv": "C:\\Documents\\Reports\\invoices.csv",
    "file_extensions": [".pdf"],
    "watch_mode": true
}
```

## Tips

1. Use absolute paths on Windows (e.g., `C:\\Documents\\...`)
2. Use forward slashes or double backslashes for Windows paths
3. The `watch_folder` will be created automatically if it doesn't exist
4. The CSV file will be created automatically if it doesn't exist

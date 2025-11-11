# Security Policy

## Supported Versions

We actively maintain the latest version of PyInv-Auto. Security updates are provided for:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Security Measures

PyInv-Auto implements several security measures to protect your data:

### 1. Path Traversal Protection
- All file paths are validated to ensure they remain within the designated watch folder
- Symbolic links are resolved and validated before processing
- Prevents malicious files from accessing data outside the watch folder

### 2. Input Validation
- File extensions are strictly validated (only `.pdf` files are processed)
- File paths are sanitized using `os.path.abspath()` and `os.path.realpath()`
- Configuration files are parsed using safe JSON methods

### 3. No Code Execution
- No use of `eval()`, `exec()`, or similar dynamic code execution
- No system command execution or subprocess calls
- All operations use safe Python standard library functions

### 4. Dependency Security
- Dependencies are kept to a minimum (only `watchdog` and `PyPDF2`)
- Dependencies are regularly checked for known vulnerabilities
- No known vulnerabilities in current dependency versions

### 5. File Handling
- Files are opened with appropriate read/write modes
- All file operations include proper exception handling
- Thread-safe CSV writing using locks to prevent data corruption

### 6. Logging
- Sensitive file paths are logged only to local log files (not transmitted)
- No credentials or secrets are logged
- Log files are stored locally in the `logs/` directory

## Data Privacy

### What Data is Processed
- PDF invoice files in the configured watch folder
- Invoice metadata (invoice number, date, total, vendor name)

### What is NOT Collected
- No data is sent to external servers
- No analytics or telemetry
- No user tracking
- No internet connection required (runs completely offline)

### Data Storage
- All processed data remains on your local machine
- CSV output is stored in the location you specify
- Log files are stored locally in the `logs/` directory

## Best Practices

### For Users
1. **Watch Folder Location**: Place your watch folder in a secure location with appropriate file permissions
2. **Configuration Files**: Keep `config.json` secure and don't share it if it contains sensitive paths
3. **Log Files**: Regularly review and clean up log files in the `logs/` directory
4. **Dependencies**: Keep Python and dependencies up to date
5. **Permissions**: Run the application with minimal necessary permissions (don't use admin/root unless required)

### For Developers
1. **Code Review**: All changes should be reviewed for security implications
2. **Dependency Updates**: Regularly check for and apply security updates to dependencies
3. **Testing**: Test security measures with various file path scenarios
4. **Documentation**: Keep security documentation up to date

## Known Limitations

### What PyInv-Auto Does NOT Do
- Does not provide encryption for stored data (use OS-level encryption if needed)
- Does not authenticate users (assumes single-user or trusted environment)
- Does not validate PDF content for malicious payloads (relies on PyPDF2's security)
- Does not sandbox PDF processing (inherits PyPDF2's security model)

### Recommended Additional Security
If processing untrusted PDFs, consider:
1. Running PyInv-Auto in a sandboxed environment (Docker container recommended)
2. Using antivirus scanning on PDFs before processing
3. Implementing file integrity checks
4. Using OS-level file permissions to restrict access

## Reporting a Vulnerability

If you discover a security vulnerability in PyInv-Auto, please report it responsibly:

### How to Report
1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Contact the maintainer directly through GitHub's security advisory feature
3. Provide detailed information about the vulnerability:
   - Description of the issue
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### What to Expect
- Acknowledgment of your report within 48 hours
- Assessment of the vulnerability within 1 week
- Communication about fix timeline
- Credit in the security advisory (if desired)

### Response Process
1. We will investigate and confirm the vulnerability
2. We will develop and test a fix
3. We will release a security update
4. We will publish a security advisory

## Security Checklist for Deployment

Before deploying PyInv-Auto in production:

- [ ] Review and understand the security measures documented here
- [ ] Configure appropriate file system permissions on watch folder
- [ ] Ensure Python and dependencies are up to date
- [ ] Review the configuration file for sensitive information
- [ ] Test with sample data before processing real invoices
- [ ] Set up log rotation to prevent disk space issues
- [ ] Consider running in Docker for additional isolation
- [ ] Document your deployment security measures

## Contact

For security concerns that are not vulnerabilities (questions about security features, best practices, etc.):
- Open a GitHub discussion
- Check existing documentation
- Review this security policy

---

**Last Updated**: November 2024  
**Version**: 1.0

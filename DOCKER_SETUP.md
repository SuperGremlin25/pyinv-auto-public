# Docker Setup Guide for PyInv-Auto

This guide explains how to run PyInv-Auto using Docker for easy deployment and portability.

## 🐳 Why Docker?

- **Portability**: Run anywhere Docker is installed (Windows, Mac, Linux)
- **No Python Setup**: No need to install Python or dependencies
- **Isolation**: Runs in its own container without affecting your system
- **Easy Updates**: Rebuild container to update
- **Consistent Environment**: Same behavior across all systems

## 📋 Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed
- Basic familiarity with command line

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Place your invoice PDFs in the `invoices` folder**
   ```bash
   mkdir -p invoices
   cp your-invoices/*.pdf invoices/
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up
   ```

3. **Check the output**
   - CSV file will be in `output/invoices_parsed.csv`
   - Logs will be in `logs/` directory

### Option 2: Using Docker CLI

1. **Build the image**
   ```bash
   docker build -t pyinv-auto .
   ```

2. **Run the container (process-only mode)**
   ```bash
   docker run --rm \
     -v "$(pwd)/invoices:/app/invoices" \
     -v "$(pwd)/output:/app/output" \
     -v "$(pwd)/logs:/app/logs" \
     pyinv-auto
   ```

3. **Run in watch mode (continuous monitoring)**
   ```bash
   docker run --rm \
     -v "$(pwd)/invoices:/app/invoices" \
     -v "$(pwd)/output:/app/output" \
     -v "$(pwd)/logs:/app/logs" \
     pyinv-auto python pyinv_auto.py
   ```

## 📁 Volume Mounts Explained

The Docker setup uses three volume mounts:

| Volume | Purpose | Local Path |
|--------|---------|------------|
| `/app/invoices` | Input PDFs | `./invoices` |
| `/app/output` | CSV output | `./output` |
| `/app/logs` | Log files | `./logs` |

## ⚙️ Configuration

### Using Custom Config

Create a custom `config.json` and mount it:

```bash
docker run --rm \
  -v "$(pwd)/invoices:/app/invoices" \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/my-config.json:/app/config.json" \
  pyinv-auto
```

### Environment Variables

You can pass environment variables for configuration:

```yaml
# docker-compose.yml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=DEBUG
```

## 🔧 Common Use Cases

### 1. One-Time Processing

Process all PDFs and exit:

```bash
docker-compose up
```

Or:

```bash
docker run --rm \
  -v "$(pwd)/invoices:/app/invoices" \
  -v "$(pwd)/output:/app/output" \
  pyinv-auto
```

### 2. Continuous Monitoring

Watch folder for new PDFs:

```yaml
# docker-compose.yml
services:
  pyinv-auto:
    command: python pyinv_auto.py  # Remove --process-only
```

Then run:
```bash
docker-compose up -d  # Run in background
```

### 3. Scheduled Processing (Cron-like)

Use Docker with a cron job or task scheduler:

**Linux/Mac (crontab):**
```bash
# Run every hour
0 * * * * cd /path/to/pyinv-auto && docker-compose up
```

**Windows (Task Scheduler):**
```powershell
# Create a scheduled task that runs:
docker-compose -f C:\path\to\pyinv-auto\docker-compose.yml up
```

### 4. Background Service

Run as a background service that watches for new files:

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop service
docker-compose down
```

## 🪟 Windows-Specific Notes

### PowerShell Volume Paths

Use PowerShell-style paths:

```powershell
docker run --rm `
  -v "${PWD}/invoices:/app/invoices" `
  -v "${PWD}/output:/app/output" `
  -v "${PWD}/logs:/app/logs" `
  pyinv-auto
```

### Docker Desktop Settings

1. Open Docker Desktop
2. Go to Settings → Resources → File Sharing
3. Ensure your project directory is shared

## 🔍 Troubleshooting

### Problem: Permission Denied

**Solution**: Ensure Docker has access to your folders:

```bash
# Linux/Mac: Fix permissions
chmod -R 755 invoices output logs

# Windows: Check Docker Desktop file sharing settings
```

### Problem: Container Exits Immediately

**Solution**: Check logs:

```bash
docker-compose logs
```

Or:

```bash
docker logs pyinv-auto
```

### Problem: No Output Files

**Solution**: Verify volume mounts:

```bash
# Check if volumes are mounted correctly
docker inspect pyinv-auto
```

### Problem: Can't See Logs

**Solution**: Logs are in the mounted `logs/` directory:

```bash
# View logs from host
cat logs/pyinv_auto_*.log

# Or view from container
docker exec -it pyinv-auto cat /app/logs/pyinv_auto_*.log
```

## 🔄 Updating

To update PyInv-Auto:

1. **Pull latest code**
   ```bash
   git pull
   ```

2. **Rebuild container**
   ```bash
   docker-compose build --no-cache
   ```

3. **Restart**
   ```bash
   docker-compose up
   ```

## 🧹 Cleanup

Remove containers and images:

```bash
# Stop and remove containers
docker-compose down

# Remove image
docker rmi pyinv-auto

# Remove all unused Docker resources
docker system prune -a
```

## 📊 Monitoring

### View Real-Time Logs

```bash
# With docker-compose
docker-compose logs -f

# With docker run
docker logs -f pyinv-auto
```

### Check Container Status

```bash
docker ps
```

### Execute Commands in Container

```bash
# Open shell in running container
docker exec -it pyinv-auto /bin/bash

# Run specific command
docker exec pyinv-auto python pyinv_auto.py --help
```

## 🎯 Best Practices

1. **Use Docker Compose** for easier management
2. **Mount volumes** for persistent data
3. **Check logs** regularly in the `logs/` directory
4. **Backup CSV files** from the `output/` directory
5. **Update regularly** by rebuilding the image
6. **Use specific tags** in production (e.g., `pyinv-auto:v1.0`)

## 🚢 Production Deployment

For production use:

1. **Tag your image**
   ```bash
   docker build -t pyinv-auto:1.0 .
   ```

2. **Use restart policies**
   ```yaml
   restart: unless-stopped
   ```

3. **Set resource limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

4. **Enable logging**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

## 📝 Example docker-compose.yml (Full)

```yaml
version: '3.8'

services:
  pyinv-auto:
    build: .
    container_name: pyinv-auto
    volumes:
      - ./invoices:/app/invoices
      - ./logs:/app/logs
      - ./output:/app/output
      - ./config.json:/app/config.json  # Optional: custom config
    environment:
      - PYTHONUNBUFFERED=1
    command: python pyinv_auto.py --process-only
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🆘 Need Help?

- Check the main [README.md](README.md) for general usage
- Review Docker logs: `docker-compose logs`
- Check application logs in `logs/` directory
- Open an issue on GitHub

---

**Happy Dockerizing!** 🐳

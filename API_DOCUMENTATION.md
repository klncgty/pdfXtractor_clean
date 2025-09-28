

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file` | File | Yes | PDF file to process (multipart/form-data) |
| `output_format` | String | No | Output format: "json", "csv", or "both" (default: "both") |
| `pages_limit` | Integer | No | Maximum pages to process (default: user's remaining quota) |

#### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "X-API-Key: pdfx_your_api_key_here" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F "output_format=both" \
  -F "pages_limit=10"
```

#### Success Response (200)

```json
{
  "success": true,
  "filename": "document.pdf",
  "pages_total": 20,
  "pages_processed": 10,
  "tables_found": 3,
  "tables": [
    {
      "page": 1,
      "table_index": 0,
      "json_file": "output_page_1_table_0.json",
      "csv_file": "output_page_1_table_0.csv",
      "image_file": "page_1_table_0.png"
    },
    {
      "page": 3,
      "table_index": 0,
      "json_file": "output_page_3_table_0.json",
      "csv_file": "output_page_3_table_0.csv", 
      "image_file": "page_3_table_0.png"
    }
  ],
  "api_usage": {
    "requests_made_this_month": 15,
    "monthly_request_limit": 1000,
    "remaining_requests": 985
  },
  "user_quota": {
    "pages_processed_this_month": 45,
    "monthly_page_limit": 30
  }
}
```

### 2. Download Extracted Files

**GET** `/v1/download/{filename}`

Download extracted table files (JSON, CSV, or image files).

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `filename` | String | Yes | Filename returned from extract endpoint |

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/v1/download/output_page_1_table_0.json" \
  -H "X-API-Key: pdfx_your_api_key_here" \
  -o "table_data.json"
```

### 3. Get API Usage Statistics

**GET** `/v1/usage`

Get current API usage and quota information for your API key.

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/v1/usage" \
  -H "X-API-Key: pdfx_your_api_key_here"
```

#### Response

```json
{
  "api_key_name": "Production Key",
  "requests_made_this_month": 15,
  "monthly_request_limit": 1000,
  "remaining_requests": 985,
  "last_used": "2025-09-27T02:14:32.123456",
  "is_active": true,
  "user_quota": {
    "pages_processed_this_month": 45,
    "monthly_page_limit": 30,
    "pages_remaining": -15
  }
}
```

### 4. Health Check

**GET** `/v1/health`

Check API service health and status.

#### Example Request

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

#### Response

```json
{
  "status": "healthy",
  "api_version": "v1.0.0",
  "service": "Octro API"
}
```

## API Key Management

### Create API Key (Web Interface Only)

**POST** `/auth/api-keys?name={key_name}`

Create a new API key. This endpoint requires web authentication (Google OAuth session).

**Note**: This endpoint is only available through the web interface dashboard, not for programmatic access.

### List API Keys (Web Interface Only)

**GET** `/auth/api-keys`

Get all your API keys. Requires web authentication.

### Delete API Key (Web Interface Only)

**DELETE** `/auth/api-keys/{api_key_id}`

Delete an API key. Requires web authentication.

## Error Responses

The API uses standard HTTP status codes and returns errors in JSON format:

```json
{
  "detail": "Error message description"
}
```

### Common Error Codes

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | Bad Request | Invalid request parameters or malformed PDF |
| 401 | Unauthorized | Invalid or missing API key |
| 403 | Forbidden | Monthly quota exceeded (pages or requests) |
| 404 | Not Found | Requested file or endpoint not found |
| 413 | Payload Too Large | File size too large |
| 422 | Unprocessable Entity | Invalid file format (only PDF supported) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error during processing |

### Error Examples

**Quota Exceeded:**
```json
{
  "detail": "Monthly quota exceeded. Monthly limit is 30 pages, you have processed 30 pages this month."
}
```

**Invalid API Key:**
```json
{
  "detail": "Geçersiz API key"
}
```

**File Not Found:**
```json
{
  "detail": "File not found"
}
```

## SDK Examples

### Python

```python
import requests
import json

API_KEY = "pdfx_your_api_key_here"
BASE_URL = "http://localhost:8000/api"

def extract_tables(pdf_path, output_format="both", pages_limit=None):
    """Extract tables from PDF using Octro API"""
    
    headers = {"X-API-Key": API_KEY}
    
    # Prepare form data
    files = {"file": open(pdf_path, 'rb')}
    data = {"output_format": output_format}
    
    if pages_limit:
        data["pages_limit"] = pages_limit
    
    try:
        response = requests.post(
            f"{BASE_URL}/v1/extract",
            headers=headers,
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Request failed: {e}")
        return None
    finally:
        files["file"].close()

def download_file(filename, output_path):
    """Download extracted file"""
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(
            f"{BASE_URL}/v1/download/{filename}",
            headers=headers
        )
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Download error: {e}")
        return False

def check_usage():
    """Check API usage statistics"""
    
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(
            f"{BASE_URL}/v1/usage",
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Usage check failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Usage check error: {e}")
        return None

# Usage Examples
if __name__ == "__main__":
    # Extract tables
    result = extract_tables("document.pdf", output_format="json", pages_limit=5)
    
    if result and result["success"]:
        print(f"Found {len(result['tables'])} tables")
        
        # Download files
        for table in result["tables"]:
            if "json_file" in table:
                download_file(table["json_file"], f"local_{table['json_file']}")
            if "csv_file" in table:
                download_file(table["csv_file"], f"local_{table['csv_file']}")
    
    # Check usage
    usage = check_usage()
    if usage:
        print(f"API Usage: {usage['requests_made_this_month']}/{usage['monthly_request_limit']}")
        print(f"Pages Used: {usage['user_quota']['pages_processed_this_month']}/{usage['user_quota']['monthly_page_limit']}")
```

### JavaScript/Node.js

```javascript
const fs = require('fs');
const FormData = require('form-data');
const axios = require('axios');

const API_KEY = 'pdfx_your_api_key_here';
const BASE_URL = 'http://localhost:8000/api';

async function extractTables(pdfPath, outputFormat = 'both', pagesLimit = null) {
    try {
        const form = new FormData();
        form.append('file', fs.createReadStream(pdfPath));
        form.append('output_format', outputFormat);
        
        if (pagesLimit) {
            form.append('pages_limit', pagesLimit.toString());
        }
        
        const response = await axios.post(`${BASE_URL}/v1/extract`, form, {
            headers: {
                'X-API-Key': API_KEY,
                ...form.getHeaders()
            }
        });
        
        return response.data;
        
    } catch (error) {
        console.error('API Error:', error.response?.data || error.message);
        return null;
    }
}

async function downloadFile(filename, outputPath) {
    try {
        const response = await axios({
            method: 'GET',
            url: `${BASE_URL}/v1/download/${filename}`,
            headers: {
                'X-API-Key': API_KEY
            },
            responseType: 'stream'
        });
        
        const writer = fs.createWriteStream(outputPath);
        response.data.pipe(writer);
        
        return new Promise((resolve, reject) => {
            writer.on('finish', resolve);
            writer.on('error', reject);
        });
        
    } catch (error) {
        console.error('Download Error:', error.response?.data || error.message);
        return false;
    }
}

async function checkUsage() {
    try {
        const response = await axios.get(`${BASE_URL}/v1/usage`, {
            headers: {
                'X-API-Key': API_KEY
            }
        });
        
        return response.data;
        
    } catch (error) {
        console.error('Usage Check Error:', error.response?.data || error.message);
        return null;
    }
}

// Usage Example
async function main() {
    // Extract tables
    const result = await extractTables('document.pdf', 'json', 5);
    
    if (result && result.success) {
        console.log(`Found ${result.tables.length} tables`);
        
        // Download files
        for (const table of result.tables) {
            if (table.json_file) {
                await downloadFile(table.json_file, `local_${table.json_file}`);
            }
        }
    }
    
    // Check usage
    const usage = await checkUsage();
    if (usage) {
        console.log(`API Usage: ${usage.requests_made_this_month}/${usage.monthly_request_limit}`);
        console.log(`Pages Used: ${usage.user_quota.pages_processed_this_month}/${usage.user_quota.monthly_page_limit}`);
    }
}

main().catch(console.error);
```

### cURL Examples

```bash
#!/bin/bash

# Set your API key
API_KEY="pdfx_your_api_key_here"
PDF_FILE="document.pdf"

echo "Extracting tables from PDF..."
curl -X POST "http://localhost:8000/api/v1/extract" \
  -H "X-API-Key: $API_KEY" \
  -F "file=@$PDF_FILE" \
  -F "output_format=json" \
  -F "pages_limit=5" \
  -o "extraction_result.json"

echo "Checking API usage..."
curl -X GET "http://localhost:8000/api/v1/usage" \
  -H "X-API-Key: $API_KEY" \
  | python -m json.tool

echo "Downloading extracted file..."
curl -X GET "http://localhost:8000/api/v1/download/output_page_1_table_0.json" \
  -H "X-API-Key: $API_KEY" \
  -o "table_data.json"

echo "Health check..."
curl -X GET "http://localhost:8000/api/v1/health" \
  | python -m json.tool
```

## Best Practices

### Security

1. **Keep API keys secure**: Never expose API keys in client-side code or public repositories
2. **Use environment variables**: Store API keys in environment variables, not hardcoded in source
3. **Rotate keys regularly**: Generate new API keys periodically for enhanced security
4. **Monitor usage**: Regularly check API usage to detect unusual activity
5. **Use HTTPS in production**: Always use secure connections in production environments

### Performance & Efficiency

1. **Optimize file sizes**: Compress PDFs when possible to reduce upload time
2. **Set appropriate page limits**: Use `pages_limit` to process only necessary pages and save quota
3. **Choose optimal output format**: 
   - Use `"json"` if you only need structured data
   - Use `"csv"` if you only need spreadsheet format
   - Use `"both"` only when you need both formats
4. **Cache results**: Store extraction results to avoid re-processing the same documents
5. **Batch processing**: Process multiple files efficiently by managing your quota

### Error Handling

1. **Check HTTP status codes**: Always verify response status before processing data
2. **Handle rate limits gracefully**: Implement exponential backoff for 429 responses
3. **Validate files before upload**: Ensure files are valid PDFs and within size limits
4. **Monitor quota usage**: Track your monthly limits to avoid service interruption
5. **Log errors appropriately**: Maintain detailed logs for debugging and monitoring

### Integration Tips

1. **Test with sample files**: Start with small, simple PDFs to verify integration
2. **Handle empty results**: Some PDFs may not contain detectable tables
3. **Process files asynchronously**: For large files, consider background processing
4. **Implement progress tracking**: Show users progress for long-running operations
5. **Graceful degradation**: Have fallback options when the API is unavailable

## Quotas & Limits

### Page Processing Quota
- **Monthly Page Limit**: 30 pages per user per month
- Quota resets automatically on the 1st of each month
- Unused pages do not carry over to the next month

### API Request Limits
- **Monthly Request Limit**: 1000 requests per API key per month
- Each API key tracks usage independently
- Limits apply per calendar month

### File Constraints
- **Maximum file size**: No explicit limit, but very large files may timeout
- **Supported formats**: PDF files only
- **Processing timeout**: Long-running extractions may be terminated

## Support & Resources

### Getting Help

1. **Documentation**: This comprehensive guide covers most use cases
2. **Dashboard**: Monitor usage and manage API keys at [http://localhost:5175/dashboard](http://localhost:5175/dashboard)
3. **Health Check**: Verify API status at [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### Troubleshooting Common Issues

**"Invalid API key" Error**
- Verify your API key format (should start with `pdfx_`)
- Check that the key hasn't been deleted from your dashboard
- Ensure the `X-API-Key` header is set correctly

**"Monthly quota exceeded" Error**
- Check your usage at `/v1/usage` endpoint
- Wait for monthly reset or reduce page processing
- Consider optimizing your usage patterns

**File Upload Failures**
- Verify file is a valid PDF
- Check file permissions and accessibility
- Ensure multipart/form-data encoding is used

**Empty Results**
- Some PDFs may not contain detectable tables
- Try different pages with `pages_limit` parameter
- Verify PDF contains actual table structures (not just text)

## Changelog

### v1.0.0 (2025-09-27)
- Initial API release
- PDF table extraction with JSON/CSV output
- API key authentication and management
- Rate limiting and quota tracking
- File download capabilities
- Usage statistics endpoint
- Health monitoring endpoint
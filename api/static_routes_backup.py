from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
import os
import re

router = APIRouter()

def markdown_to_html(md_content):
    """Simple markdown to HTML converter with TOC generation"""
    html = md_content
    
    # Extract headings for TOC
    toc_items = []
    import re
    
    # Find all headings and create anchors
    def replace_heading(match):
        level = len(match.group(1))
        title = match.group(2).strip()
        # Create anchor from title
        anchor = re.sub(r'[^\w\s-]', '', title).strip()
        anchor = re.sub(r'[-\s]+', '-', anchor).lower()
        
        toc_items.append({
            'level': level,
            'title': title,
            'anchor': anchor
        })
        
        return f'<h{level} id="{anchor}">{title}</h{level}>'
    
    # Replace headers with anchored versions
    html = re.sub(r'^(#{1,6})\s+(.*?)$', replace_heading, html, flags=re.MULTILINE)
    
    # Code blocks
    html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code class="language-\1">\2</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'````(\w+)?\n(.*?)\n````', r'<pre><code class="language-\1">\2</code></pre>', html, flags=re.DOTALL)
    
    # Inline code
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Bold text
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', html)
    
    # Tables - simple conversion
    lines = html.split('\n')
    processed_lines = []
    in_table = False
    
    for i, line in enumerate(lines):
        if '|' in line and line.strip().startswith('|') and line.strip().endswith('|'):
            if not in_table:
                processed_lines.append('<table>')
                in_table = True
                
            # Check if this is a header separator line
            if i + 1 < len(lines) and '---' in lines[i + 1]:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                processed_lines.append('<thead><tr>')
                for cell in cells:
                    processed_lines.append(f'<th>{cell}</th>')
                processed_lines.append('</tr></thead>')
                processed_lines.append('<tbody>')
            elif '---' not in line:
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                processed_lines.append('<tr>')
                for cell in cells:
                    processed_lines.append(f'<td>{cell}</td>')
                processed_lines.append('</tr>')
        else:
            if in_table:
                processed_lines.append('</tbody></table>')
                in_table = False
            if line.strip():
                processed_lines.append(f'<p>{line}</p>')
            else:
                processed_lines.append('<br>')
    
    if in_table:
        processed_lines.append('</tbody></table>')
    
    # Generate TOC HTML (non-collapsible, all items visible like Ragie docs)
    toc_html = '<div class="toc"><h3>İçindekiler</h3>'
    
    # Add Overview as first item
    toc_html += '<div class="toc-level-1"><a href="#overview">Overview</a></div>'
    
    for item in toc_items:
        indent_class = f"toc-level-{item['level']}"
        toc_html += f'<div class="{indent_class}"><a href="#{item["anchor"]}">{item["title"]}</a></div>'
    
    toc_html += '</div>'
    
    return '\n'.join(processed_lines), toc_html

@router.get('/api-docs')
async def get_api_documentation():
    """API documentation sayfası"""
    try:
        # Markdown dosyasını oku
        base_dir = os.path.dirname(os.path.dirname(__file__))  # Parent directory
        md_path = os.path.join(base_dir, 'API_DOCUMENTATION.md')
        
        with open(md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Markdown'ı HTML'e dönüştür
        html_content, toc_html = markdown_to_html(md_content)
        
        # Overview içeriğini oluştur
        overview_content = """
        <h1 id="overview">Overview</h1>
        <p>Welcome to the Octro API documentation. This API allows you to extract tables from PDF documents with high accuracy using advanced machine learning models.</p>
        
        <h2>Key Features</h2>
        <ul>
            <li>📄 PDF table extraction with ML-powered accuracy</li>
            <li>🔐 Secure API key authentication</li>
            <li>📊 Multiple output formats (JSON, CSV)</li>
            <li>🎯 Page-specific and bulk processing</li>
            <li>📈 Usage tracking and quotas</li>
        </ul>
        
        <h2>Getting Started</h2>
        <p>To get started with the API:</p>
        <ol>
            <li>Navigate to the <a href="http://localhost:5175/dashboard">Dashboard</a></li>
            <li>Generate your API key</li>
            <li>Use the TOC menu on the left to explore different sections</li>
            <li>Start making API calls to extract tables from your PDFs</li>
        </ol>
        
        <div style="background: rgba(59, 130, 246, 0.1); padding: 16px; border-radius: 8px; margin: 20px 0;">
            <p><strong>💡 Tip:</strong> Click on any section in the table of contents to view detailed information about that topic.</p>
        </div>
        """
        
        # Styled HTML template
        styled_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Octro API Documentation</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
            <style>
                :root {{
                    --bg-primary: #0a0a0a;
                    --bg-secondary: #1a1a1a;
                    --bg-tertiary: #2a2a2a;
                    --text-primary: #ffffff;
                    --text-secondary: #d1d5db;
                    --text-muted: #9ca3af;
                    --border-color: #374151;
                    --accent-blue: #3b82f6;
                    --accent-green: #10b981;
                    --accent-yellow: #f59e0b;
                    --accent-red: #ef4444;
                }}
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.7;
                    background: var(--bg-primary);
                    color: var(--text-primary);
                    font-size: 16px;
                    font-weight: 400;
                }}
                
                .main-container {{
                    display: flex;
                    max-width: 1300px;
                    margin: 0 auto;
                    gap: 30px;
                    padding-top: 20px;
                }}
                
                .sidebar {{
                    width: 240px;
                    position: sticky;
                    top: 120px;
                    height: fit-content;
                    max-height: calc(100vh - 140px);
                    overflow-y: auto;
                    padding: 0 15px;
                }}
                
                .content-area {{
                    flex: 1;
                    min-width: 0;
                    padding: 0 20px;
                }}
                
                .back-button {{
                    position: fixed;
                    top: 16px;
                    left: 24px;
                    background: var(--accent-blue);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 8px;
                    text-decoration: none;
                    font-size: 0.85rem;
                    font-weight: 500;
                    transition: all 0.2s ease;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
                    z-index: 1001;
                    display: flex;
                    align-items: center;
                    gap: 6px;
                }}
                
                .back-button:hover {{
                    background: #2563eb;
                    transform: translateY(-2px);
                    box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
                }}
                
                .content {{
                    padding: 60px 0;
                }}
                
                h1, h2, h3, h4 {{
                    font-weight: 600;
                    margin: 40px 0 20px 0;
                    color: var(--text-primary);
                    line-height: 1.3;
                }}
                
                h1 {{ font-size: 2.5rem; color: var(--accent-blue); }}
                h2 {{ 
                    font-size: 2rem; 
                    padding-bottom: 12px;
                    border-bottom: 2px solid var(--border-color);
                    margin-top: 60px;
                }}
                h3 {{ 
                    font-size: 1.5rem; 
                    color: var(--accent-green);
                    margin-top: 40px;
                }}
                h4 {{ font-size: 1.25rem; }}
                
                p {{
                    margin: 16px 0;
                    color: var(--text-secondary);
                    line-height: 1.7;
                }}
                
                code {{
                    background: var(--bg-secondary);
                    padding: 4px 8px;
                    border-radius: 6px;
                    border: 1px solid var(--border-color);
                    font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace;
                    font-size: 0.875rem;
                    font-weight: 500;
                    color: var(--accent-blue);
                }}
                
                pre {{
                    background: var(--bg-secondary);
                    padding: 24px;
                    border-radius: 12px;
                    border: 1px solid var(--border-color);
                    overflow-x: auto;
                    margin: 24px 0;
                    position: relative;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                
                pre code {{
                    background: none;
                    padding: 0;
                    border: none;
                    color: var(--text-primary);
                    font-size: 0.875rem;
                    line-height: 1.6;
                }}
                
                blockquote {{
                    border-left: 4px solid var(--accent-blue);
                    padding: 20px;
                    margin: 24px 0;
                    background: var(--bg-secondary);
                    border-radius: 8px;
                    border-top-left-radius: 0;
                    border-bottom-left-radius: 0;
                }}
                
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 32px 0;
                    background: var(--bg-secondary);
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                }}
                
                th, td {{
                    padding: 16px 20px;
                    text-align: left;
                    border-bottom: 1px solid var(--border-color);
                }}
                
                th {{
                    background: var(--bg-tertiary);
                    font-weight: 600;
                    color: var(--text-primary);
                    font-size: 0.875rem;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }}
                
                td {{
                    color: var(--text-secondary);
                }}
                
                tr:hover {{
                    background: rgba(255, 255, 255, 0.02);
                }}
                
                a {{
                    color: var(--accent-blue);
                    text-decoration: none;
                    font-weight: 500;
                    transition: color 0.2s ease;
                }}
                
                a:hover {{
                    color: #60a5fa;
                    text-decoration: underline;
                }}
                
                strong {{
                    font-weight: 600;
                    color: var(--text-primary);
                }}
                
                .endpoint-badge {{
                    display: inline-block;
                    background: var(--accent-green);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-right: 8px;
                }}
                
                .post {{ background: var(--accent-green); }}
                .get {{ background: var(--accent-blue); }}
                .delete {{ background: var(--accent-red); }}
                
                .section {{
                    margin-bottom: 80px;
                }}
                
                .toc {{
                    background: var(--bg-secondary);
                    border: 1px solid var(--border-color);
                    border-radius: 12px;
                    padding: 18px;
                    position: sticky;
                    top: 20px;
                }}
                
                .toc h3 {{
                    margin: 0 0 16px 0;
                    color: var(--text-primary);
                    font-size: 0.95rem;
                    font-weight: 600;
                    border-bottom: 1px solid var(--border-color);
                    padding-bottom: 10px;
                }}
                
                .toc ul {{
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }}
                
                .toc-section {{
                    margin-bottom: 8px;
                }}
                
                .toc-level-1 {{
                    margin: 12px 0 4px 0;
                }}
                
                .toc-level-1:first-child {{
                    margin-top: 0;
                }}
                
                .toc-level-1 a {{
                    display: block;
                    padding: 8px 12px;
                    color: var(--text-primary);
                    text-decoration: none;
                    font-size: 0.9rem;
                    font-weight: 600;
                    border-radius: 8px;
                    transition: all 0.2s ease;
                    background: rgba(255, 255, 255, 0.03);
                    border-left: 3px solid transparent;
                }}
                
                .toc-level-1 a:hover {{
                    background: rgba(59, 130, 246, 0.1);
                    color: var(--accent-blue);
                    border-left-color: var(--accent-blue);
                    transform: translateX(2px);
                }}
                
                .toc-level-2 {{
                    margin: 2px 0;
                    padding-left: 16px;
                }}
                
                .toc-level-2 a {{
                    display: block;
                    padding: 6px 12px;
                    color: var(--text-secondary);
                    text-decoration: none;
                    font-size: 0.85rem;
                    font-weight: 500;
                    border-radius: 6px;
                    transition: all 0.2s ease;
                    border-left: 2px solid transparent;
                }}
                
                .toc-level-2 a:hover {{
                    background: rgba(59, 130, 246, 0.08);
                    color: var(--accent-blue);
                    border-left-color: var(--accent-blue);
                    transform: translateX(2px);
                }}
                
                .toc-level-3 {{
                    margin: 1px 0;
                    padding-left: 32px;
                }}
                
                .toc-level-3 a {{
                    display: block;
                    padding: 4px 10px;
                    color: var(--text-muted);
                    text-decoration: none;
                    font-size: 0.8rem;
                    font-weight: 400;
                    border-radius: 4px;
                    transition: all 0.2s ease;
                }}
                
                .toc-level-3 a:hover {{
                    background: rgba(59, 130, 246, 0.06);
                    color: var(--text-secondary);
                    transform: translateX(2px);
                }}
                
                .toc-level-4 {{
                    margin: 1px 0;
                    padding-left: 48px;
                }}
                
                .toc-level-4 a {{
                    display: block;
                    padding: 3px 8px;
                    color: var(--text-muted);
                    text-decoration: none;
                    font-size: 0.75rem;
                    font-weight: 400;
                    border-radius: 4px;
                    transition: all 0.2s ease;
                }}
                
                .toc-level-4 a:hover {{
                    background: rgba(59, 130, 246, 0.05);
                    color: var(--text-secondary);
                    transform: translateX(1px);
                }}
                
                /* Active state for current section */
                .toc a.active {{
                    background: rgba(59, 130, 246, 0.15) !important;
                    color: var(--accent-blue) !important;
                    border-left-color: var(--accent-blue) !important;
                    font-weight: 600 !important;
                }}
                
                .toc::-webkit-scrollbar {{
                    width: 6px;
                }}
                
                .toc::-webkit-scrollbar-track {{
                    background: var(--bg-primary);
                    border-radius: 3px;
                }}
                
                .toc::-webkit-scrollbar-thumb {{
                    background: var(--border-color);
                    border-radius: 3px;
                }}
                
                .toc::-webkit-scrollbar-thumb:hover {{
                    background: var(--text-muted);
                }}
                
                .footer {{
                    border-top: 1px solid var(--border-color);
                    padding: 40px 0;
                    text-align: center;
                    color: var(--text-muted);
                    margin-top: 80px;
                }}
                
                @media (max-width: 1024px) {{
                    .main-container {{
                        flex-direction: column;
                        gap: 20px;
                    }}
                    
                    .sidebar {{
                        width: 100%;
                        position: static;
                        max-height: 300px;
                        order: -1;
                    }}
                    
                    .toc {{
                        margin-bottom: 40px;
                    }}
                }}
                
                @media (max-width: 768px) {{
                    .main-container {{ padding: 0 16px; }}
                    .back-button {{ position: relative; margin-bottom: 20px; }}
                    .sidebar {{ padding: 0; }}
                    .content-area {{ padding: 0; }}
                    .toc {{ padding: 16px; }}
                }}
            </style>
        </head>
        <body>
            <a href="http://localhost:5175/dashboard" class="back-button">
                ← Dashboard'a Dön
            </a>
            
            <div class="main-container">
                <div class="sidebar">
                    {toc_html}
                </div>
                <div class="content-area">
                    <div class="content" id="main-content">
                        <!-- Initially show only overview -->
                        <div id="content-overview" class="content-section">
                            {overview_content}
                        </div>
                        
                        <!-- Hidden sections that will be shown on demand -->
                        <div id="full-content" class="content-section" style="display: none;">
                            {html_content}
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <div style="max-width: 1300px; margin: 0 auto; padding: 0 20px; text-align: center;">
                    <p>© 2025 Octro. Built with ❤️ for developers.</p>
                </div>
            </div>
            
            <script>
                // Initialize syntax highlighting
                hljs.highlightAll();
                
                // Show specific section when TOC link is clicked
                document.querySelectorAll('.toc a[href^="#"]').forEach(anchor => {{
                    anchor.addEventListener('click', function (e) {{
                        e.preventDefault();
                        const targetId = this.getAttribute('href').substring(1);
                        
                        // Update active state in TOC
                        document.querySelectorAll('.toc a').forEach(link => link.classList.remove('active'));
                        this.classList.add('active');
                        
                        // Special case for overview
                        if (targetId === 'overview') {{
                            document.getElementById('content-overview').style.display = 'block';
                            document.getElementById('full-content').style.display = 'none';
                        }} else {{
                            // Show full content and scroll to target
                            document.getElementById('content-overview').style.display = 'none';
                            document.getElementById('full-content').style.display = 'block';
                            
                            // Scroll to target section
                            setTimeout(() => {{
                                const target = document.getElementById(targetId);
                                if (target) {{
                                    target.scrollIntoView({{
                                        behavior: 'smooth',
                                        block: 'start'
                                    }});
                                    
                                    // Highlight the target section briefly
                                    target.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                                    target.style.borderRadius = '8px';
                                    target.style.padding = '16px';
                                    target.style.transition = 'all 0.3s ease';
                                    
                                    setTimeout(() => {{
                                        target.style.backgroundColor = '';
                                        target.style.padding = '';
                                    }}, 2000);
                                }}
                            }}, 100);
                        }}
                    }});
                }});
                
                // Set overview as active by default
                document.addEventListener('DOMContentLoaded', function() {{
                    const overviewLink = document.querySelector('.toc a[href="#overview"]');
                    if (overviewLink) {{
                        overviewLink.classList.add('active');
                    }}
                }});
                
                // Active TOC highlighting on scroll (only when full content is visible)
                const observerOptions = {{
                    rootMargin: '-140px 0px -80% 0px'
                }};
                
                const observer = new IntersectionObserver(entries => {{
                    // Only update active states when full content is visible
                    if (document.getElementById('full-content').style.display !== 'none') {{
                        entries.forEach(entry => {{
                            const id = entry.target.getAttribute('id');
                            const tocLink = document.querySelector(`.toc a[href="#${{id}}"]`);
                            
                            if (entry.isIntersecting) {{
                                // Remove active class from all TOC links
                                document.querySelectorAll('.toc a').forEach(link => {{
                                    link.classList.remove('active');
                                }});
                                
                                // Add active class to current TOC link
                                if (tocLink) {{
                                    tocLink.classList.add('active');
                                }}
                            }}
                        }});
                    }}
                }}, observerOptions);
                
                // Observe all headings in full content
                setTimeout(() => {{
                    document.querySelectorAll('#full-content h1[id], #full-content h2[id], #full-content h3[id], #full-content h4[id]').forEach(heading => {{
                        observer.observe(heading);
                    }});
                }}, 500);
            </script>
                }});
            </script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=styled_html)
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return PlainTextResponse(f"Error loading documentation: {str(e)}\n\nFull traceback:\n{error_details}", status_code=500)
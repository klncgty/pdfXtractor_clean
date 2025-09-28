from fastapi import APIRouterfrom fastapi import APIRouter



router = APIRouter()router = APIRouter()



# ...existing code...

# Currently disabled for simplicity# Currently disabled for simplicity
    
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
    
    for item in toc_items:
        indent_class = f"toc-level-{item['level']}"
        toc_html += f'<div class="{indent_class}"><a href="#{item["anchor"]}">{item["title"]}</a></div>'
    
    toc_html += '</div>'
    
    return '\n'.join(processed_lines), toc_html

# ...existing code...
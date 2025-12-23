"""
Textract Response Parser
Parses Amazon Textract responses into structured data
"""


class TextractParser:
    """Parse Textract responses into structured format."""
    
    def parse_response(self, response):
        """
        Parse Textract AnalyzeDocument response.
        
        Args:
            response: Textract API response
            
        Returns:
            dict: Structured data with fields, tables, and raw text
        """
        blocks = response.get('Blocks', [])
        
        blocks_map = {block['Id']: block for block in blocks}
        
        fields = self._extract_key_value_pairs(blocks, blocks_map)
        tables = self._extract_tables(blocks, blocks_map)
        raw_text = self._extract_raw_text(blocks)
        
        return {
            'fields': fields,
            'tables': tables,
            'raw_text': raw_text,
            'block_count': len(blocks)
        }
    
    def _extract_key_value_pairs(self, blocks, blocks_map):
        """
        Extract form fields (key-value pairs) from Textract response.
        """
        fields = {}
        
        for block in blocks:
            if block['BlockType'] == 'KEY_VALUE_SET':
                if 'KEY' in block.get('EntityTypes', []):
                    key_text = self._get_text(block, blocks_map)
                    value_block = self._find_value_block(block, blocks_map)
                    
                    if value_block:
                        value_text = self._get_text(value_block, blocks_map)
                        if key_text and value_text:
                            fields[key_text] = value_text
        
        return fields
    
    def _extract_tables(self, blocks, blocks_map):
        """
        Extract tables from Textract response.
        """
        tables = []
        
        for block in blocks:
            if block['BlockType'] == 'TABLE':
                table = self._parse_table(block, blocks_map)
                if table:
                    tables.append(table)
        
        return tables
    
    def _parse_table(self, table_block, blocks_map):
        """
        Parse a single table block into rows and columns.
        """
        rows = {}
        
        if 'Relationships' not in table_block:
            return None
        
        for relationship in table_block['Relationships']:
            if relationship['Type'] == 'CHILD':
                for cell_id in relationship['Ids']:
                    cell = blocks_map.get(cell_id)
                    if cell and cell['BlockType'] == 'CELL':
                        row_index = cell.get('RowIndex', 0)
                        col_index = cell.get('ColumnIndex', 0)
                        
                        if row_index not in rows:
                            rows[row_index] = {}
                        
                        cell_text = self._get_text(cell, blocks_map)
                        rows[row_index][col_index] = cell_text
        
        table_data = []
        for row_index in sorted(rows.keys()):
            row = rows[row_index]
            row_data = [row.get(col_index, '') for col_index in sorted(row.keys())]
            table_data.append(row_data)
        
        return {
            'rows': len(table_data),
            'columns': len(table_data[0]) if table_data else 0,
            'data': table_data
        }
    
    def _extract_raw_text(self, blocks):
        """
        Extract all raw text from LINE blocks.
        """
        text_lines = []
        
        for block in blocks:
            if block['BlockType'] == 'LINE':
                text_lines.append(block.get('Text', ''))
        
        return '\n'.join(text_lines)
    
    def _get_text(self, block, blocks_map):
        """
        Get text content from a block and its children.
        """
        text = ''
        
        if 'Text' in block:
            text = block['Text']
        
        if 'Relationships' in block:
            for relationship in block['Relationships']:
                if relationship['Type'] == 'CHILD':
                    for child_id in relationship['Ids']:
                        child = blocks_map.get(child_id)
                        if child and child['BlockType'] == 'WORD':
                            text += child.get('Text', '') + ' '
        
        return text.strip()
    
    def _find_value_block(self, key_block, blocks_map):
        """
        Find the VALUE block associated with a KEY block.
        """
        if 'Relationships' not in key_block:
            return None
        
        for relationship in key_block['Relationships']:
            if relationship['Type'] == 'VALUE':
                for value_id in relationship['Ids']:
                    value_block = blocks_map.get(value_id)
                    if value_block:
                        return value_block
        
        return None

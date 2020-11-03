
class TsvTableDocument:

    def __init__(self):
        self.column_headers = []
        self.rows = []

    @staticmethod
    def get_tsv(file,
                open_in_text_mode=True,
                separator_char='\t',
                strip_line_break=False,
                strip_space=False):

        strip = ''
        if strip_line_break:
            strip = '\n'

        if open_in_text_mode:
            rows = [line.rstrip(strip).split(separator_char) for line in file]
        else:
            rows = []

        for line in file:
            try:
                rows.append(line.decode().rstrip(strip).split(separator_char))
            except UnicodeDecodeError as e:
                print(e)
                raise e

        if strip_space:
            rows = [[cell.strip() for cell in row] for row in rows]

        return rows

    @staticmethod
    def load_tsv(filepath,
                 open_in_text_mode=True,
                 encoding='utf8',
                 separator_char='\t',
                 strip_line_break=False,
                 strip_space=False):
        with open(filepath, encoding=encoding) as file:
            return TsvTableDocument.get_tsv(file, open_in_text_mode=open_in_text_mode, separator_char=separator_char, strip_line_break=strip_line_break, strip_space=strip_space)

    def load_from_file(self,
                       filepath,
                       open_in_text_mode=True,
                       encoding='utf8',
                       separator_char='\t',
                       strip_line_break=False,
                       strip_space=False):
        self.rows.clear()
        rows = TsvTableDocument.load_tsv(filepath=filepath, open_in_text_mode=open_in_text_mode, encoding=encoding, separator_char=separator_char,
                                         strip_line_break=strip_line_break, strip_space=strip_space)
        self.column_headers = rows[0]
        self.rows = rows[1:]
        print(f'loaded {len(self.column_headers)} columns and {len(self.rows)} rows')

    def get_columns(self):
        return self.column_headers

    def get_column_index(self, column_name):
        for i, col in enumerate(self.column_headers):
            if col == column_name:
                return i
        return None

    def __getitem__(self, item):
        return self.rows[item]

    def __len__(self):
        return len(self.rows)


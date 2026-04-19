import unittest
import sys
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from main import main

class TestMain(unittest.TestCase):
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.input_file = Path(self.temp_dir) / 'input.txt'
        self.output_file = Path(self.temp_dir) / 'output.txt'
    
    def tearDown(self):
        if self.input_file.exists():
            self.input_file.unlink()
        if self.output_file.exists():
            self.output_file.unlink()
        os.rmdir(self.temp_dir)
    
    @patch('sys.argv', ['main.py'])
    def test_default_hello_world(self):
        with patch('sys.stdout', new=StringIO()) as fake_out:
            main()
            self.assertEqual(fake_out.getvalue().strip(), 'Hello, World!')
    
    @patch('sys.argv', ['main.py', '--input', 'nonexistent.txt'])
    def test_nonexistent_input_file(self):
        with patch('sys.stderr', new=StringIO()) as fake_err:
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)
            self.assertIn('does not exist', fake_err.getvalue())
    
    def test_input_file_to_stdout(self):
        self.input_file.write_text('hello world')
        with patch('sys.argv', ['main.py', '--input', str(self.input_file)]):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                self.assertEqual(fake_out.getvalue().strip(), 'HELLO WORLD')
    
    def test_input_file_to_output_file(self):
        self.input_file.write_text('hello world')
        with patch('sys.argv', ['main.py', '--input', str(self.input_file), '--output', str(self.output_file)]):
            main()
            self.assertTrue(self.output_file.exists())
            self.assertEqual(self.output_file.read_text(), 'HELLO WORLD')
    
    def test_verbose_mode(self):
        self.input_file.write_text('test')
        with patch('sys.argv', ['main.py', '--input', str(self.input_file), '--output', str(self.output_file), '--verbose']):
            with patch('sys.stdout', new=StringIO()) as fake_out:
                main()
                output = fake_out.getvalue()
                self.assertIn('Input:', output)
                self.assertIn('Output:', output)
                self.assertIn('Processed content written', output)

if __name__ == '__main__':
    unittest.main()

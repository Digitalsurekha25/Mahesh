import unittest
from unittest.mock import patch
import io # For capturing print output

from src.input_handler import get_manual_input

class TestInputHandler(unittest.TestCase):

    @patch('builtins.input')
    def test_get_manual_input_valid_numbers_and_done(self, mock_input):
        mock_input.side_effect = ['10', '20', '0', '36', 'done']
        # Suppress print output during this test
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = get_manual_input()
        self.assertEqual(result, [10, 20, 0, 36])

    @patch('builtins.input')
    def test_get_manual_input_empty_to_finish(self, mock_input):
        mock_input.side_effect = ['5', '15', '']
        with patch('sys.stdout', new_callable=io.StringIO):
            result = get_manual_input()
        self.assertEqual(result, [5, 15])

    @patch('builtins.input')
    def test_get_manual_input_invalid_non_numeric(self, mock_input):
        mock_input.side_effect = ['abc', '10', 'done']
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = get_manual_input()
        self.assertEqual(result, [10])
        output = mock_stdout.getvalue()
        self.assertIn("Invalid input: Please enter a valid number or 'done'.", output)

    @patch('builtins.input')
    def test_get_manual_input_out_of_range(self, mock_input):
        mock_input.side_effect = ['-1', '37', '10', 'done']
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = get_manual_input()
        self.assertEqual(result, [10])
        output = mock_stdout.getvalue()
        self.assertIn("Invalid input: Number must be between 0 and 36.", output) # Checks for one of the messages

    @patch('builtins.input')
    def test_get_manual_input_mixed_valid_invalid(self, mock_input):
        mock_input.side_effect = ['1', 'hello', '25', '50', '0', 'done']
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = get_manual_input()
        self.assertEqual(result, [1, 25, 0])
        output = mock_stdout.getvalue()
        self.assertIn("Invalid input: Please enter a valid number or 'done'.", output)
        self.assertIn("Invalid input: Number must be between 0 and 36.", output)

    @patch('builtins.input')
    def test_get_manual_input_no_numbers_entered(self, mock_input):
        mock_input.side_effect = ['done']
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = get_manual_input()
        self.assertEqual(result, [])
        output = mock_stdout.getvalue()
        self.assertIn("No numbers were entered.", output)

    @patch('builtins.input')
    def test_get_manual_input_only_invalid_then_done(self, mock_input):
        mock_input.side_effect = ['-5', 'forty', '100', 'done']
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            result = get_manual_input()
        self.assertEqual(result, [])
        output = mock_stdout.getvalue()
        self.assertIn("No numbers were entered.", output)


if __name__ == '__main__':
    unittest.main()

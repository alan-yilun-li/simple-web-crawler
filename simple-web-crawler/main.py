import sys
from processor import scrape_inputs
from typing import Text

'''
This file contains the startup configuration code.

See README.md for more information on each given file.
'''

INPUT_FILE_FLAG = '--input-file'


def main() -> Text:
    '''Accepts line-separated input file through the --input-file flag, else defaults to input.txt'''

    # Would normally use Click or some other CLI library to accept input files
    try:
        input_file = sys.argv[sys.argv.index(INPUT_FILE_FLAG) + 1]
    except IndexError:
        print(f'no input file found after {INPUT_FILE_FLAG} flag')
        return ''
    except ValueError:
        input_file = 'input.txt'

    # this does NOT load the entire file into memory at once
    with open(input_file) as inputs:
        result = scrape_inputs(inputs)
        print(result)
        return result


if __name__ == '__main__':
    main()

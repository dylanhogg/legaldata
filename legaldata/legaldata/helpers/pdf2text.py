from pdfminer.high_level import extract_text


def convert_pdfminer(input_file):
    # print(dir(pdfminer))

    # https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
    # https://pdfminersix.readthedocs.io/en/latest/topic/converting_pdf_to_text.html
    # https://pdfminersix.readthedocs.io/en/latest/reference/highlevel.html#api-extract-text
    # https://pdfminersix.readthedocs.io/en/latest/tutorial/composable.html
    print("input_file = " + input_file)
    text = extract_text(input_file)

    output_file = input_file + ".pdfminer.txt"

    with open(output_file, "w") as f:
        print("output_file = " + output_file)
        f.write(text)

    return output_file

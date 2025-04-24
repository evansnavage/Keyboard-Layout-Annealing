# GPT 4.0 banger
import os


def merge_text_files(input_directory, output_file):
    with open(output_file, "w", encoding="utf-8") as outfile:
        for root, _, files in os.walk(input_directory):
            for file in files:
                if not file.startswith("."):  # Skip hidden or temporary files
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            outfile.write(infile.read())
                            outfile.write("\n")  # Add a newline between files
                    except (UnicodeDecodeError, FileNotFoundError):
                        print(f"Skipping file due to an error: {file_path}")


if __name__ == "__main__":
    input_directory = input("Enter the path to the input directory: ").strip()
    output_file = input("Enter the path to the output file: ").strip()
    merge_text_files(input_directory, output_file)
    print(
        f"All text files from '{input_directory}' have been merged into '{output_file}'."
    )

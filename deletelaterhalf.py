import sys


def halve_file(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        half_length = len(lines) // 2
        with open(file_path, "w") as file:
            file.writelines(lines[:half_length])

        print(f"File '{file_path}' has been halved successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python deletelaterhalf.py <file_path>")
    else:
        halve_file(sys.argv[1])

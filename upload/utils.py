from math import ceil


def get_number_of_chunks(file_size, chunk_size):
    return ceil(file_size / chunk_size)

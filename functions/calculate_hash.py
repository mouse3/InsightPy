def calculate_hash(file_path :str, algorithm : str):
    import hashlib
    if algorithm == '':
        algorithm = 'md5'
    # Initialize the hash object
    hash_func = getattr(hashlib, algorithm)()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hash_func.update(chunk)
    if hash_func.hexdigest() == None:
        return ''
    else:
        return hash_func.hexdigest()
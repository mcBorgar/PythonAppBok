def register_name():
    name = input("Enter the name to register: ")
    new_person = {'name': name, 'address': input("Enter the address: "), 'phone': input("Enter the phone number: ")}
    remote_file_path_names = '/home/bok/names.json'

    try:
        with sftp.open(remote_file_path_names, 'r') as file:
            names = json.load(file)
    except FileNotFoundError:
        names = []

    names.append(new_person)

    with sftp.open(remote_file_path_names, 'w') as file:
        json.dump(names, file, indent=4)

    print(f"Name registered: {name}")

register_name()
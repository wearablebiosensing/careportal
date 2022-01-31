# AES 256 encryption/decryption using pycrypto library
 # Example: https://medium.com/qvault/aes-256-cipher-python-cryptography-examples-b877b9d2e45e
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto import Random
import os
import json
# pad with spaces at the end of the text
# beacuse AES needs 16 byte blocks
def pad(s):
    block_size = 16
    remainder = len(s) % block_size
    padding_needed = block_size - remainder
    return s + padding_needed * ' '

# remove the extra spaces at the end
def unpad(s): 
    return s.rstrip()

def encrypt(plain_text, password):
    # generate a random salt
    salt = os.urandom(AES.block_size)
    # generate a random iv
    iv = Random.new().read(AES.block_size)
    # use the Scrypt KDF to get a private key from the password
    private_key = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    # pad text with spaces to be valid for AES CBC mode
    padded_text = pad(plain_text)
    # create cipher config
    cipher_config = AES.new(private_key, AES.MODE_CBC, iv)
    # return a dictionary with the encrypted text
    return {
        'cipher_text': base64.b64encode(cipher_config.encrypt(padded_text)),
        'salt': base64.b64encode(salt),
        'iv': base64.b64encode(iv)
    }
def decrypt(enc_dict, password):
    # decode the dictionary entries from base64
    salt = base64.b64decode(enc_dict['salt'])
    enc = base64.b64decode(enc_dict['cipher_text'])
    iv = base64.b64decode(enc_dict['iv'])
    # generate the private key from the password and salt
    private_key = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    # create the cipher config
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    # decrypt the cipher text
    decrypted = cipher.decrypt(enc)
    # unpad the text to remove the added spaces
    original = unpad(decrypted)

    return original

def main():
    folder_path = "/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/WBL/My_Thesis/careportal-webapp/static/plotlycharts/PatientID_75/"
    password = "weartech"
    for idx,file in enumerate(os.listdir(folder_path)):
        if file.startswith(""):
            print("File:",file)
            # for all_files in os.listdir(folder_path + file):
                    # 1. hr_stats_hour_pid_27.json, 2. hr_stats_pid_27.json
            if file.startswith("hr_stats_"):
                print("File name",file)
                with open(folder_path + file) as f:
                    data = json.load(f)
                # First let us encrypt secret message#"The secretest message"
                encrypted = encrypt(json.dumps(data), password)
                print("Encrypted msg: ",encrypted,type(encrypted))
                # Let us decrypt using our original password
                decrypted = decrypt(encrypted, password)
                print("Decrypted: ",bytes.decode(decrypted))
                # Write encrypted data to a file.
                # print("Get only first few chars",file.split(".")[0])
                with open(folder_path + file.split(".")[0] + ".txt", 'w') as json_file:
                    json.dump(encrypted, json_file)
                # with open('readme.txt', 'w') as f:
                #     f.write('readme')

    with open("/Users/shehjarsadhu/Desktop/UniversityOfRhodeIsland/Graduate/WBL/My_Thesis/careportal-webapp/static/plotlycharts/PatientID_34/hr_stats_pid_34.json") as f:
        d = json.load(f)
    print(d)
    

    
    

main()
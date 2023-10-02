import json
import os
import requests
from utils import download_image_from_url

def generate_nft_from_file(name, description, url):
    verbwire_api_token = os.environ['verbwire_token']
    contractAddress = os.environ['contract_address']

    url = "https://api.verbwire.com/v1/nft/mint/mintFromFile"
    download_image_from_url(url, 'nft.png')
    files = {"filePath": ("nft.png", open("nft.png", "rb"), "nft/png")}
    payload = {
        "chain": "bsc-testnet",
        "name": name,
        "description": description,
        "contractAddress": contractAddress
    }
    headers = {
        "accept": "application/json",
        "X-API-Key": f"{verbwire_api_token}"
    }

    response = requests.post(url, data=payload, files=files, headers=headers)
    print('response', response.text)
    nft_details = json.loads(response.text)['transaction_details']
    print('nft_details', nft_details)
    if nft_details['status'] == 'Sent':
        transactionHash = nft_details['transactionHash']
    return transactionHash

    
def trade_nft(sender_address, recipient_address, tokenId):
    verbwire_api_token = os.environ['verbwire_token']

    url = "https://api.verbwire.com/v1/nft/update/transferToken"

    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"chain\"\r\n\r\nbsc-testnet\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"contractAddress\"\r\n\r\n{os.environ['contract_address']}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"fromAddress\"\r\n\r\n{sender_address}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"toAddress\"\r\n\r\n{recipient_address}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"tokenId\"\r\n\r\n{tokenId}\r\n-----011000010111000001101001--\r\n\r\n"

    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001",
        "X-API-Key": f"{verbwire_api_token}"
    }

    response = requests.post(url, data=payload, headers=headers)
    print(response.text)

    transfer_details = json.loads(response.text)['transaction_details']
    print('transfer_details', transfer_details)
    if transfer_details['status'] == 'Sent':
        transactionHash = transfer_details['transactionHash']
    return transactionHash

def create_new_contract():
    url = "https://api.verbwire.com/v1/nft/deploy/deployContract"

    payload = "-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"chain\"\r\n\r\nbsc-testnet\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"contractName\"\r\n\r\nnovaContract\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"contractSymbol\"\r\n\r\nnova\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"contractType\"\r\n\r\nnft721\r\n-----011000010111000001101001--\r\n\r\n"
    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001"
    }
    response = requests.post(url, data=payload, headers=headers)
    print(response.text)
    return response

def view_my_nft():
    verbwire_api_token = os.environ['verbwire_token']
    url = "https://api.verbwire.com/v1/nft/userOps/nftsMinted"

    headers = {
        "accept": "application/json",
        "X-API-Key": f"{verbwire_api_token}"
    }

    response = requests.get(url, headers=headers)
    nfts_minted = json.loads(response.text)['nfts_minted']["NFT details"]
    nft_list = []
    for nft in nfts_minted:
        nft_dict = {
            "Transaction Hash": nft["transactionHash"],
            "Contract Name": nft["contractName"],
            "Contract Symbol": nft["contractSymbol"],
        }
        nft_list.append(nft_dict)
    print(nft_list)
    return nft_list

def add_file_to_ipfs(url):
    verbwire_api_token = os.environ['verbwire_token']
    url = "https://api.verbwire.com/v1/nft/store/fileFromUrl"

    payload = {"fileUrl": url}
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "X-API-Key": f"{verbwire_api_token}"
    }

    response = requests.post(url, data=payload, headers=headers)
    print(response.text)

    ipfs_url = json.loads(response.text)['ipfs_storage']['ipfs_url']
    return ipfs_url

def view_uploaded_ipfs_files():
    verbwire_api_token = os.environ['verbwire_token']
    url = "https://api.verbwire.com/v1/nft/userOps/ipfsUploads"

    headers = {
        "accept": "application/json",
        "X-API-Key": f"{verbwire_api_token}"
    }

    response = requests.get(url, headers=headers)
    file_details_list = []
    ipfs_file = json.loads(response.text)['ipfs_upload_details']
    for file_detail in ipfs_file["IPFS file details"]:
        file_info = {
            "File Name": file_detail["fileName"],
            "IPFS URL": file_detail["ipfsUrl"],
            "File Size": file_detail["fileSize"],
            "Status": file_detail["status"],
            "Date Uploaded": file_detail["dateUploaded"],
        }
        file_details_list.append(file_info)

    print(file_details_list)
    return file_details_list


def generate_nft_from_metadata(name,metadata):
    verbwire_api_token = os.environ['verbwire_token']
    contract_address= os.environ['contract_address']
    url = "https://api.verbwire.com/v1/nft/mint/mintFromMetadata"

    payload = f"-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"chain\"\r\n\r\nbsc-testnet\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"name\"\r\n\r\n{name}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"contractAddress\"\r\n\r\n{contract_address}\r\n-----011000010111000001101001\r\nContent-Disposition: form-data; name=\"data\"\r\n\r\n{metadata}\r\n-----011000010111000001101001--\r\n\r\n"
    headers = {
        "accept": "application/json",
        "content-type": "multipart/form-data; boundary=---011000010111000001101001",
        "X-API-Key": f"{verbwire_api_token}"
    }

    response = requests.post(url, data=payload, headers=headers)
    transfer_details = json.loads(response.text)['transaction_details']
    if transfer_details['status'] == 'Sent':
        transactionHash = transfer_details['transactionHash']
    return transactionHash
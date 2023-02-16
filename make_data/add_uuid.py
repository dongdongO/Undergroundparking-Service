import yaml
import requests
import json
from utils.general import LOGGER


def get_uuid(config, site):
    headers = {'Content-Type': 'application/json', 'X-API-KEY':'o0808kcg8sosssoc84gkkos0sss8kcok4s4k40so'}  # api key may have to change
    # headers = {'Content-Type': 'application/json'}  # api key may have to change
    url = f'https://{site}.watchmile.com/api/v1/parking/slot/'

    get_pos = get_yaml(config)

    # load data from server
    slot_data = get_server(url, headers)
    total_state = slot_data.json()['lists']
    # with open('test.yaml', 'w', encoding='utf-8') as f:
    #     yaml.dump(total_state, f, default_style=False)

    result = {}  # init result
    
    for key, value in get_pos.items():
        result[key] = value
        roi = []
        double_rois = []
        double_slots = []
        for i in value['roi']:
            roi.append(str(i))
        
        try:
            for i in value['double_rois']:
                double_rois.append(str(i))
        except KeyError:
            pass
        
        try:
            for i in value['double_slots']:
                double_slots.append(str(i))
        except KeyError:
            pass
        
        result[key]['roi'] = roi
        try:
            result[key]['double_rois'] = double_rois
        except KeyError:
            pass
        
        try:
            result[key]['double_slots'] = double_slots
        except KeyError:
            pass
        
        uuid_list = []
        for idx in value['pos']:
            for slot in total_state:
                if slot['slot_name'] in idx:
                    uuid_list.append(slot['uuid'])
                    break

        result[key]['uuid'] = uuid_list
    return_yaml('result.yaml', result)

def get_server(url: str, headers: str):
    """
    Server communication functions using get

    Args:
        url (str): Parking lot server address
        headers (str): request header
    """
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:  # if fail show in LOGGER
            LOGGER.info("HTTP Error code: ", r.status_code)
        return r
    # Error type
    except requests.exceptions.Timeout as errd:
        LOGGER.exception("Timeout Error : ", errd)
    except requests.exceptions.ConnectionError as errc:
        LOGGER.exception("Error Connecting : ", errc)
    except requests.exceptions.HTTPError as errb:
        LOGGER.exception("Http Error : ", errb)
        # Any Error except upper exception
    except requests.exceptions.RequestException as erra:
        LOGGER.exception("AnyException : ", erra)

def get_yaml(location: str):
    loads = dict()
    # yaml load from location
    with open(location) as f:
        loads = yaml.load(f, Loader=yaml.FullLoader)
    return loads

def return_yaml(location: str, return_dict):
    with open(location, 'w') as f:
        yaml.dump(return_dict, f)

# run
get_uuid('add_ip.yaml', 'ansan-grancity-xi')
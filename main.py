import random
from time import sleep


def get_status(server: str) -> str:
    statuses = ['VERIFY_RESIZE', 'Nothing', 'Pending']
    print(f'Checking: {server}')
    result = random.choice(statuses)
    print(f'Status is: {result}')
    return result


def do_something(action: str):
    print(f'Doing: {action}')


class Nova:
    @staticmethod
    def status(server):
        statuses = ['VERIFY_RESIZE', 'Nothing', 'Pending']
        print(f'Checking: {server}')
        result = random.choice(statuses)
        print(f'Status is: {result}')
        return result

    @staticmethod
    def remove(server):
        print(f'Removing {server}')

    @staticmethod
    def resize(server):
        result = random.choice([True, False])
        print(f'Server {server} resize result is {result}')
        if not result:
            raise Exception("500!")


def initial_shutoff_vm_resize(action, shutoff_servers):
    print(f'Initial list: {shutoff_servers}')
    while shutoff_servers:
        sleep(5)
        for server in shutoff_servers:
            check = action(server)
            if check != 'VERIFY_RESIZE':
                continue
            else:
                action('confirm')
                shutoff_servers.remove(server)
        print('Once again')
        print(f'Current Servers list: {shutoff_servers}')


'''
def confirm_shutoff_vm_resize(nova, shutoff_servers):
    while shutoff_servers:
        sleep(5)
        for server in shutoff_servers:
            check = nova.servers.get(server.id)
            if check.status != 'VERIFY_RESIZE':
                continue
            else:
                nova.servers.confirm_resize(server.id)
                shutoff_servers.remove(server)

'''


def _confirm_shutoff_vm_resize(action, shutoff_servers):
    print(f'Initial list: {shutoff_servers}')
    servers_list_empty = False
    while not servers_list_empty:
        sleep(5)
        for server in shutoff_servers[:]:
            status = action(server)
            if status == 'VERIFY_RESIZE':
                do_something(f'Remove {server}')
                shutoff_servers.remove(server)
        # shutoff_servers[:] = [server for server in shutoff_servers if action(server) != 'VERIFY_RESIZE']
        if not shutoff_servers:
            servers_list_empty = True
        print('Once again')
        print(f'Current Servers list: {shutoff_servers}')


def _new_shutoff_vm_resize(nova, shutoff_servers):
    print(f'Initial list: {shutoff_servers}')
    servers_list_empty = False
    while not servers_list_empty:
        shutoff_servers[:] = [server if nova.status(server) != 'VERIFY_RESIZE' else nova.remove(server) for server in shutoff_servers]
        if not shutoff_servers:
            servers_list_empty = True
        print('Once again')
        print(f'Current Servers list: {shutoff_servers}')


def confirm_resize(nova, server):
    try:
        nova.resize(server)
        print(f'Resize successful, remove server {server} from list')
        return True
    except Exception as e:
        print(f'Exception {e} resizing server "{server}"')
        return False


def confirm_shutoff_vm_resize(nova, shutoff_servers, max_retry_count=20):
    do_retry = True
    retry_count = 0
    while do_retry:
        sleep(5)
        shutoff_servers[:] = [server for server in shutoff_servers if not confirm_resize(nova, server)]
        retry_count += 1
        if not shutoff_servers or retry_count > max_retry_count:
            do_retry = False
        print('Once again')
        print(f'Current Servers list: {shutoff_servers}')


def get_quotas_dict_from_cinder_quotas(quotas):
    quotas_dict = {}
    volume_types_quotas = {}
    for quota in quotas:
        if quota.startswith(("gigabytes", "volumes", "snapshots")) and quota.find('_') > -1:
            quota_type = quota[quota.find('_') + 1:]
            quota_param = quota[:quota.find('_')]
            print(f'Found: {quota_type}, {quota_param}')
            if quota_type not in volume_types_quotas:
                volume_types_quotas[quota_type] = {}
                volume_types_quotas[quota_type]["volume_type"] = quota_type
            volume_types_quotas[quota_type][quota_param] = quotas[quota]
        else:
            quotas_dict[quota] = quotas[quota]
        print(f'volume_types_quotas: {volume_types_quotas}, \n quotas_dict: {quotas_dict}')
    quotas_dict["volume_types_quotas"] = list(volume_types_quotas.values())
    print(f'Finally, {quotas_dict}')
    return quotas_dict


if __name__ == '__main__':
    # servers_list = ['a', 'b', 'c', 'd', 'e']
    # get_status('Nova Test')
    # n = Nova()
    # confirm_shutoff_vm_resize(n, servers_list)
    quotas_cinder = {
        "gigabytes": 0,
        "volumes": 5,
        "snapshots": 11,
        "gigabytes___stand__": 1,
        "snapshots___stand__": 2,
        "volumes___stand__": 3,
        "gigabytes_opt": 1,
        "snapshots_opt": 2,
        "volumes_opt": 3,
    }
    get_quotas_dict_from_cinder_quotas(quotas_cinder)


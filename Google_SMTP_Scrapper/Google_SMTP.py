import ipaddress, dns.resolver, re
import numpy as np
import pandas as pd
from jinja2 import FileSystemLoader, Environment
from netmiko import ConnectHandler


def get_google_dns_blocks():
    # Dynamically parse the response from the Google subdomain that holds the public SMTP blocks
    response = dns.resolver.query('_spf.google.com', 'TXT').response.answer[0]

    reg_subdomain = r'include:(.[a-zA-Z]{1,}\d{,2}.google.com)'
    match_blocks = re.finditer(reg_subdomain, str(response))

    dns_netblocks = []
    for match in match_blocks:
        dns_netblocks.append(match[0][8:])

    return dns_netblocks


def parse_dns_reply(netblocks):
    # get the networks from the DNS TXT record and parse into a list
    # v6 regex adapted from David M. Syzdek: https://gist.github.com/syzdek/6086792
    regex_v4 = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/[1-3][0-9])'
    regex_v6 = r'''ip6:(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:
                    [0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:
                    [0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:
                    [0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:
                    (:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}
                    [0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}
                    [0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(\/\d{1,3})'''

    # queries netblock records, regex out network IDs (ipv4 and ipv6), append to a list, and save them off
    address_blocks = []
    for block in netblocks:
        answer = dns.resolver.query(block, 'TXT').response.answer[0]

        match_v4 = re.finditer(regex_v4, str(answer))
        match_v6 = re.finditer(regex_v6, str(answer))

        if match_v4 != None:
            for match in match_v4:
                address_blocks.append(ipaddress.ip_network(match.group(0)))

        if match_v6 != None:
            for match in match_v6:
                address_blocks.append(ipaddress.ip_network(match[0][4:]))

    return address_blocks


def saveNetworks(networks):
    # Save the networks scrapped from Google DNS records for future use and reference
    df = pd.DataFrame(np.array(networks),columns=['Public IPs'])
    df.to_csv('Current_Google_SMTP.csv', index=False)
    return 0


def createconfig(networks):
    # generates a list of the ACL statements needed to allow the public networks in
    config = []

    env = Environment(loader=FileSystemLoader('Google_SMTP_Scrapper/template'))
    tempv4 = env.get_template('ASA_Permit_Network_SMTP_v4')
    tempv6 = env.get_template('ASA_Permit_Network_SMTP_v6')

    for network in networks:
        if (network.version == 4):
            config.append(tempv4.render(network=network.network_address, netmask=network.netmask))
        else:
            config.append(tempv6.render(network=network))

    return config


def sendtodevice(config):
    # Connect to a device and publish the generated configuration
    testBox = {
        'device_type': 'cisco_asa_ssh',
        'host': '192.168.1.10',
        'username': 'user',
        'password': 'pass'
    }

    try:
        print('Connecting to the end point. Standby.')
        netConnect = ConnectHandler(**testBox)
        print('connected!')
    except:
        print('Cannot connect to end point.')
        return 0

    netConnect.send_config_set(config)
    netConnect.save_config()
    return 0


def main():
    netblocks = get_google_dns_blocks()
    address_blocks = parse_dns_reply(netblocks)
    saveNetworks(address_blocks)
    config = createconfig(address_blocks)
    sendtodevice(config)


if __name__ == '__main__':
    main()

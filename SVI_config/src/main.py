#!/usr/bin/env python

import csv
from netmiko import ConnectHandler

SWITCH_CREDS = {
    'device_type':'cisco_xe',
    'ip':'192.168.1.1',
    'username':'user',
    'password':'password!'
    }

# *** Helper functions***

def networkGateway(ip, netmask):
    # Get the network ID based on a given IP and netmask
    ip_split = [0]*4
    netmask_split = [0]*4
    network = [0]*4
    
    ip_split = ip.split('.')
    netmask_split = netmask.split('.')
    
    for ind in range(len(ip_split)):
        network[ind] = int(ip_split[ind]) & int(netmask_split[ind])
    
    network[3] = int(network[3])+1
    
    return '.'.join(str(idx) for idx in network)

def vlan(vlan):
    # 0 was used in some cases instead of simply 1 for the default vlan. Quick fix
    if (vlan == '1' or vlan == '0'):
        return '1'
    else:
        return vlan


def main():
    # import data
    config_commands = []

    # host.csv contains the raw data that is used. host_header file contains the schema of the file, along with data types
    with open('../hosts.csv', 'rb') as csvfile:
        siteData = csv.reader(csvfile, delimiter=',')
        for row in siteData:
            #parse data and generate config statements

            # CMIC
            cmicNetwork = networkGateway(row[12], row[11])
            config_commands.append('interface vlan ' + vlan(row[13]))
            config_commands.append('ip address ' + cmicNetwork + ' ' + row[11] + ' secondary')
            
            # MGMT
            vmotionNetwork = networkGateway(row[16], row[15])
            config_commands.append('interface vlan ' + vlan(row[17]))
            config_commands.append('ip address ' + vmotionNetwork + ' ' + row[15] + ' secondary')
            
            # vMotion
            vmotionNetwork = networkGateway(row[18], row[19])
            config_commands.append('interface vlan ' + vlan(row[20]))
            config_commands.append('ip address ' + vmotionNetwork + ' ' + row[19] + ' secondary')
            
            # vSAN
            if(row[23]!='N/A'):
                vsanNetwork = networkGateway(row[21], row[22])
                config_commands.append('interface vlan ' + vlan(row[23]))
                config_commands.append('ip address ' + vsanNetwork + ' ' + row[22] + ' secondary')
            
            
    # push to device or a backup txt file
    try:
        print('Logging into the switch...')
        net_connect = ConnectHandler(**SWITCH_CREDS)
        print('In!')
        
        try:
            print('Configuring the device...')
            output= net_connect.send_config_set(config_commands)
            print('configured!')
        except:
            print('something went wrong with configuring this thing')
            
    except:
        print('something went wrong, can\'t log in')
        # Dump config to text file for manual application
        output = '\n'.join(config_commands)
        fileConfig = open("config.txt", "w")
        fileConfig.write(output)
        fileConfig.close()
        print('dumped all the configuration to a text file instead. Good luck.')

main()
from netmiko import ConnectHandler
import sys
from UnitTesting.colors import *
import re

# ============= Start of test cases =============

NUM_OF_TEST = 3

def test1(netConnect):
    # deny = bad. It means BGP is getting dropped. Check the output of the packet tracer function for a deny, and if so
    # alert to it. Checks in both directions to ensure both endpoints can establish a peering session
    print("===== Test 1 =====")
    testNum = 1

    regex = r"^(Action: deny)$"
    output = netConnect.send_command("packet-tracer input inside tcp 10.2.2.1 65179 10.1.1.1 bgp")
    matches = re.finditer(regex,output,re.MULTILINE)

    for match in matches:
        if(match.group(1)!=regex):
            status(testNum, RED)
            return -1

    output = netConnect.send_command("packet-tracer input outside tcp 10.1.1.1 65179 10.2.2.1 bgp")
    matches = re.finditer(regex, output, re.MULTILINE)

    for match in matches:
        if (match.group(1) != regex):
            status(testNum, RED)
            return -1

    status(testNum, GREEN)
    return 0

def test2(netConnect):
    # Make sure our business app can still reach out to the internet on the intended port (TCP/3939 in thisn case)
    print("===== Test 2 =====")
    testNum = 2

    regex = r"^(Action: allow)$"
    output = netConnect.send_command("packet-tracer input inside tcp 192.168.1.10 65000 1.1.1.1 3939")
    matches = re.finditer(regex, output, re.MULTILINE)

    for match in matches:
        if (match.group(1) != regex):
            status(testNum, RED)
            return -1

    status(testNum, GREEN)
    return 0

def test3(netConnect):
    # Drop all SSH traffic along the data plane destined for the internal subnet.
    print("===== Test 3 =====")
    testNum = 3

    regex = r"^(Action: allow)$"
    output = netConnect.send_command("packet-tracer input inside tcp 1.1.1.1 65000 192.168.1.1 ssh")
    matches = re.finditer(regex, output, re.MULTILINE)

    for match in matches:
        if (match.group(1) != regex):
            status(testNum, RED)
            return -1

    status(testNum, GREEN)

    return 0

# ============= End of test cases =============

def status(testNum, color):
    # Will output a simple pass or fail to the console. Injects the test number and color codes the test to green
    # or red based on result. Helper function for unit test above.

    if (color==GREEN):
        sys.stdout.write(GREEN)
        print("Passed Test Case %d!" % testNum)
        sys.stdout.write(RESET)
    else:
        sys.stdout.write(RED)
        print("Failed Test Case %d!" % testNum)
        sys.stdout.write(RESET)

    return 0



def main():

    # Connect to ASA with given device creds
    testBox = {
        'device_type': 'cisco_asa_ssh',
        'host':   '192.168.1.1',
        'username': 'user',
        'password': 'pass'
    }

    try:
        print("Connecting to the end point. Standby.")
        netConnect = ConnectHandler(**testBox)
    except:
        print("Cannot connect to end point.")
        return 0

    # This will loop over all test functions that are defined above.
    for i in range(1, NUM_OF_TEST+1):
        globals()["test"+ str(i)](netConnect)

    return 0


if __name__== "__main__":
  main()
import os

if __name__ == "__main__":

    sc_dir = os.path.dirname(os.path.realpath(__file__)) + '/SecurityCenters'
    if not os.path.exists(sc_dir):
        os.makedirs(sc_dir)

    server = raw_input('\nEnter the DNS name of the Security Center you wish to add: ')

    # Check if the directory for that server is already there
    if os.path.isdir(sc_dir + '/' + server):
        print "\nYou have already added a Security Center with that name!\n"
        exit(0)

    # Getting the SC version
    version = 4
    while True:
        version = raw_input('\nEnter the version of the Security Center (4 or 5): ')
        if version == '4' or version == '5':
            break
        else:
            print '\nYou did not enter a 4 or 5, please try again!'

    # Add the file we need
    os.makedirs('SecurityCenters/' + server)
    with open(sc_dir + '/'+ server + '/securitycenter.txt', 'w') as sc_file:
        sc_file.write("server=" + server + "\n")
        sc_file.write("version=" + version)

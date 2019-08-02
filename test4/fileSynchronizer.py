#!/usr/bin/python3
#==============================================================================
#description     :This is a skeleton code for programming assignment 3
#usage           :python skeleton.py trackerIP trackerPort
#python_version  :3.5
#Authors         :Chenhe Li, Yongyong Wei, Rong Zheng
#==============================================================================

import socket, sys, threading, json,time,os,ssl
import os.path
import glob
import json
import optparse

#Validate the IP address of the correct format
def validate_ip(s):
    '''
    Arguments:
    s -- dot decimal IP address in string
    Returns:
    True if valid; False otherwise
    '''
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

# Validate the port number is in range [0,2^16 -1 ]
def validate_port(x):
    '''
    Arguments:
    x -- port number
    Returns:
    True if valid; False, otherwise
    '''
    if not x.isdigit():
        return False
    i = int(x)
    if i < 0 or i > 65535:
            return False
    return True

# Get file info in the local directory (subdirectories are ignored)
# Note: Exclude files with .so, .py, .dll suffixes
def get_file_info():

    

    '''
    Get file information in the current folder. which is used to construct the
    intial message as the instructions (exclude subfolder, you may also exclude *.py)

    Return: an array, with each element is {'name':filename,'mtime':mtime}
    i.e, [{'name':filename,'mtime':mtime},{'name':filename,'mtime':mtime},...]

    hint: use os.path.getmtime to get mtime, due to the fact mtime is handled
    differntly in different platform (ref: https://docs.python.org/2/library/os.path.html)
    here mtime should be rounded *down* to the closest integer. just use int(number)
    '''
    #YOUR CODE

    #files that are in the same directory as fileSynchronizer.py
    files_in_dir = (os.listdir('.'))
    #list of dictionaries of files that will be returned
    list_file = []
    for file in files_in_dir:
        filename = file
        #file extensions that will be excluded
        suffix=['.so', '.py', '.dll','.DS_Store']
        #if file doesn't have such extensions
        if not any(x in filename for x in suffix):
            #get the modification of the file
            modification_time = int(os.path.getmtime(filename))
            #create dictionary to store information
            file_dict ={}
            file_dict['name']=filename
            file_dict['mtime']=modification_time
            #append the dictionary to the list
            list_file.append(file_dict)
        
    #return the list of dictionaries of files
    return list_file

#Check if a port is available
def check_port_available(check_port):
    '''
    Arguments:
    check_port -- port number
    Returns:
    True if valid; False otherwise
    '''

    #if check_port is currently being used by system, return false otherwise true
    if str(check_port) in os.popen("netstat -na").read():
        return False
    return True

#Get the next available port by searching from initial_port to 2^16 - 1
#Hint: use check_port_avaliable() function
def get_next_available_port(initial_port):

    #maximum value specified in the instruction.pdf
    Maximum = 2**16
    #from initial_port to 2^16, return the port number if not being used
    for return_port in range (initial_port, Maximum):
        if(check_port_available(return_port)):
            return (return_port)
    #return false if all ports in the range are being used
    return False

class FileSynchronizer(threading.Thread):
    def __init__(self, trackerhost,trackerport,port, host='0.0.0.0'):

        threading.Thread.__init__(self)
        #Port for serving file requests
        self.port = port  #YOUR CODE
        self.host = host #YOUR CODE

        #Tracker IP/hostname and port
        self.trackerhost = trackerhost #YOUR CODE
        self.trackerport = trackerport #YOUR CODE

        self.BUFFER_SIZE = 8192

        #Create a TCP socket to commuicate with tracker
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #YOUR CODE
        self.client.settimeout(180)

        #Store the message to be sent to tracker. Initialize to Init message
        #that contains port number and local file info. (hint: json.dumps)

        #initial message containing port number and list of dictionaries of files.
        self.msg = {'port':self.port,'files':get_file_info()}#YOUR CODE
        #json.dumps to make it to dictionary.
        self.msg = json.dumps(self.msg)

        #Create a TCP socket to serve file requests.
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #YOUR CODE
        self.lock = threading.Lock()

        try:
            print("trying to conenct to host : "+ str(self.host)+" port : "+str(self.port))
            self.server.bind((self.host, self.port))
        except socket.error:
            print(('Bind failed %s' % (socket.error)))
            sys.exit()
        self.server.listen(10)

    # Not currently used. Ensure sockets are closed on disconnect
    def exit(self):
        self.server.close()

    #Handle file requests from a peer(i.e., send requested file content to peers)
    def process_message(self, conn,addr):
        '''
        Arguments:
        self -- self object
        conn -- socket object for an accepted connection from a peer
        addr -- address bound to the socket of the accepted connection
        '''


        #YOUR CODE
        #Step 1. read the file name contained in the request
        #Step 2. read the file from the local directory (assumming binary file <4MB)
        #Step 3. send the file to the requester
        #Note: use socket.settimeout to handle unexpected disconnection of a peer
        #or prolonged responses to file requests

        #times out when connection is stuck
        conn.settimeout(20)
        #wrapped in try because it gives error when connection is lost
        try:
            print(('Client connected with ' + addr[0] + ':' + str(addr[1])))
    
            
            #receiving data from a peer
            data = ''
            #receive file name from the peer
            while True:
                part = conn.recv(self.BUFFER_SIZE).decode('utf-8')
                data = data+part
                if len(part) < self.BUFFER_SIZE:
                    break
    
            print('requestd file data is : '+str(data))
    
            #open the file with options read and byte.
            f = open(data, 'rb')
            #read the contents of the file
            file_content = f.read()
            #close the file.
            f.close()
            
    
            print('sending file : '+data+' to : '+str(addr[1]))
    
            #send the content of file to peer, break it down to buffer size if it needs
            for i in range(0, len(file_content), self.BUFFER_SIZE):
                    end = min(i + self.BUFFER_SIZE, len(file_content))
                    #print('sending...')
                    #no need to encode it because the file is opened with byte option.
                    conn.sendall(file_content[i: end])
    
            print('done sending file')
            
        except (socket.timeout, socket.error, Exception) as e:
            print(str(e)+'from process_message of port : '+str(self.port))
            
        finally:
            #close conn since new conn, addr will be accepted for every new connection
            print('closing conn!')
            conn.close()

        

    def run(self):
        self.client.connect((self.trackerhost,self.trackerport))
        t = threading.Timer(5, self.sync)
        t.start()
        print(('Waiting for connections on port %s' % (self.port)))
        while True:
            conn, addr = self.server.accept()
            threading.Thread(target=self.process_message, args=(conn,addr)).start()

    #Send Init or KeepAlive message to tracker, handle directory response message
    #and  request files from peers
    def sync(self):
        print(('connect to:'+self.trackerhost,self.trackerport))
        #Step 1. send self.msg (when sync is called the first time, self.msg contains
        #the Init message. Later, in Step 4, it will be populated with a KeepAlive message)
        #YOUR CODE

        #sending the initial message with port number and list of dictionaries of files in current
        #directory. Breaking down to Buffer size if needed
        for i in range(0, len(self.msg), self.BUFFER_SIZE):
                    end = min(i + self.BUFFER_SIZE, len(self.msg))
                    #encode it to make it to byte
                    self.client.sendall(self.msg[i: end].encode('utf-8'))
        

        #Step 2. receive a directory response message from a tracker
        #initialize the directory_response_message
        directory_response_message = ''
        while True:
            #decode it to string
            part = self.client.recv(self.BUFFER_SIZE).decode('utf-8')
            directory_response_message = directory_response_message+part
            if len(part) < self.BUFFER_SIZE:
                break
        #json.loads to convert directory_response_message to dictionary                
        directory_response_message = json.loads(directory_response_message)



        #YOUR CODE

        #Step 3. parse the directory response message. If it contains new or
        #more up-to-date files, request the files from the respective peers and
        #set the modified time for the synced files to mtime of the respective file
        #in the directory response message (hint: using os.utime).

        #YOUR CODE

        #list of files in current directory
        files_in_dir = (os.listdir('.'))
        #dictionary of files that needs to be recieved from the peers
        files_to_update={}

        #for every file in the directory response message from the tracker
        for file in directory_response_message:
            #if file is not in current directory, add it to the files_to_update dictionary
            if file not in files_in_dir:
                files_to_update[file]=directory_response_message[file]
            #else compare the mtime of local file and mtime of incoming file, and if incoming
            #file is more recent, add it to the files_to_update dictionary
            else:
                local_mtime = int(os.path.getmtime(file))
                incoming_mtime = directory_response_message[file]['mtime']
                #if incoming if more recent than local file
                if (incoming_mtime > local_mtime):
                    files_to_update[file]=directory_response_message[file]

       


        #connect to peers

        #for every file in files_to_update
        for file in files_to_update:
            host = self.host
            #get the port number from the directory response message from tracker
            port = files_to_update[file]['port']
            #create a new socket to send file request, and receive file contents
            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #wrapped in try because when another peer disconnects, it gives an error
            try:
                #connect it to the socket that has the file that needs to be received
                peer.connect((host, port))
                print('connected to peer ip : '+str(host)+ ' port : '+str(port))
                #send the message (name of the file) to the peers, break it down to buffer size if it needs
                for i in range(0, len(file), self.BUFFER_SIZE):
                        end = min(i + self.BUFFER_SIZE, len(file))
                        #encode it to make it bytes
                        peer.send(file[i: end].encode('utf-8'))
    
                print('file requested : '+file)
    
                #initialize the byte variable
                received_file=b''
                #receive the bytes of requested file, breaking it down to buffer size if needed.
                while True:
                    part = peer.recv(self.BUFFER_SIZE)
                    #print('receiving...')
                    received_file = received_file+part
                    if len(part) < self.BUFFER_SIZE:
                        break
    
                #open the file with options to write and byte with file name that received.
                f = open(file, 'wb')
                #write received byte to file
                f.write(received_file)
                #close the file
                f.close()
    
                #setting the mtime of recieved file to mtime of the origin file
                os.utime (file, (-1, files_to_update[file]['mtime']))
            except (socket.error, Exception) as e:
                print(str(e)+'from sync of port : '+str(self.port))
                
            finally:
                #close the peer socket
                peer.close()
            





        #Step 4. construct a KeepAlive message (hint: json.dumps)
        #keepAlive message
        self.msg = {'port':self.port}#YOUR CODE
        self.msg = json.dumps(self.msg)

        #Step 5. start timer
        t = threading.Timer(5, self.sync)
        t.start()

if __name__ == '__main__':
    #parse command line arguments
    parser = optparse.OptionParser(usage="%prog ServerIP ServerPort")
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.error("No ServerIP and ServerPort")
    elif len(args) < 2:
        parser.error("No  ServerIP or ServerPort")
    else:
        if validate_ip(args[0]) and validate_port(args[1]):
            tracker_ip = args[0]
            tracker_port = int(args[1])

        else:
            parser.error("Invalid ServerIP or ServerPort")
    #get free port
    synchronizer_port = get_next_available_port(8000)
    synchronizer_thread = FileSynchronizer(tracker_ip,tracker_port,synchronizer_port)
    synchronizer_thread.start()

import socket, main, time, threading
import pickle
import colorama as color


color.init()

greenL = color.Fore.LIGHTGREEN_EX
yellowL = color.Fore.LIGHTYELLOW_EX
redL = color.Fore.LIGHTRED_EX
red = color.Fore.RED
white = color.Fore.WHITE

ip = None
port = None

users = []

tries = 0
maxTries = 5
maxSize = 10
user_amount = 0
headerSize = 7
bufferSize = 500
maxheaderSize = pow(10, headerSize-2) #100,000  10*10*10*10*10


def addServer():
    global ip, port
    print("Type the server's")
    while True:
        ip = input("ip>")
        port = input("port>")
        if ip == "": 
            print("IP cannot be blank\n")
        else:
            try: 
                port = int(port)
                if 0 <= port <= 65535:
                    print(f"\n---IP:    {ip}")
                    print(f"---PORT:  {port}\n")
                    break
                else:
                    print("Port must be between 0-65535\n")
            except ValueError:
                print("Port should only be a number\n")
    return ip, port


def create_server():
    global server, tries, ip, port
    # print(ip, port)
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((ip, port))
        server.listen(5)
        print("\nServer created!\n")
    except socket.error:
        tries += 1
        if tries >= maxTries:
            tries = 0
            print(redL + f"\nERROR: Server could not be created after {maxTries} tries!" + white)
            print("Possibly the IP or the port is wrong.\n")
            addServer()
            create_server()
            return
        print(redL + f"ERROR: Server could not be created!\n       Retrying...({tries})" + white)
        time.sleep(0.5)
        create_server()   


def remove_user(conn, address):
    global user_amount
    for user in users:
        if user[0] == [conn, address]:
            users.remove(user)
            main.remove_cam(conn)
            print(yellowL + f"\n{address} removed!" + white)
            conn.close()
            user_amount -= 1
            for user in Users:
                sendMessage(user[0], user[1], f"User {address[0]} left the server!", "yellowL")


def sendMessage(conn, address, msg, colorIndex):
    try:
        d = pickle.dumps([False, msg, colorIndex])
        conn.send(bytes(f"{len(d):<{headerSize}}", "utf-8") + d)
    except socket.error:
        print(red + "\nERROR: User, whom we are sending a message, does not exsist." + white)
        remove_user(conn, address)
        return


def sendInfo(conn, address): # 9,999,999
    while True:    
        try:
            length = int(conn.recv(headerSize))
            if length > maxheaderSize: 
                print(red + "\nERROR: User, we are receiving data from, has given faulty data size." + white); remove_user(conn, address)
            data = bytes("", "utf-8")
            while length > 0:
                data += conn.recv(bufferSize); length -= bufferSize
            mX, mY, cx, cy, key = pickle.loads(data)
            # print(mX, mY, cx, cy, key)
            info = main.main(conn, cx, cy, key)
            # print(info)
            main.camRotate(conn, mX, mY)
            # print(conn, " ", len(info))
            d = pickle.dumps([True, info])
            conn.send(bytes(f"{len(d):<{headerSize}}", "utf-8") + d)
        except ValueError:
            print(red + "\nERROR: User, we are receiving data from, does not exsist, or is giving faulty data." + white)
            remove_user(conn, address)
            return 


def start():
    global user_amount, maxSize
    main.start()
    # print("Noob")
    while True:
        conn, address = server.accept()
        if maxSize <= user_amount: 
            sendMessage(conn, address, "SERVER: Server is full!    Try again later.", "yellowL")
            conn.close()
        else:
            for user in users:
                sendMessage(user[0], user[1], f"SERVER: User {(conn, address)} joined the server!", "yellowL")
            users.append([conn, address])
            main.add_cam(conn)
            print(greenL + f"User {address} connected!" + white)
            sendMessage(conn, address, "Welcome to the server!", "greenL")
            threading.Thread(target=sendInfo, args=[conn, address]).start()
            user_amount += 1

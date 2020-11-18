import sys, time, threading
import main, server
from math import *


import socket
import time
import sys
import os
import pickle
import threading
import colorama as color

color.init()

green = color.Fore.GREEN
white = color.Fore.WHITE
red = color.Fore.RED
redL = color.Fore.LIGHTRED_EX
yellow = color.Fore.LIGHTYELLOW_EX

colors = {
    "white" : color.Fore.WHITE,
    "green" : color.Fore.GREEN,
    "greenL" : color.Fore.LIGHTGREEN_EX,
    "yellowL" : color.Fore.LIGHTYELLOW_EX,
    "red" : color.Fore.RED,
    "redL" : color.Fore.LIGHTRED_EX,
    "cyan" : color.Fore.CYAN,
    "blue" : color.Fore.BLUE,
    "blueL" : color.Fore.LIGHTBLUE_EX,
    "magenta" : color.Fore.MAGENTA,
    "magentaL" : color.Fore.LIGHTMAGENTA_EX,
}
#--------------------------------------------
ip = None # Add ip here (don't)? >=|
port = None

w, h = 300*3, 240*3; cx, cy = w//2, h//2
fps = 120
headerSize = 7
bufferSize = 500
#--------------------------------------------
#
i = 0
maxTries = 5
info = ()
loaded = True
pause = False


def render():
    screen.fill((0, 0, 0))
    # print(info)
    for i in info:
        if i[0] == 0: pygame.draw.circle(screen, i[1], i[2], 3)
        elif i[0] == 1: pygame.draw.line(screen, i[1], i[2], i[3], 1)
        elif i[0] == 2: pygame.draw.circle(screen, i[1], i[2], i[3])
    if pause: pygame.draw.rect(screen, (0, 255, 255), (cx-25, cy-25, 50, 50))
    pygame.display.update()


def addServer():
    global ip, port
    print("Type the server's ip\n")
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


def connect_to_server():
    global i
    global serverC
    try:
        serverC = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverC.connect((ip, port))
    except socket.error:
        i += 1
        if i >= maxTries:
            print(redL + f"\nERROR: Could not connect to server after {maxTries} tries!" + white)
            print("Possibly the IP or the port is wrong.\n" + white)
            addServer()
            connect_to_server()
        print(red + f"ERROR: Could not connect to server!\n       Retrying...({i})" + white)
        time.sleep(0.5)
        connect_to_server()


def new_info():
    global info, loaded
    while True:
        loaded = True
        length = int(serverC.recv(headerSize))
        data = bytes("", "utf-8")
        while length > 0:
            data += serverC.recv(bufferSize); length -= bufferSize
        d = pickle.loads(data)
        if d[0]: info = d[1]
        else: print(colors.get(d[2]) + d[1] + white)       


# while True:
#     addServer()
#     connect_to_server()

#     d = server.recv(1024)
#     msg, userColor = pickle.loads(d)
#     print(colors.get(userColor) + f"{msg}\n" + white)
#     if msg.find("-") != -1:
#         texts.append([colors.get(userColor) + msg + white, ""])
#         break

# messageTread = threading.Thread(target=new_message)
# messageTread.start()

# while True:
#     if queue == True:
#         time.sleep(0.1)
#     else:
#         user_input = input(">")
#         if len(user_input) > 1024:
#             print("\nMessage is too long!")
#         elif user_input == "":
#             pass
#         else:
#             server.send(bytes(user_input, "utf-8"))

# Select Singleplayer/Multiplayer
print("1 - Singleplayer\n2 - Multiplayer\n")
global option
while True:
    try:
        option = int(input(">"))
        if option == 1: 
            main.start()
            break
        elif option == 2:
            # Create or Join
            print("\n1 - Join Server\n2 - Create Server\n3 - Back\n") 
            while True:
                try:
                    option += int(input(">"))
                    if option == 3:
                        addServer()
                        connect_to_server()
                        threading.Thread(target=new_info).start()
                        break
                    elif option == 4:
                        ip, port = server.addServer()
                        server.create_server()  
                        threading.Thread(target=server.start).start()
                        connect_to_server()
                        threading.Thread(target=new_info).start()
                        break
                    elif option == 5: break
                    else: print("pls type a 1, 2 or 3. pls\n") 
                except ValueError: pass
            if option != 5: break
        else: print("pls type a 1 or 2. pls\n") 
    except ValueError: pass

if option == 1: main.add_cam("user")

import pygame

pygame.init()

screen = pygame.display.set_mode((w, h))
pygame.mouse.set_visible(False)
pygame.display.set_caption("3D Cube")
clock = pygame.time.Clock()

while True:
    clock.tick(fps)
    key = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if pause: 
                    pause = False; pygame.mouse.set_visible(False); pygame.mouse.set_pos(cx, cy)
                else: 
                    pause = True; pygame.mouse.set_visible(True)

    mX, mY = pygame.mouse.get_pos()
    if pause: mX, mY = cx, cy
    # print(mX, mY)
    # print(mX - cx, mY - cy
    if option == 1: 
        # t = time.time()
        info = main.main("user", cx, cy, key)
        main.camRotate("user", mX, mY)
        # print(time.time() - t)
    elif loaded:
        # print("Noob")
        loaded = False
        d = pickle.dumps([mX, mY, cx, cy, key])
        serverC.send(bytes(f"{len(d):<{headerSize}}", "utf-8") + d)
    if not pause: pygame.mouse.set_pos(cx, cy)
    render()
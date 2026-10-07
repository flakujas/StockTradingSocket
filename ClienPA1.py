import socket

HOST = 'localhost'
PORT = 7840

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

menu ="""
-------------------------------------------------------------------------
Stock Trading Terminal
-------------------------------------------------------------------------
Available commands:
Note: Please include spaces after each argument when entering commands!

>Buy Stocks: BUY <stock_symbol> <stock_amount> <price_per_stock> <user_id>
>Sell Stocks: SELL <stock_symbol> <stock_price> <stock_amount> <user_id>
>List All Stocks: LIST <user_id>
>Show Your Balance: BALANCE <user_id>
>Create New User: CREATE <first_name> <last_name> <user_name> <password> <account_balance>
>Quit Connection: QUIT
>Shutdown Server: SHUTDOWN
"""

print(menu)

while True:
    message = input("Enter a command: ")
    updatedMessage = message.split(" ")                 #delineates the message by the spaces
    command = updatedMessage[0].upper()                 #the first word is always the command
    arguments = updatedMessage[1:]                      #the rest of the message is the arguments

    if command.upper() == "BUY":                        #Buy Command: calcs the stock price and deducts from user balance
        if len(arguments) == 4:                         #Buy command requires 4 arguments: stock_symbol, stock_amount, price per stock, user id
              client_socket.sendall(message.encode())
        else:                                           #An invalid number (not 4) of arguments was received, try again
            print("Invalid number of arguments for buy command, please try again.")
            continue

    elif command.upper() == "SELL":                     #Sell Command: sell stocks and deposit price into user balance
        if len(arguments) == 4:                         #Sell command requires 4 arguments: stock_symbol, stock price, stock_amount, user id
              client_socket.sendall(message.encode())
        else:                                           #An invalid (not 4) number of arguments was received, try again
            print("Invalid number of arguments for sell command, please try again.")
            continue

    elif command.upper() == "LIST":                     #List Command: list all records in the stocks table
        if len(arguments) == 1:
            client_socket.sendall(message.encode())
        else:                                           #A nonzero number of arguments was received, try again
            print("Invalid number of arguments for list command, please try again.")
            continue

    elif command.upper() == "BALANCE":                  #Balance Command: show user 1's balance
        if len(arguments) == 1:
            client_socket.sendall(message.encode())
        else:                                           #A nonzero number of arguments was received, try again
            print("Invalid number of arguments for balance command, please try again.")
            continue

    elif command.upper() == "CREATE":                   #Create Command: create a new user with the necessary db fields
        if len(arguments) == 5:
            client_socket.sendall(message.encode())
        else:
            print("Invalid information to create a new user, please try again.")
            continue
        
    elif command.upper() == "SHUTDOWN":                 #Shutdown Command: shutdown the server, close all open sockets & database
        print("Full shutdown in progress...")
        break

    elif command.upper() == "QUIT":                     #Quit Command: terminate only the client connection
        print("Quitting your connection to the server...")
        break

    else:                                               #Invalid Command: Command has not been recognized, prompt user to try again
        print("Invalid command, please try again.")
        continue

    data = client_socket.recv(1024)
    print("RECEIVED:", data.decode())
client_socket.close()


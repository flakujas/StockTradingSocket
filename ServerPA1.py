import socket
import sqlite3


HOST = 'localhost'
PORT = 7840

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind((HOST, PORT))
serversocket.listen(1)

# Open database
conn = sqlite3.connect("user.db")
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users
    (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT,
    user_name TEXT NOT NULL,
    password TEXT,
    usd_balance DOUBLE NOT NULL
    );
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Stocks
    (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_symbol VARCHAR(4) NOT NULL,
    stock_name VARCHAR(20) NOT NULL,
    stock_balance DOUBLE,
    user_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES Users (ID)
    );
''')

conn.commit()

# Check if at least one user exists
cursor.execute("SELECT COUNT(*) FROM Users;")
count = cursor.fetchone()[0]

#If no users exist, creates a default user with 100 USD balance and stocks
if count == 0:
    cursor.execute("""
        INSERT INTO Users (first_name, last_name, user_name, password, usd_balance)
        VALUES ('User_First', 'User_Last', 'User', '000', 100.00);
    """)
    conn.commit()
    print("Default user created.")
else:
    print("User(s) already exist.")

# Create stocks
cursor.execute("SELECT COUNT(*) FROM Stocks;")
stock_count = cursor.fetchone()[0]

if stock_count == 0:
    cursor.execute("""
        INSERT INTO Stocks (stock_symbol, stock_name, stock_balance, user_id) VALUES
        ('AAPL', 'Apple Inc', 10.5, 1),
        ('MSFT', 'Microsoft Corp', 8.0, 1),
        ('GOOG', 'Alphabet Inc', 12.3, 1),
        ('TSLA', 'Tesla Inc', 6.7, 1),
        ('AMZN', 'Amazon.com Inc', 4.2, 1);
    """)
    conn.commit()
    print("Default stocks inserted.")
else:
    print("Stocks already exist.")

# Print users
cursor = conn.execute("Select ID, first_name, last_name, user_name, password, usd_balance from Users")

#If needed: Display all users in the database
"""
for row in cursor:
   print ("ID = ", row[0])
   print ("FIRST NAME = ", row[1])
   print ("LAST NAME = ", row[2])
   print ("USER NAME = ", row[3])
   print ("PASSWORD = ", row[4])
   print ("USD BALANCE = ", row[5], "\n")"""

# Command functions
# create a custom user------------------------------------------------------------------------
def create_user(first_name, last_name, user_name, password, usd_balance):
    cursor.execute("""SELECT user_name FROM Users WHERE user_name=?""", (user_name,))
    result = cursor.fetchone()
    
    if result is not None:
        return "Username already exists. Please try again with a different User Name."
    else:
        cursor.execute("""
        INSERT INTO Users (first_name, last_name, user_name, password, usd_balance)
        VALUES (?, ?, ?, ?, ?);
    """, (first_name, last_name, user_name, password, usd_balance))
        conn.commit()
        return "User created successfully."
        

# Balance
def balance(user_id):
    # Select user info from specific user
    cursor.execute("SELECT first_name, last_name, usd_balance From Users WHERE ID=?", (user_id,))
    user = cursor.fetchone() # This will be our current users data
    # Display balance
    if user:
        return f"200 OK\nBalance for {user[0]} {user[1]}: ${user[2]:.2f}"
    else:
        return "User does not exist"

# Stock list
def list_stocks(user_id):
    # Get stock info (ID, symbol, and balance)
    cursor.execute("SELECT ID, stock_symbol, stock_balance FROM Stocks WHERE user_id=?", (user_id,))
    stocks = cursor.fetchall() # This will fetch ALL stocks and their data
    if not stocks:
        return "200OK\nNo Stocks found"
    # Display all stocks
    response = "200OK\nStocks:\n"
    for i in stocks:
        response += f"{i[0]} {i[1]} {i[2]}\n"
    return response.strip()

# Buy
def buy(symbol, amount, price, user_id):
    # Get users balance
    cursor.execute("SELECT usd_balance FROM Users WHERE ID=?",(user_id,))
    user = cursor.fetchone()
    if not user:
        return "User does not exist"

    # Calculate cost
    total_cost = amount * price
    if user[0] < total_cost:
        return "Balance too low"

    # Update balance
    new_balance = user[0] - total_cost
    cursor.execute("UPDATE Users SET usd_balance=? WHERE ID=?", (new_balance, user_id))
    
    # Update stock information
    cursor.execute("SELECT stock_balance FROM Stocks WHERE user_id=? AND stock_symbol=?", (user_id, symbol))
    stock = cursor.fetchone()

    # Update stocks if exists else make new balance
    if stock:
        new_stock_balance = stock[0] + amount
        cursor.execute("UPDATE Stocks SET stock_balance=? WHERE user_id=? AND stock_symbol=?",(new_stock_balance,user_id,symbol))
    else:
        cursor.execute("Insert Into Stocks (stock_symbol, stock_name, stock_balance, user_id) VALUES (?, ?, ?, ?)", (symbol, symbol, amount, user_id))
    conn.commit()
    return f"200 OK\nBOUGHT: {amount} {symbol}. USD balance ${new_balance:.2f}"

def sell (symbol, price, amount, user_id):
    # Get users balance
    cursor.execute("SELECT usd_balance FROM Users WHERE ID=?",(user_id,))
    user = cursor.fetchone()
    if not user:
        return "User does not exist"

    # Get stocks to sell
    cursor.execute("SELECT stock_balance FROM Stocks WHERE user_id=? AND stock_symbol=?", (user_id, symbol))
    stock = cursor.fetchone()
    if not stock or stock[0] < amount:
        return f"Not enough {symbol} stock balance"
    
    # Subtract stock
    new_stock_balance = stock[0] - amount
    cursor.execute("UPDATE Stocks SET stock_balance=? WHERE user_id=? AND stock_symbol=?",(new_stock_balance, user_id,symbol))

    # Add USD to user
    new_balance = user[0] + (amount * price)
    cursor.execute("UPDATE Users SET usd_balance=? WHERE ID=?", (new_balance, user_id))
    conn.commit()
    return f"200 OK\nSOLD: {amount} {symbol}. USD balance: ${new_balance:.2f}"


# Server loop

print("Server is running...")

while True:
    connection, address = serversocket.accept()
    print("Connected by", address)

    while True:
        data = connection.recv(1024)
        if not data:
            break

        message = data.decode().strip()
        parts = message.split()
        if not parts:
            continue

        command = parts[0].upper()
        response = "Invalid command"

        print("Received command: ", command)
        if command == "BALANCE":
                if len(parts) == 2:
                    user_id = int(parts[1])
                    response = balance(user_id)
                else:
                    response = "ERROR: BALANCE <user_id>"

        elif command =="LIST":
                if len(parts) == 2:
                    user_id = int(parts[1])
                    response = list_stocks(user_id)
                else:
                    response = "ERROR: LIST <user_id>"

        elif command == "BUY":
                if len(parts) == 5:
                    user_id = int(parts[4])
                    symbol = parts[1].upper()
                    amount = float(parts[2])
                    price = float(parts[3])
                    response = buy(symbol, amount, price, user_id)
                else:
                    response = "ERROR: BUY <user_id> <symbol> <amount> <price>"

        elif command  == "SELL":
                if len(parts) == 5:
                    user_id = int(parts[4])
                    symbol = parts[1].upper()
                    price = float(parts[2])
                    amount = float(parts[3])
                    response = sell(symbol, price, amount, user_id)
                else:
                    response = "ERROR: SELL <user_id> <symbol> <amount> <price>"

        elif command == "QUIT":
                response  ="200 OK\nA user has disconnected..."
                connection.sendall(response.encode())
                break


        elif command == "SHUTDOWN":
                response = "200 OK\nShutting down server..."
                connection.sendall(response.encode())
                connection.close()
                serversocket.close()
                conn.close()
                exit(0)
            #--------------------------------------------------------------------------------
        elif command == "CREATE":
                if len(parts) == 6:
                    first_name = parts[1]
                    last_name = parts[2]
                    user_name = parts[3]
                    password = parts[4]
                    usd_balance = float(parts[5])
                    response = create_user(first_name, last_name, user_name, password, usd_balance)
                else:
                    print("ERROR: CREATE <first_name> <last_name> <user_name> <password> <account_balance>")
        else:
                response = "400 Unknown command"

        connection.sendall(response.encode())

    connection.close()
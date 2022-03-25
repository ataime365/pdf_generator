import sqlite3
import random
from fpdf import FPDF
import os

class Buy:
    
    def __init__(self):
        pass
    
    def buy_seat(self, seat, card, full_name, seat_id, ticket_id):
        if seat.seat_is_free(): #This gets the price
            seat_price = seat.price #class variable
            if card.checking_card_details():
                if card.deductions(seat_price): #we check that the deduction has occured(is True) before changing the seat from 0 to 1(taken)
                    seat.after_seat_purchase()
                    ticket = Ticket(full_name, seat_price, seat_id, ticket_id)
                    ticket.generate(full_name+ ' ' +ticket_id+ ' ' +'_ticket.pdf')
                    return "Purchase Successful"
            else:
                return "Problem with your card"
        else:
            return "Seat is taken"


class Seat:
    database='cinema.db'
    
    price = 0
    def __init__(self, seat_chosen):
        self.seat_chosen = seat_chosen
        
    def seat_is_free(self):
        conn = sqlite3.connect(self.database) #Creates the database if none
        cur = conn.cursor()
        cur.execute("SELECT taken FROM Seat WHERE seat_id=? ", (self.seat_chosen,)) 
        taken_chosen_seat_d = cur.fetchall()[0][0] #To fetch the data from the cursor
        
        if taken_chosen_seat_d ==0:
            cur.execute("SELECT price FROM Seat WHERE seat_id=? ", (self.seat_chosen,))
            price_from_database = cur.fetchall()[0][0]
            self.price = self.price + price_from_database
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    def after_seat_purchase(self):
        conn = sqlite3.connect(self.database) #Creates the database if none
        cur = conn.cursor()
        cur.execute("UPDATE Seat SET taken = ? WHERE seat_id = ?", (1, self.seat_chosen)) 
        conn.commit()
        conn.close()
        return True

        
class Card:
    database='banking.db'
    card_balance = 0
    
    def __init__(self, card_type, card_no, cvc, card_holders_name):
        self.card_type = card_type
        self.card_no = card_no
        self.cvc = cvc
        self.card_holders_name = card_holders_name
        
    def checking_card_details(self):
        conn = sqlite3.connect(self.database) #Creates the database if none
        cur = conn.cursor()
        cur.execute("SELECT number FROM Card") 
        nums = cur.fetchall()
        nums_li = [num[0] for num in nums]
        
        if self.card_no in nums_li:
            cur.execute("SELECT * FROM Card WHERE number=?", (self.card_no,))
            card = cur.fetchall()[0]
            if self.card_type == card[0] and self.card_no == card[1] and self.cvc == card[2] and self.card_holders_name==card[3]:
                self.card_balance = self.card_balance + card[4]
                return True
            else:
                return False 
        conn.close()

    def deductions(self, seat_price):
        if type(seat_price) == float:
            new_bal = self.card_balance - seat_price
            conn = sqlite3.connect(self.database) #Creates the database if none
            cur = conn.cursor()
            cur.execute("UPDATE Card SET balance = ? WHERE number = ?", (new_bal, self.card_no)) 
            conn.commit()
            conn.close()
            return True
        else:
            return False
            
class Ticket:
    """
    Creates a pdf file that contains data about the flatmates,
    such as their names, their due amount and the period of the bill.
    """
    
    def __init__(self, full_name, price, seat_number, ticket_id):
        self.full_name = full_name
        self.price = price
        self.seat_number = seat_number
        self.ticket_id = ticket_id
        
    def generate(self, filename):
        pdf = FPDF(orientation='P', unit='pt', format='A4') #Default (orientation='P', unit='mm', format='A4')
        pdf.add_page()
        # title
        pdf.set_font(family='Times', style= 'B', size=24) #B means Bold
        pdf.cell(w=0, h=80, txt="Ticket", border=0, align="C", ln=1) #"C" means center
        #w and h are in pt units as defined in the FPDF, ln=1 takes it to the next line, if not, it will just be in front of it
        pdf.set_font(family='Times', size=18)
        pdf.cell(w=150, h=40, txt="Full Name: ", border=0)
        pdf.cell(w=150, h=40, txt=self.full_name , border=0, ln=1)
        pdf.cell(w=150, h=40, txt="Price: ", border=0)
        pdf.cell(w=150, h=40, txt=str(self.price) , border=0, ln=1)
        pdf.cell(w=150, h=40, txt="Seat Number: ", border=0)
        pdf.cell(w=150, h=40, txt=self.seat_number , border=0, ln=1)
        pdf.cell(w=150, h=40, txt="Ticket ID ", border=0)
        pdf.cell(w=150, h=40, txt=self.ticket_id , border=0, ln=1)
        # This is the only part that changes, and it would be saved in the files directory
        os.chdir("files") #This changes the working directory to 'files' while the python code is still running
        pdf.output(filename)
        
if __name__ =="__main__":
    
    full_name = 'Marry Smith'
    seat_id = 'A1'
    card_holders_name = full_name
    characters = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ123456789"
    ticket_id = ''
    for a in range(8):
        ticket_id = ticket_id + random.choice(characters)
    ticket_id = ticket_id

    seat = Seat(seat_id)
    card = Card('Master Card', '23456789', '234', card_holders_name)
    
    buy = Buy().buy_seat(seat, card, full_name, seat_id, ticket_id)
    print(buy)
 
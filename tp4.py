import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import random

GUI_TITLE = 'Kafe Daun-Daun Pacilkom v2.0 🌿'

'''
    Pembuatan class database untuk menyimpan data yang digunakan seperti data meja dan menu.
    Penyimpanan meja = [['<nama>', [0, 2, 3, 4, 5, 5], <jumlah> ], [], ..., [<meja 9>]]
    Penyimpanan menu = [[<jenis>, <kode>, <nama>, <harga>, <info tambahan>], ...]
'''
class Database(object):
    def __init__(self):
        self.__tables = [[] for _ in range(10)]
        self.__menu_items = []
    def add_item(self, item: list):
        self.__menu_items.append(item)
    def set_table(self, table_num: int, table_data: list):
        self.__tables[table_num] = table_data
    def get_tables(self):
        return self.__tables
    def get_items(self):
        return self.__menu_items
db = Database()

'''
    Class untuk membuat master dari semua window, menunjukkan opsi untuk buat pesanan atau selesaikan pesanan.
'''
class Main(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master.geometry('400x200')
        self.master.title(GUI_TITLE)
        self.pack()
        self.create_widgets()
    def create_widgets(self):
        tk.Button(self, text='Buat Pesanan', width=30, bg='#4472C4', fg='white', command=self.create).grid(row=0, column=0, pady=40)
        tk.Button(self, text='Selesai Menggunakan Meja', width=30, bg='#4472C4', fg='white', command=self.finish).grid(row=1, column=0)
    def create(self):
        CustomerOrder(self.master) if [] in db.get_tables() else\
            messagebox.showwarning(title='Oh tidak!', message='Mohon maaf, meja sedang penuh. Silakan datang kembali di lain kesempatan.')
    def finish(self):
        FinishOrder() if db.get_tables().count([]) != 10 else\
            messagebox.showwarning(title='Oh tidak!', message='Tidak ada meja yang sedang dipakai!')

'''
    Class untuk mengambil nama dari pelanggan, lalu meneruskannya ke class window selanjutnya.
'''
class CustomerOrder(tk.Frame):
    def __init__(self, master):
        self.main_window = tk.Toplevel(master)
        self.main_window.grab_set()
        self.main_window.title(GUI_TITLE)
        self.main_window.geometry('400x200')
        self.name_input = tk.StringVar()
        self.create_widgets()
    def create_widgets(self):
        tk.Label(self.main_window, text='Siapa nama Anda?').grid(column=0, row=0, pady=75, padx=(90, 5))
        tk.Entry(self.main_window, text=self.name_input).grid(column=1, row=0, padx=10)
        tk.Button(self.main_window, text='Kembali', width=20, command=self.main_window.destroy)\
            .grid(column=0, row=1, sticky=tk.E, padx=(0, 5))
        tk.Button(self.main_window, text='Lanjut', width=20, command=lambda: self.create_order(self.name_input.get()))\
            .grid(column=1, row=1, sticky=tk.W, padx=(5, 0))
    def create_order(self, name):
        CreateOrder(name) if name != '' else\
            messagebox.showwarning(title='Oh tidak!', message='Nama tidak boleh kosong!')
        self.main_window.destroy()

'''
    Utility class untuk menyimpan method yang diperlukan untuk class membuat order dan menyelesaikan order. Diantaranya ada:
    1. display tables, untuk mengatur penampilan page penampilan tabel, menyesuaikan dengan apakah sedang membuat atau menyelesaikan order
    2. display picker, untuk mengatur penampilan page memilih meja, menyesuaikan dengan apakah sedang membuat atau menyelesaikan order
    3. change table, utility method untuk picker, agar picker dapat mengubah meja yang dipilih
    4. table finder, untuk pemilihan meja secara random
    5. update price, untuk memperbarui tampilan harga setiap kali jumlah barang di combobox diubah
    6. submit order, untuk memperbarui data meja di database
    7. create tables, untuk membuat tabel lalu hasilnya dimasukkan ke dalam display tables
    8. create picker, untuk membuat picker, lalu hasilnya dimasukkan ke dalam display picker
'''
class OrderHandler(tk.Frame):
    def __init__(self, values=[], bill=0):
        self.values = values if values != [] else [tk.IntVar(value=0) for _ in range(len(db.get_items()))]
        self.bill = bill
    def display_tables(self, window, mode: str):
        window.grab_set()
        window.geometry('690x420')
        name_label = tk.Label(window, text=f'Nama pemesan: {self.name}')
        table_num_label = tk.Label(window, text=f'No meja: {self.table_num}')
        bill_label = tk.Label(window, text=f'Total harga: {self.bill}', font=(10, 10, 'bold'))
        name_label.grid(column=0, row=0)
        table_num_label.grid(column=6, row=0)
        start_row = self.create_tables(window, bill_label, db.get_items(), self.values, mode) + 1
        bill_label.grid(column=6, row=start_row, sticky=tk.E+tk.W, columnspan=2)
        tk.Button(window, text='Kembali', command=window.destroy, width=15).grid(column=1, row=start_row+1, pady=25, columnspan=2)
        if mode == 'order':
            tk.Button(window, text=f'Ubah Meja', 
                command=lambda: self.display_picker(tk.Toplevel(window), table_num_label, db.get_tables(), 'order')).grid(column=7, row=0)
            tk.Button(window, text='Lanjut', width=15,
                command=lambda: self.submit_order(self.values, self.table_num))\
                    .grid(column=3, row=start_row+1, columnspan=3)
        elif mode == 'finish':
            tk.Button(window, text='Selesai', width=15,
                command=lambda: self.finish_order(self.table_num, self.main_window))\
                    .grid(column=3, row=start_row+1, columnspan=3)
    def display_picker(self, window, table_num_label, table_list: list, mode: str):
        window.grab_set()
        window.geometry('260x420')
        info = tk.Label(window)
        info['text'] = 'Silakan klik meja kosong yang diinginkan' if mode == 'order' else 'Silakan klik meja yang selesai digunakan.'
        info.grid(columnspan=3, sticky=tk.E+tk.W, pady=(20, 10))
        start_row = self.create_picker(window, table_list, mode, table_num_label, 1) + 1
        tk.Label(window, text='Info mengenai warna:', font=(10, 10, 'bold')).grid(column=0, row=start_row, columnspan=2, pady=(20, 0))
        info_colors = {'red': 'Ditempati', 'gray': 'Kosong', 'blue': 'Anda'}
        for i, color in enumerate(info_colors):
            if mode == 'finish' and color == 'blue': continue
            tk.Label(window, text=info_colors[color], bg=color, fg='white', width=20).grid(column=0, row=start_row+i+1, columnspan=2, pady=5)
        tk.Button(window, text='Kembali', width=20, command=window.destroy).grid(column=0, row=start_row+4, columnspan=2, pady=(20, 0))
    def table_finder(self, table_list: list):
        while True:
            table_num = random.randint(0, 9)
            if table_list[table_num] == []:
                return table_num
    def create_tables(self, window, label, menu: list, values: list, mode:str ='order', row=3, col=0):
        menu_num = 0
        previous = ''
        for item in menu:
            current = item[0]
            if current != previous:
                category_label = tk.Label(window, text=current)
                category_label.grid(column=0, row=row)
                previous, row = current, row + 1
                col = 0
                col_names = ['Kode', 'Nama', 'Harga', {'MEALS': 'Kegurihan', 'DRINKS': 'Kemanisan', 'SIDES': 'Keviralan'}, 'Jumlah']
                for col, column in enumerate(col_names):
                    entry = tk.Entry(window, width=20, bg='white')
                    entry.grid(column=col+2, row=row, columnspan=2) if column == 'Jumlah' else entry.grid(column=col, row=row)
                    entry.insert(tk.END, column) if len(column) != 3 else entry.insert(tk.END, column[current])
                    entry['state'] = 'readonly'
                row += 1
            col = 0
            for data in item:
                if data == item[0]: continue
                entry = tk.Entry(window, width=20, bg='white')
                entry.grid(column=col, row=row)
                entry.insert(tk.END, data)
                entry['state'] = 'readonly'
                col += 1
            if mode == 'order':
                item_total = ttk.Combobox(window, textvariable=values[menu_num], state='readonly')
                item_total['values'] = tuple([k for k in range(10)])
                item_total.bind('<<ComboboxSelected>>', lambda item = item: self.update_price(values, label))
                item_total.grid(row=row, column=6, columnspan=2)
            else:
                entry = tk.Entry(window, width=20, bg='white')
                entry.grid(row=row, column=6, columnspan=2)
                entry.insert(tk.END, values[menu_num])
                entry['state'] = 'readonly'
            row += 1
            menu_num += 1
        return row
    def create_picker(self, window, table_list: list, mode: str, label=None, row=0):
        for num, table in enumerate(table_list):
            table_button = tk.Button(window, text=num, fg='white', disabledforeground='white', width=15)
            if mode == 'order':
                table_button['command'] = lambda num=num: self.change_table(window, num, label)
            else:
                table_button['command'] = lambda num=num: self.set_customer(window, table_list, num)
            if mode == 'order' and num == self.table_num:
                table_button['bg'] = 'blue'
                table_button['state'] = 'disabled'
            elif table == []:
                table_button['bg'] = 'gray'
                if mode != 'order': table_button['state'] = 'disabled'
            else:
                table_button['bg'] = 'red'
                if mode == 'order': table_button['state'] = 'disabled'
            if num % 2 == 0:
                table_button.grid(row=row, column=0, padx=(10, 5), pady=5)
            else:
                table_button.grid(row=row, column=1, padx=(5, 10), pady=5)
                row += 1
        return row

'''
    Class untuk membuat pesanan, cukup pendek karena inherit method dari OrderHandler.
    Semuanya sudah diatur dalam kondisional OrderHandler dengan method tersendiri
    seperti change table untuk mengubah meja, update price untuk memperbarui harga
    setelah mengubah jumlah, dan submit order untuk mengumpulkan orderan ke database.
'''
class CreateOrder(OrderHandler):
    def __init__(self, name, values=[], bill=0):
        super().__init__(values, bill)
        self.main_window = tk.Toplevel()
        self.name = name
        self.table_num = self.table_finder(db.get_tables())
        self.display_tables(self.main_window, mode='order')
    def change_table(self, window, table_num, label):
        self.table_num = table_num
        label['text'] = f'No meja: {table_num}'
        window.destroy()
    def update_price(self, values: list, label):
        self.bill = 0
        for amount, data in zip(values, db.get_items()):
            price = data[3]
            self.bill += amount.get() * int(price)
        label['text'] = f'Total harga: {self.bill}'
    def submit_order(self, values: list, table_num: int):
        if max([value.get() for value in values]) == 0:
            messagebox.showwarning(title='Oh tidak!', message='Tolong setidaknya pesan satu makanan!')
        else:
            db.set_table(table_num, [self.name, values, self.bill])
            self.main_window.destroy()
            messagebox.showinfo(title='Berhasil!', message=f'Berhasil memesan atas nama {self.name} di meja {self.table_num}')


'''
    Class untuk membuat pesanan, cukup pendek karena inherit method dari OrderHandler.
    Semuanya sudah diatur dalam kondisional OrderHandler dengam  method tersendiri seperti 
    set customer untuk mengambil data pelanggan ketika nomor meja yang dimiliki pelanggan 
    dipencet, dan juga finish order untuk mengosongkan meja setelah meja selesai digunakan.
'''
class FinishOrder(OrderHandler):
    def __init__(self):
        self.main_window = tk.Toplevel()
        self.display_picker(self.main_window, None, db.get_tables(), 'finish')
    def set_customer(self, window, tables, table_num):
        self.table_num = table_num
        self.name, self.values, self.bill = tables[table_num]
        self.values = [value.get() for value in self.values]
        self.display_tables(tk.Toplevel(window), 'finish')
    def finish_order(self, table_num, window):
        db.set_table(table_num, [])
        window.destroy()
        messagebox.showinfo(title='Berhasil!', message='Berhasil menyelesaikan pesanan!')

'''
    Pengambilan data dari menu.txt dengan memperhatikan 3 karakter awal. Jika ketiganya merupakan '=',
    maka akan dianggap sebagai kategori. Kategori berdasarkan file TP4 hanya ada 3, yaitu MEALS, DRINKS, dan SIDES.
    Setiap line akan displit dan akan masuk dalam variabel code, name, price, info lalu dimasukkan ke dalam object db.
'''
def main():
    with open('menu.txt', 'r') as f:
        lines = f.read().splitlines()
    for line in lines:
        if line[:3] == '===':
            current = line[3:]
        else:
            code, name, price, info = line.split(';')
            db.add_item([current, code, name, price, info])
    window = tk.Tk()
    cafe = Main(window)
    window.mainloop()

if __name__ == '__main__':
    main()
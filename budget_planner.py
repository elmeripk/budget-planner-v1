"""
COMP.CS.100 Ohjelmointi 1
Elmeri Pohjois-Koivisto, elmeri.pohjois-koivisto@tuni.fi, opiskelijanumero 150194031.
A program which can be used to manage a budget. The program uses a csv file to
store and write data and this way a deeper analysis can be conducted using a
spreadsheet application. A user can add and remove categories and events and
the changes are reflected both in the file and the UI.
"""

import getpass
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from csv import writer, reader
from ast import literal_eval

class file_selection_menu:
    """
    Class for the file selection menu.
    """
    def __init__(self):
        """
        This function creates the file selection window,
        where user can choose to open an existing
        file or create a new one.
        """
        self.__file_selection_main_window = Tk()
        self.__file_selection_main_window.geometry("600x500")
        #Creates a new frame which to pack the content for better alignment
        self.__new_file_selection_frame = Frame(self.__file_selection_main_window)
        self.__label_open_file = Label(self.__new_file_selection_frame,
                                       text="Open an exising file by clicking here. "
                                            "If you do not have a file created with " 
                                            "this application before, please create a "
                                            "new file. Otherwise the program won't work.",
                                       wraplength=200, borderwidth=1,
                                       relief="solid", width=35, height=8)

        self.__label_create_file = Label(self.__new_file_selection_frame,
                                         text="Create a new file by entering the filename "
                                              "below and clicking here. Beware that if a file"
                                              " of the same name exists already, it is cleared. The "
                                              "file is stored in the same directory as this program.",
                                         wraplength=200, borderwidth=1, relief="solid",
                                         width=35, height=8)

        self.__ask_file = Button(self.__new_file_selection_frame, text="Select a file",
                                 command=self.open_file)

        self.__greeting = Label(self.__file_selection_main_window, font='Arial 25 bold')
        self.__sub_greeting = Label(self.__file_selection_main_window,
                                    text="Welcome to use this budget management software!",
                                    font='Arial 16 bold')
        self.__create_file_button = Button(self.__new_file_selection_frame, text="Create a new file",
                                           command=self.create_file)
        self.__filename = Entry(self.__new_file_selection_frame)

        self.__new_file_selection_frame.grid_columnconfigure(0, weight=1)
        self.__new_file_selection_frame.grid_columnconfigure(1, weight=1)

        self.__greeting.pack(fill="x")
        self.__sub_greeting.pack(fill="x")
        self.__new_file_selection_frame.pack(fill=BOTH)
        self.__label_open_file.grid(row=0, column=0, pady=5, padx=5)
        self.__label_create_file.grid(row=0, column=1, pady=5, padx=5)
        self.__ask_file.grid(row=1, column=0)
        self.__create_file_button.grid(row=1, column=1)
        self.__filename.grid(row=2, column=1, pady=5, padx=5)

        self.get_current_date()

        self.__file_selection_main_window.mainloop()

    #If file doesn't exist:
    def create_file(self):
        """
        Creates a new budget managing template (csv-file) and opens it in
        reading and writing mode. Raises OSError if the opening fails.
        Passes the file onwards to store_file_content which handles the
        reading and writing of the file.

        :return: None
        """
        file_name = self.__filename.get()
        if file_name == "":
            self.__box = messagebox.showwarning("Error", "The name can't be empty")
            return
        file_name = f"{file_name}.csv"
        try:
            file = open(file_name, "w+", newline='', encoding='utf-8')
            store_file_content(file, self.__file_selection_main_window)
        except OSError:
            self.__box = messagebox.showwarning("Error", "Opening of the file failed")

    def open_file(self):
        """
        Opens a user given file in reading and
        writing mode. Raises OSError if the opening fails.
        Passes the file onwards to store_file_content
        which handles the reading and writing of the file.
        :return: None
        """
        file_name = filedialog.askopenfilename()
        try:
            file = open(file_name, "r+", newline='', encoding='utf-8')
            store_file_content(file, self.__file_selection_main_window)
        except OSError:
            self.__box = messagebox.showwarning("Error", "Opening of the file failed")

    def get_username(self):
        """
        Gets the username of the user using the application.
        Uses the string "user" as a fallback.

        :return: the user's username, str
        """
        try:
            return getpass.getuser()
        except:
            return "user"

    def get_current_date(self):
        """
        Gets the current hour when the program is opened. Also
        calls the print_greeting -method.

        :return: None
        """
        #Gets the hour the application is opened
        current_hour = datetime.now()
        current_hour = int(current_hour.strftime("%H"))
        self.print_greeting(current_hour)

    def print_greeting(self, current_hour):
        """
        Shows a greeting to the user according to the time of day.
        Greeting is constructed by using the hour from get_current_date -method
        and username from get_username -method

        :param current_hour: the current hour when the user is using
        the application, int
        :return: 
        """
        if 9 > current_hour >= 6:
            time_of_day = "morning"
        elif 12 > current_hour >= 9:
            time_of_day = "day"
        elif  16 > current_hour >= 12:
            time_of_day = "afternoon"
        elif  24 > current_hour >= 16:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        user = self.get_username()
        self.__greeting.configure(text=f"Good {time_of_day} {user}!")

class managing_menu():
    """
    Functions as a template for the budget managing interface
    """
    def __init__(self, data_dict, headers, categories):
        self.__mainwindow = Tk()
        self.__mainwindow.geometry("1200x500")

        self.__delete_event_button = Button(text="Delete item by selecting it and pressing here",
                                            command=lambda: self.delete_event(data_dict))
        cols = headers
        self.__list_of_events = ttk.Treeview(self.__mainwindow, columns=cols, show='headings')
        self.__info_about_scrolling = Label(text="You can scroll the budget window with your mouse!")
        #Creates the columns and headings for the budget table
        for names in cols:
            self.__list_of_events.heading(names, text=names, anchor=W)

        #Sets the current highest event id from the return value of
        #update_and_sort_data_method.
        self.__new_event_id, dict = self.update_and_sort_data(data_dict)

        self.__list_of_events.pack()
        self.__info_about_scrolling.pack(side=TOP, pady=5, padx=5)
        self.__delete_event_button.pack(pady=10, padx=10)


        self.__adding_frame = Frame(self.__mainwindow)
        self.__adding_frame.pack()

        self.__event_type_menu_state = StringVar()
        self.__category_menu_state = StringVar()

        self.__event_date = Entry(self.__adding_frame)
        self.__event_type = OptionMenu(self.__adding_frame,
                                       self.__event_type_menu_state, "Expense", "Income")

        self.__event_category = OptionMenu(self.__adding_frame,
                                           self.__category_menu_state,
                                           self.check_if_category_menu_empty(categories))
        self.__event_price = Entry(self.__adding_frame)
        self.__event_details = Entry(self.__adding_frame)

        self.__submit_new_event = Button(self.__adding_frame,
                                         text="Add event",
                                         command=lambda: self.add_new_event(data_dict))

        #Creates the labels for input fields for adding an event, names are taken
        #from the column headers of the submitted file
        self.__event_date_label = Label(self.__adding_frame, text=f"{cols[0]} (DD.MM.YYYY)")
        self.__event_type_label = Label(self.__adding_frame, text=cols[1])
        self.__event_category_label = Label(self.__adding_frame, text=cols[2])
        self.__event_price_label = Label(self.__adding_frame, text=cols[3])
        self.__event_details_label = Label(self.__adding_frame, text=cols[4])

        self.__event_date_label.grid(row=0, column=0)
        self.__event_type_label.grid(row=0, column=1)
        self.__event_category_label.grid(row=0, column=2)
        self.__event_price_label.grid(row=0, column=3)
        self.__event_details_label.grid(row=0, column=4)

        self.__event_date.grid(row=1, column=0,pady=5, padx=5)
        self.__event_type.grid(row=1, column=1,pady=5, padx=5)
        self.__event_category.grid(row=1, column=2,pady=5, padx=5)
        self.__event_price.grid(row=1, column=3,pady=5, padx=5)
        self.__event_details.grid(row=1, column=4,pady=5, padx=5)
        self.__submit_new_event.grid(row=1, column=5,pady=5, padx=5)

        #Elements for adding a category
        self.__new_category_label = Label(self.__adding_frame,
                                          text="Write the name of the category to add")
        self.__new_category_field = Entry(self.__adding_frame)
        self.__new_category_submit_button = Button(self.__adding_frame,
                                                   text="Add category",
                                                   command=lambda: self.add_category(categories))
        self.__new_category_label.grid(row=3, column=0, pady=5, padx=5)
        self.__new_category_field.grid(row=3, column=1, pady=5, padx=5)
        self.__new_category_submit_button.grid(row=3, column=2, pady=5, padx=5)

        #Elements for deleting a category
        self.__deletion_menu_state = StringVar()
        self.__deleteable_category_list = OptionMenu(self.__adding_frame,
                                                     self.__deletion_menu_state,
                                                     self.check_if_category_menu_empty(categories))
        self.__deleteable_category_list_label = Label(self.__adding_frame,
                                                       text="Choose a category to be deleted")
        self.__delete_category_button = Button(self.__adding_frame,
                                               text="Delete category",
                                               command=lambda: self.delete_category(categories))
        self.__deleteable_category_list_label.grid(row=4, column=0, pady=5, padx=5)
        self.__deleteable_category_list.grid(row=4, column=1, pady=5, padx=5)
        self.__delete_category_button.grid(row=4, column=2, pady=5, padx=5)

        self.__mainwindow.mainloop()


    def check_if_category_menu_empty(self, categories):
        """
        Check if categories exist, if so populate the category
        menu with them, else with empty string.

        :param categories: a list containing the categories
        that exist already, list
        :return:
        """
        if categories == []:
            return ''
        else:
            return *categories,

    def delete_category(self, categories):
        """
        Deletes a user specified category from the "database" (list) and the
        category selection menu which is part of the UI. Also calls the
        update_menus -method to update the appearance of category menus
        
        :param categories: a list containing the categories 
        that exist already, list
        :return: None
        """
        # Removes the event and clears the menus
        item = self.__deletion_menu_state.get();
        
        if item in categories:
            categories.remove(item)
            self.__deleteable_category_list.children["menu"].delete(0, "end")
            self.__event_category.children["menu"].delete(0, "end")
            self.update_menus(categories)
            self.__category_menu_state.set('')
            self.__deletion_menu_state.set('')

    def update_menus(self, categories):
        """
        Updates both the category deletion and adding menus when
        a category is added or deleted by the user.

        :param categories: a list containing the categories
        that exist already, list
        :return:
        """
        for items in categories:

            self.__event_category.children["menu"].add_command(label=items, command=lambda
                item=items: self.__category_menu_state.set(item))

            self.__deleteable_category_list.children["menu"].\
                add_command(label=items, command=lambda
                item=items: self.__deletion_menu_state.set(item))

    def add_category(self, categories):
        """
        Adds a user specified category to the "database" (list) and the
        category selection menu which is part of the UI. Raises ValueError
        if either the category is empty or exists already. Also calls the
        update_menus -method to update the appearance of category menus.
        
        :param categories: a list containing the categories 
        that exist already, list
        :return: None
        """
        category_to_add = self.__new_category_field.get()
        #Clears the menus
        self.__event_category.children["menu"].delete(0, "end")
        self.__deleteable_category_list.children["menu"].delete(0, "end")
        try:
            if category_to_add == '':
                self.__alertbox = messagebox.showwarning("Error", "Category can't be empty!")
                return
            else:
                if category_to_add not in categories:
                    categories.append(category_to_add)
                    #Loops through the list of expenditure
                    # categories and creates the menu anew
                    self.update_menus(categories)
                else:
                    raise ValueError

            self.__alertbox = messagebox.showinfo("Success!",
                                                  f"Category {category_to_add} added!")

        except ValueError:
            self.__alertbox = messagebox.showwarning("Error!",
                                                     f"Category {category_to_add} "
                                                     f"already exists!")

    def add_new_event(self, data_dict):
        """
        Adds a new event to both the dictionary and the UI. 
        Also updates the UI and calls the update_and_sort_data -method
        to sort the newly changed data.
        
        :param data_dict: data_dict: the dictionary containing
        the rows of the file and their id:s, dict
        :return: 
        """
        event_id = self.__new_event_id
        #Gets the values the user has inserted/selected
        [date, event_type, category, price, details] = self.__event_date.get(), \
                                                       self.__event_type_menu_state.get(), \
                                                       self.__category_menu_state.get(), \
                                                       self.__event_price.get(), \
                                                       self.__event_details.get()

        #Validates the date
        try:
            datetime.strptime(date, '%d.%m.%Y').date()
        except ValueError:
            self.__alertbox = messagebox.showwarning("Error!",
                                                     "Incorrect date format!")
            return
        if event_type == '':
            self.__alertbox = messagebox.showwarning("Error!", "Select a type!")
            return
        if category == '':
            self.__alertbox = messagebox.showwarning("Error!",
                                                     "Select or add a category!")
            return
        #Tries to convert the price/amount to float and adds a minus sign if type
        #Expense is selected
        try:
            if event_type == 'Expense':
                #Removes the preceeding minus sign, if user has entered it accidentally
                price = price.lstrip("-")
                price = f"-{price}"
            price = float(price)
            price = format(price, ".2f")

        except ValueError:
            self.__alertbox = messagebox.showwarning("Error!",
                                                     "The given value is not a float!")
            return

        event_detail_list = [date, event_type, category, price, details]
        #Inserts the new event into a dictionary so it can be stored
        data_dict[event_id] = event_detail_list
        #Converts the date for the user to see more clearly
        #Insertes the event into the UI
        self.__list_of_events.insert('', END, iid=str(event_id), values=event_detail_list)
        #Updates the ID for the next event id
        self.__new_event_id += 1
        self.update_and_sort_data(data_dict)
        #Clears the fields, except for date because the user propably
        #wants to add several entries on the same day
        self.__event_price.delete(0, 'end')
        self.__event_details.delete(0, 'end')

    def update_and_sort_data(self, data_dict):
        """
        This function sorts the rows of the file
        according to the date. Assigns new IDs to the entries in
        ascending order. Also handles the updating of the UI
        when a new entry is added.

        :param data_dict: data_dict: the dictionary containing the rows of the file
        and their id:s, dict
        :return: and id for the next product which will be added, int
        """

        #Sorts the dictionary containing the rows according to date
        sorted_data_dict_items = sorted(data_dict.items(),
                                        key=lambda x: datetime.strptime(x[1][0], '%d.%m.%Y'))
        #The original dict is cleared
        data_dict = {}
        #The UI is cleared
        for row in self.__list_of_events.get_children():
            self.__list_of_events.delete(row)
        counter = 0
        #Sorted items are inserted into the dictionary and
        #given new ascending ID:s.
        for items in sorted_data_dict_items:
            counter += 1
            data_dict[counter] = items[1]
            #Updates the UI
            self.__list_of_events.insert('', END, iid=str(counter), values=items[1])
        #Return the next ID for an item when it's eventually added
        return counter + 1, data_dict

    def delete_event(self, data_dict):
        """
        A method which deletes a row a user has currently selected from the file.
        The deletion happens both from the UI and the file and is permanent.

        :param data_dict: the dictionary containing the rows of the file
        and their id:s.
        :return: None
        """
        #The event the user has selected to be deleted
        event_to_delete = self.__list_of_events.selection()[0]
        #Get the ID of the event
        event_id = int(self.__list_of_events.focus())
        self.__list_of_events.delete(event_to_delete)
        del data_dict[event_id]

def store_file_content(file, window):
    """
    Reads the file given by the user and inserts the data
    from the file into a dictionary. Also starts the
    budget management interface and when the program is closed, writes
    the existing data and added data back to the file and saves it.

    :param file: the file user has specified (csv)
    :param window: the previous file selection window
    which has to be closed
    :return: None
    """
    #Destroys the file selection window
    window.destroy()
    writer_obj = writer(file, delimiter=";")
    datareader = reader(file, delimiter=";")
    data_dict = {}
    #If the headers don't exist i.a the file is new, they are created,
    #otherwise they are read from the file
    try:
        headers = next(datareader)
    except StopIteration:
        headers = ["Date", "Type", "Category", "Amount", "Details", "Categories:", "[]"]
        writer_obj.writerow(headers)
    
    #Converts the list from the file from str to list
    categories = literal_eval(headers[6])
    #Stores the rows into a dictionary, with and unique ID as a key
    event_id = 1
    for row in datareader:
        data_dict[event_id] = row
        event_id += 1

    #Creates the budget management interface
    management_screen = managing_menu(data_dict, headers[0:5], categories)

    #Clears the file once read
    file.truncate(0)
    file.seek(0)

    #Write the data that existed before or was added to the file 
    #during the existence of the program
    headers[6] = str(categories)
    writer_obj.writerow(headers)

    #Dict must be sorted before saving, because it doesn't
    #keep its order. This is because this dictionary and
    #the one inside the class are not the same.
    sorted_dict_values = sorted(data_dict.items(),
                                key=lambda x: datetime.strptime(x[1][0], '%d.%m.%Y'))
    for items in sorted_dict_values:
        writer_obj.writerow(items[1])
    file.close()


def main():
    file_select_screen = file_selection_menu()
if __name__ == "__main__":
    main()
import datetime
import os
import shutil
import random
import sqlite3
import tkinter as tk
import webbrowser
import configparser
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.filedialog import asksaveasfilename
from tkcalendar import DateEntry
from ttkwidgets.autocomplete import AutocompleteCombobox
from textwrap import wrap
import matplotlib.pyplot as plt
import pandas as pd

#Makes a backup copy of the vgames.db file
if os.path.exists('vgames.db'):
        shutil.copyfile( 'vgames.db' , 'vgames.bak' )

class database:
        def __init__ (self):
                self.conn = sqlite3.connect('vgames.db')
                self.cursor = self.conn.cursor()
                self.cursor.execute("PRAGMA foreign_keys = 1")
        def open (self):
                conn = self.conn
                return conn
        def close (self):
                self.conn.close()
                return
        def fetchone(self, sql, args=None):
                if not args:
                        self.cursor.execute(sql)
                else:
                        self.cursor.execute(sql, args)
                sqlresults = self.cursor.fetchone()
                self.conn.commit()
                self.conn.close()
                return sqlresults
        def fetchall(self, sql, args=None):
                if not args:
                        self.cursor.execute(sql)
                else:
                        self.cursor.execute(sql, args)
                sqlresults = self.cursor.fetchall()
                self.conn.commit()
                self.conn.close()
                return sqlresults
        def execute(self, sql, args=None):
                if not args:
                        self.cursor.execute(sql)
                else:
                        self.cursor.execute(sql, args)
                self.conn.commit()
                self.conn.close()

def create_database():

        #Creates tables
        database().execute("""CREATE TABLE IF NOT EXISTS "tbl_Games" (
	"GameID"	INTEGER NOT NULL DEFAULT '',
	"SystemID"	INTEGER NOT NULL DEFAULT '',
	"Title"	TEXT NOT NULL DEFAULT '',
	"Year"	INTEGER NOT NULL DEFAULT '',
	"CompanyID"	INTEGER NOT NULL DEFAULT '',
	"GenreID"	INTEGER NOT NULL DEFAULT '',
	"Format"	INTEGER NOT NULL DEFAULT '',
        "Region"        INTEGER NOT NULL DEFAULT '',
	"Progress"	INTEGER NOT NULL DEFAULT '',
	"Playtime"	NUMERIC NOT NULL DEFAULT '',
	"Date_Completed"	TEXT NOT NULL DEFAULT '',
	"Rating"	NUMERIC NOT NULL DEFAULT '',
	"Notes"	TEXT NOT NULL DEFAULT '',
	PRIMARY KEY("GameID"),
	FOREIGN KEY("SystemID") REFERENCES "tbl_System"("SystemID"),
	FOREIGN KEY("CompanyID") REFERENCES "tbl_Company"("CompanyID"),
	FOREIGN KEY("GenreID") REFERENCES "tbl_Genre"("GenreID"));""")

        database().execute("""CREATE TABLE IF NOT EXISTS "tbl_Company" (
	"CompanyID"	INTEGER NOT NULL,
	"CompanyName"	TEXT NOT NULL,
	PRIMARY KEY("CompanyID" AUTOINCREMENT))""")

        database().execute("""CREATE TABLE IF NOT EXISTS "tbl_WishList" (
	"WishListID"	INTEGER NOT NULL,
	"SystemID"	INTEGER NOT NULL,
	"Title"	TEXT NOT NULL,
	PRIMARY KEY("WishListID"),
	FOREIGN KEY("SystemID") REFERENCES "tbl_System"("SystemID"))""")

        database().execute("""CREATE TABLE IF NOT EXISTS "tbl_Genre" (
	"GenreID"	INTEGER NOT NULL,
	"GenreName"	TEXT NOT NULL,
	PRIMARY KEY("GenreID"))""")

        database().execute("""CREATE TABLE IF NOT EXISTS "tbl_System" (
	"SystemID"	INTEGER NOT NULL,
	"SystemName"	TEXT NOT NULL,
	PRIMARY KEY("SystemID" AUTOINCREMENT))""")

        #Adds newer columns to tbl_Games. If the column exists, it is skipped.
        try:
                database().execute("ALTER TABLE tbl_Games ADD COLUMN Playtime NUMERIC NOT NULL DEFAULT ''")
        except:
                print ("Playtime column already exists.")              
        try:
                database().execute("ALTER TABLE tbl_Games ADD COLUMN Date_Completed TEXT NOT NULL DEFAULT ''")
        except:
                print ("Date_Completed column already exists.")               
        try:
                database().execute("ALTER TABLE tbl_Games ADD COLUMN Rating NUMERIC NOT NULL DEFAULT ''")
        except:	
                print ("Rating column already exists.")
        try:
                database().execute("ALTER TABLE tbl_Games ADD COLUMN Region NUMERIC NOT NULL DEFAULT ''")
        except:	
                print ("Region column already exists.")

        #Creates default Systems (if they don't exist)
        DBSystems = database().fetchall("SELECT SystemName FROM tbl_System")
        DBSystemsList = []
        for row in DBSystems:
                DBSystemsList.append(row[0])

        DefaultSystems = ['Atari 2600', 'Colecovision', 'Dreamcast', 'Famicom', 'Game Boy', 'Game Boy Advance', 'Game Boy Color', 'Gamecube', 'Game Gear', 'Genesis', 'NES', 'Nintendo 64', 'Nintendo 3DS', 'Nintendo DS', 'Nintendo Switch', 'PC', 'PS1', 'PS2', 'PS3', 'PS4', 'SNES', 'Super Famicom', 'Wii', 'Wii U', 'Xbox 360', 'Xbox']
        for System in DefaultSystems:
                if System not in DBSystemsList:
                        database().execute ("INSERT INTO tbl_System (SystemID, SystemName) VALUES (null, ?)", (System,))

        #Creates default Genres (if they don't exist)
        DBGenres = database().fetchall("SELECT GenreName FROM tbl_Genre")
        DBGenresList = []
        for row in DBGenres:
                DBGenresList.append(row[0])

        DefaultGenres = ['', 'Action', 'Adventure', 'Arcade', 'Beat-Em-Up', 'Board', 'Card', 'Compilation', 'Educational', 'Fighting', 'First Person Shooter', 'Metroidvania', 'Other', 'Platformer', 'Puzzle', 'Roguelike', 'RPG', 'Racing', 'Shooter', 'Simulation', 'Sports']
        for Genre in DefaultGenres:
                if Genre not in DBGenresList:
                        database().execute ("INSERT INTO tbl_Genre (GenreID, GenreName) VALUES (null, ?)", (Genre,))

create_database()

#-----------------------------------------------------------------------------------------

class main_window:
        def __init__(self, master):

                self.master = master

                master.geometry("1250x700")
                master.title("Video Games Database")
                master.iconbitmap("vgames.ico")
                master.configure(bg='gray')
                master.protocol("WM_DELETE_WINDOW", self.close_app)

                #-----------------------POPUP MENUS-----------------------------

                #Creates SEARCH WEB pop-up Menu
                self.popup_search_web = Menu(master, tearoff = 0)
                self.popup_search_web.add_command(label="Google", command=lambda: self.search_web (self.games_list.focus(), "Google"))
                self.popup_search_web.add_separator()
                self.popup_search_web.add_command(label="YouTube", command=lambda: self.search_web (self.games_list.focus(), "YouTube"))
                self.popup_search_web.add_command(label="Wikipedia",command=lambda: self.search_web (self.games_list.focus(), "Wikipedia"))
                self.popup_search_web.add_command(label="Price Charting", command=lambda: self.search_web (self.games_list.focus(), "Price Charting"))
                self.popup_search_web.add_command(label="GameFAQs", command=lambda: self.search_web (self.games_list.focus(), "GameFAQs"))
                self.popup_search_web.add_command(label="HowLongToBeat", command=lambda: self.search_web (self.games_list.focus(), "HowLongToBeat"))
                self.popup_search_web.add_command(label="Metacritic", command=lambda: self.search_web (self.games_list.focus(), "Metacritic"))

                #Creates STATS pop-up menu
                self.popup_stats = Menu(master, tearoff = 0)
                self.popup_stats.add_command(label="Total Games Per System", command=lambda: stats(self.system_menu_option.get()).System())
                self.popup_stats.add_separator()
                self.popup_stats.add_command(label="Games By Format", command=lambda: stats(self.system_menu_option.get()).Format())
                self.popup_stats.add_command(label="Games By Genre",command=lambda:stats(self.system_menu_option.get()).Genre())
                self.popup_stats.add_command(label="Games By Decade",command=lambda:stats(self.system_menu_option.get()).Decade())
                self.popup_stats.add_command(label="Games By Region",command=lambda:stats(self.system_menu_option.get()).Region())
                self.popup_stats.add_separator()
                self.popup_stats.add_command(label="Progress", command=lambda: stats(self.system_menu_option.get()).Progress())
                self.popup_stats.add_command(label="Highest Playtime", command=lambda: stats(self.system_menu_option.get()).Playtime())
                self.popup_stats.add_separator()
                self.popup_stats.add_command(label="Top 10 Companies", command=lambda: stats(self.system_menu_option.get()).Top10Companies())

                #Creates UPDATE PROGRESS pop-up menu
                self.popup_update_progress = Menu(master, tearoff = 0)
                self.popup_update_progress.add_command(label = "Complete", command=lambda: self.update_right_click(self.games_list.focus(), "Progress", "Complete"))
                self.popup_update_progress.add_command(label = "Incomplete", command=lambda: self.update_right_click(self.games_list.focus(), "Progress", "Incomplete"))
                self.popup_update_progress.add_command(label = "Currently Playing", command=lambda: self.update_right_click(self.games_list.focus(), "Progress", "Currently Playing"))
                self.popup_update_progress.add_command(label = "Backlog", command=lambda: self.update_right_click(self.games_list.focus(), "Progress", "Backlog"))
                self.popup_update_progress.add_command(label = "N/A", command=lambda: self.update_right_click(self.games_list.focus(), "Progress", "N/A"))

                #Creates UPDATE RATING pop-up menu
                self.popup_update_rating = Menu(master, tearoff = 0)
                self.popup_update_rating.add_command(label = "1", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 1))
                self.popup_update_rating.add_command(label = "2", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 2))
                self.popup_update_rating.add_command(label = "3", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 3))
                self.popup_update_rating.add_command(label = "4", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 4))
                self.popup_update_rating.add_command(label = "5", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 5))
                self.popup_update_rating.add_command(label = "6", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 6))
                self.popup_update_rating.add_command(label = "7", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 7))
                self.popup_update_rating.add_command(label = "8", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 8))
                self.popup_update_rating.add_command(label = "9", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 9))
                self.popup_update_rating.add_command(label = "10", command=lambda: self.update_right_click(self.games_list.focus(), "Rating", 10))

                #Creates EXPORT pop-up menu
                self.popup_export = Menu(master, tearoff = 0)
                self.popup_export.add_command(label = "CSV", command=lambda: export().csv())
                self.popup_export.add_command(label = "Google Sheets", command=lambda: export().gsheets())

                #Creates RIGHT CLICK pop-up menu
                self.popup_right_click = Menu(master, tearoff = 0)
                self.popup_right_click.add_command(label="View/Edit", command=lambda: game_info_window(self).view_game_window(self.games_list.focus()))
                self.popup_right_click.add_command(label="Duplicate", command=lambda: self.duplicate_game(self.games_list.focus()))
                self.popup_right_click.add_command(label="Delete", command=lambda: self.delete_game(self.games_list.focus()))
                self.popup_right_click.add_separator()
                self.popup_right_click.add_cascade(label="Search Web", menu=self.popup_search_web)
                self.popup_right_click.add_separator()
                self.popup_right_click.add_cascade(label="Update Progress", menu=self.popup_update_progress)
                self.popup_right_click.add_cascade(label="Update Rating", menu=self.popup_update_rating)

                #---------------------------FRAMES--------------------------------

                # #Creates top frame
                self.FrameTop =LabelFrame (master, padx =10, bg="black")
                self.FrameTop.pack(side=TOP, pady =10)

                #Creates frame for System Selection
                self.FrameSystemSelect=LabelFrame(self.FrameTop, text="System", padx=5, pady=5, fg="yellow", bg="black")
                self.FrameSystemSelect.pack (side=LEFT, padx=5, pady=5)

                #Creates Format box frame
                self.FrameFormat=LabelFrame(self.FrameTop, text="Format", padx=5, pady=5, fg="yellow", bg="black")
                self.FrameFormat.pack (side=LEFT, padx=5, pady=5)

                #Creates Region box frame
                self.FrameRegion=LabelFrame(self.FrameTop, text="Region", padx=5, pady=5, fg="yellow", bg="black")
                self.FrameRegion.pack (side=LEFT, padx=5, pady=5)

                #Creates Progress box frame
                self.FrameProgress=LabelFrame(self.FrameTop, text="Progress", padx=5, pady=5, fg="yellow", bg="black")
                self.FrameProgress.pack (side=LEFT, padx=5, pady=5)

                #Creates Search box frame
                self.FrameSearch=LabelFrame(self.FrameTop, text="Search", padx=5, pady=5, fg="yellow", bg="black")
                self.FrameSearch.pack (side=LEFT, padx=5, pady=5)

                #Creates View box frame
                self.FrameView=LabelFrame(self.FrameTop, text="View", padx=5, pady=5, fg="yellow", bg="black")
                self.FrameView.pack (side=LEFT, padx=5, pady=5)

                #Creates Clear Filter box frame
                self.FrameReset=LabelFrame(self.FrameTop, text="Filter", padx=5, pady=5, fg="yellow", bg="black")
                self.FrameReset.pack (side=LEFT, padx=5, pady=5)

                #Games list frame
                self.FrameGames=LabelFrame(master, padx=5, pady=5)
                self.FrameGames.pack (side=TOP, padx=5, pady=5)

                #Buttons frame
                self.FrameButtons=LabelFrame(master, padx=5, bg="#404040")
                self.FrameButtons.pack (side=BOTTOM, padx=5, pady=5)
                self.FrameButtons1=LabelFrame(self.FrameButtons, padx=5, pady=5, bg="black")
                self.FrameButtons1.pack (side=LEFT, padx=5, pady=5)
                self.FrameButtons2=LabelFrame(self.FrameButtons, padx=5, pady=5, bg="black")
                self.FrameButtons2.pack (side=LEFT, padx=5, pady=5)
                self.FrameButtons3=LabelFrame(self.FrameButtons, padx=5, pady=5, bg="black")
                self.FrameButtons3.pack (side=LEFT, padx=5, pady=5)
                self.FrameButtons4=LabelFrame(self.FrameButtons, padx=5, pady=5, bg="black")
                self.FrameButtons4.pack (side=RIGHT, padx=5, pady=5)

                #------------------------TOP TOOLBAR--------------------------------

                #System Selection Menu
                system = database().fetchall("SELECT SystemName from tbl_System ORDER BY SystemName")
                systems_menu = ['All']
                for row in system:
                        systems_menu.append(row[0])
                self.system_menu_option = StringVar()
                self.system_menu_option = ttk.Combobox(self.FrameSystemSelect, values = systems_menu, state="readonly")
                self.system_menu_option.bind ('<<ComboboxSelected>>', lambda event: self.update_game_list())
                self.system_menu_option.set("All")
                self.system_menu_option.grid(row=0,column=0) 

                #Format Selection Menu
                values = ['All', 'Physical', 'Digital', 'Other']
                self.FormatSelection = StringVar()
                self.FormatSelection = ttk.Combobox(self.FrameFormat, values = values, state="readonly", width=10)
                self.FormatSelection.bind ('<<ComboboxSelected>>', lambda event: self.update_game_list())
                self.FormatSelection.set("All")
                self.FormatSelection.grid(row=0, column=0)

                #Region Selection Menu
                values = ['All', 'NTSC-U/C', 'NTSC-J', 'NTSC-C', 'PAL']
                self.RegionSelection = StringVar()
                self.RegionSelection = ttk.Combobox(self.FrameRegion, values = values, state="readonly", width=10)
                self.RegionSelection.bind ('<<ComboboxSelected>>', lambda event: self.update_game_list())
                self.RegionSelection.set("All")
                self.RegionSelection.grid(row=0, column=0)

                #Progress Selection Menu
                values = ['All', 'Complete', 'Incomplete', 'Currently Playing', 'Backlog', 'N/A']
                self.ProgressSelection = StringVar()
                self.ProgressSelection = ttk.Combobox(self.FrameProgress, values = values, state="readonly")
                self.ProgressSelection.bind ('<<ComboboxSelected>>', lambda event: self.update_game_list())
                self.ProgressSelection.set("All")
                self.ProgressSelection.grid(row=0,column=0) 

                #Search bar
                self.txt_search_bar = Entry(self.FrameSearch, width = 40)
                self.txt_search_bar.bind("<KeyPress>", lambda event: self.update_game_list())
                self.txt_search_bar.bind("<KeyRelease>", lambda event: self.update_game_list())
                self.txt_search_bar.grid(row=0, column=1)

                #Clear button
                self.btn_clearsearch = Button(
                        self.FrameSearch,
                        text = "Clear",
                        width = 4,
                        height= 1,
                        bg="grey",
                        fg="white",
                        command=self.clear_search
                )
                self.btn_clearsearch.grid(row=0, column=2, padx=10)

                #View Radio Button
                values = ['Game Info', 'Stats']
                self.ViewSelection = StringVar()
                col = 0
                for value in values:
                        self.rbt_View = Radiobutton (self.FrameView, text = value, value = value, variable = self.ViewSelection, bg='black', fg= 'white', selectcolor="red", command = self.update_game_list)
                        self.rbt_View.grid(row = 0, column = col)
                        col +=1
                self.ViewSelection.set('Game Info')

                #Clear Filter button
                self.btn_resetfilter = Button(
                        self.FrameReset,
                        text = "Reset Filter",
                        width = 8,
                        height= 1,
                        bg="red",
                        fg="white",
                        command=self.reset_filter
                )
                self.btn_resetfilter.grid(row=0, column=2, padx=10)

                #------------------------GAMES LIST--------------------------------

                #Games list (in Treeview)
                style = ttk.Style()
                style.theme_use("clam")
                style.configure("Treeview.Heading", background="red", foreground="white")

                self.games_list = ttk.Treeview(self.FrameGames, height = 20)
                self.games_list['columns'] = ('System', 'Title', 'Year', 'Company', 'Genre', 'Format', 'Region', 'Progress', 'Playtime', 'Date Completed', 'Rating')

                self.games_list.column("#0", width=0, stretch=NO)

                # 'Game Info' columns
                self.games_list.column("System",anchor=W, width=150)
                self.games_list.column("Title",anchor=W,width=350)
                self.games_list.column("Year",anchor=W,width=50)
                self.games_list.column("Company",anchor=W,width=150)
                self.games_list.column("Genre",anchor=W,width=150)
                self.games_list.column("Format",anchor=W,width=100)
                self.games_list.column("Region",anchor=W,width=80)

                # 'Stats' columns
                self.games_list.column("Progress",anchor=W,width=120)
                self.games_list.column("Playtime",anchor=W,width=100)
                self.games_list.column("Date Completed",anchor=W,width=100)
                self.games_list.column("Rating",anchor=W,width=100)

                self.games_list.heading("#0",text="",anchor=W)
                self.games_list.heading("System",text="System",anchor=W, command=lambda: self.sort_column (self.games_list, "System", False))
                self.games_list.heading("Title",text="Title",anchor=W, command=lambda: self.sort_column (self.games_list, "Title", False))
                self.games_list.heading("Year",text="Year",anchor=W, command=lambda: self.sort_column (self.games_list, "Year", False))
                self.games_list.heading("Company",text="Company",anchor=W, command=lambda: self.sort_column (self.games_list, "Company", False))
                self.games_list.heading("Genre",text="Genre",anchor=W, command=lambda: self.sort_column (self.games_list, "Genre", False))
                self.games_list.heading("Format",text="Format",anchor=W, command=lambda: self.sort_column (self.games_list, "Format", False))
                self.games_list.heading("Region",text="Region",anchor=W, command=lambda: self.sort_column (self.games_list, "Region", False))
                self.games_list.heading("Progress",text="Progress",anchor=W, command=lambda: self.sort_column (self.games_list, "Progress", False))
                self.games_list.heading("Playtime",text="Playtime",anchor=W, command=lambda: self.sort_column (self.games_list, "Playtime", False))
                self.games_list.heading("Date Completed",text="Date Completed",anchor=W, command=lambda: self.sort_column (self.games_list, "Date Completed", False))
                self.games_list.heading("Rating",text="Rating",anchor=W, command=lambda: self.sort_column (self.games_list, "Rating", False))
             
                self.games_list.grid(row=0, column=0)

                #Games list key bindings
                self.games_list.bind("<Double-Button-1>", lambda event: game_info_window(self).view_game_window(self.games_list.focus()))
                self.games_list.bind("<Return>", lambda event: game_info_window(self).view_game_window(self.games_list.focus()))
                self.games_list.bind("<Delete>", lambda event: self.delete_game(self.games_list.focus()))
                self.games_list.bind("<Button-3>", lambda event: main_window_popup_menu (self, event).Right_Click())

                #Creates label for game count
                self.lblgamecount = Label (self.FrameGames)
                self.lblgamecount.grid(row=1, column=0, columnspan=1)

                #Imports filters and window size from "vgames.ini" file
                if os.path.exists('vgames.ini'):  
                        
                        try:
                                config = configparser.ConfigParser()
                                config.read('vgames.ini')

                                SystemName = config.get('FILTERS', 'SystemName')
                                Progress = config.get('FILTERS', 'Progress')
                                Format = config.get('FILTERS', 'Format')
                                Region = config.get('FILTERS', 'Region')
                                View = config.get('FILTERS', 'View')
                                SearchString = config.get ('FILTERS', 'SearchString')
                                State = config.get ('WINDOW', 'State')

                                self.system_menu_option.set(SystemName)
                                self.ProgressSelection.set(Progress)
                                self.FormatSelection.set(Format)
                                self.RegionSelection.set(Region)
                                self.ViewSelection.set(View)
                                self.txt_search_bar.insert(0, SearchString)
                                self.master.state(State)
                        except:
                                #Passes try block if config line is not found.
                                pass

                #Initial update of the Treeview Games list
                self.update_game_list()

                #Adds scrollbar to Treeview Games list
                self.games_list_scrollbar = ttk.Scrollbar(self.FrameGames, orient=VERTICAL, command=self.games_list.yview)
                self.games_list.configure(yscroll=self.games_list_scrollbar.set)
                self.games_list_scrollbar.grid(row=0, column=1, sticky='ns')

                #------------------------BUTTONS--------------------------------

                self.btn_new = Button(
                        self.FrameButtons1,
                        text = "New",
                        width = 15,
                        height= 2,
                        bg="green",
                        fg="white",
                        command=lambda: game_info_window(self).new_game_window(self.system_menu_option.get(), self.FormatSelection.get())
                )

                self.btn_new.grid(row=0, column=0, padx=5, pady=5)

                self.btn_view = Button(
                        self.FrameButtons1,
                        text = "View/Edit",
                        width = 15,
                        height= 2,
                        bg="#000099",
                        fg="white",
                        command=lambda: game_info_window(self).view_game_window(self.games_list.focus())
                )

                self.btn_view.grid(row=0, column=1, padx=5, pady=5)

                self.btn_delete = Button(
                        self.FrameButtons1,
                        text = "Delete",
                        width = 15,
                        height= 2,
                        bg="red",
                        fg="white",
                        command=lambda: self.delete_game(self.games_list.focus())
                )

                self.btn_delete.grid(row=0, column=2, padx=5, pady=5)

                self.btn_random = Button(
                        self.FrameButtons2,
                        text = "Random Game",
                        width = 15,
                        height= 2,
                        bg="purple",
                        fg="white",
                        command=lambda: random_game_window(self)
                )

                self.btn_random.grid(row=0, column=0, padx=5, pady=5)


                self.btn_export = Button(
                        self.FrameButtons2,
                        text = "Export",
                        width = 15,
                        height= 2,
                        bg="#004d00",
                        fg="white",
                        command=lambda: main_window_popup_menu (self, 0).Export()
                )

                self.btn_export.grid(row=0, column=1, padx=5, pady=5)

                self.btn_stats = Button(
                        self.FrameButtons2,
                        text = "Stats",
                        width = 15,
                        height= 2,
                        bg="#cc3300",
                        fg="white",
                        command=lambda: main_window_popup_menu (self, 0).Stats()
                )

                self.btn_stats.grid(row=0, column=2, padx=5, pady=5)


                self.btn_hangman = Button(
                        self.FrameButtons3,
                        text = "Hangman",
                        width = 15,
                        height= 2,
                        bg="#0000e6",
                        fg="white",
                        command=lambda: hangman()
                )

                self.btn_hangman.grid(row=0, column=0, padx=5, pady=5)

                #Wish List button
                self.btn_wishlist = Button(
                        self.FrameButtons4,
                        width = 15,
                        height= 2,
                        bg="yellow",
                        fg="black",
                        command=lambda: wish_list_window(self)
                )
                self.btn_wishlist.grid(row=0, column=0, padx=5, pady=5)

                self.btn_wishlist.bind('<Control-Button-2>', lambda event: sql_query_window(self))
                self.btn_wishlist.bind('<Control-Button-3>', lambda event: sql_query_window(self))
       
                #Creates variable to detect if changes have been made to the database
                self.changes = False

                #Initial count for Wish List button text
                count = database().fetchone("SELECT COUNT(WishListID) FROM tbl_WishList")
                initial_wishlist_count = count[0]
                self.btn_wishlist.config (text= "Wish List (" + str(initial_wishlist_count) + ")")

        def update_game_list(self):
                
                #Clears current Treeview
                x = self.games_list.get_children()
                for item in x:
                        self.games_list.delete(item)

                #Creates local variables based on main window selections
                SystemName = self.system_menu_option.get()
                Progress = self.ProgressSelection.get()
                Format = self.FormatSelection.get()
                Region = self.RegionSelection.get()
                View = self.ViewSelection.get()
                SearchString = self.txt_search_bar.get()

                #Disables the "Reset Filter" button if any filter is not set to "All"
                if SystemName != "All" or Format != "All" or Progress != "All" or SearchString != "":
                        self.btn_resetfilter.config(state=NORMAL)
                else:
                        self.btn_resetfilter.config(state=DISABLED)

                #Disabled "Clear" search button if search box is blank
                if SearchString == "":
                        self.btn_clearsearch.config(state=DISABLED)
                else:
                        self.btn_clearsearch.config(state=NORMAL)

                #Sets SystemName variable to wildcard when "All" is selected
                if SystemName == "All":
                        SystemName = "%"
                
                #Sets "Format" variable to wildcard if "All" is selected
                if Progress == "All":
                        Progress = "%"
                
                #Sets "Region" variable to wildcard if "All" is selected
                if Region == "All":
                        Region = "%"

                #Sets "Progress" variable to wildcard if "All" is selected
                if Format == "All":
                        Format = "%"
                
                #Sets SearchString variable to wildcard when Search box is empty
                if SearchString == "":
                        SearchString = "%"

                Records = database().fetchall("""SELECT tbl_Games.GameID, tbl_System.SystemName as 'System', Title, Year, tbl_Company.CompanyName as 'Company', tbl_Genre.GenreName as 'Genre', Format, Region, Progress, Playtime, Date_Completed, Rating
                        FROM tbl_Games
                        LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_Games.SystemID
                        LEFT JOIN tbl_Genre ON tbl_Genre.GenreID = tbl_Games.GenreID 
			LEFT JOIN tbl_Company ON tbl_Company.CompanyID = tbl_Games.CompanyID 
                        WHERE (Title LIKE ? OR Company LIKE ? OR Genre LIKE ?) AND SystemName LIKE ? AND Progress LIKE ? AND Format LIKE ? AND Region LIKE ?
                        ORDER BY System, CASE WHEN Title like 'The %' THEN substring(Title, 5, 1000) ELSE Title END""" , ('%' + SearchString + '%', '%' + SearchString + '%', '%' + SearchString + '%', SystemName, Progress, Format, Region))
                
                #Displays all games in Treeview. NOTE: The iid is set to the GameID in the DB.
                gamecount = 0
                for column in Records:
                        self.games_list.insert("", index='end',iid=column[0], text="",
                        values =(column[1], column[2], column[3], column[4], column[5], column[6], column[7], column[8], column[9], column[10], column[11]))
                        gamecount += 1

                #Sets Treeview columns based on "View" combo box
                if View == "Game Info":
                        self.games_list["displaycolumns"]=("System", "Title", "Year", "Company", "Genre", "Format", "Region")
                if View == "Stats":
                        self.games_list["displaycolumns"]=("System", "Title", "Progress", "Playtime", "Date Completed", "Rating")

                #Sends number of games to 'update_game_count' function   
                self.update_game_count(gamecount)

                
        def update_game_count(self, gamecount):
                TotalGames = database().fetchone("SELECT COUNT(GameID) from tbl_Games")

                #Updates text in lblgamecount Label
                self.lblgamecount.config (text="Count: " + str(gamecount) + "/" + str(TotalGames[0]), font=('Helvetica', 10, 'bold'))
                       
        def sort_column(self, tview, column, reverse):
               
                #Edited from: https://stackoverflow.com/questions/1966929/tk-treeview-column-sort

                l = [(tview.set(k, column), k) for k in tview.get_children('')]
                l.sort(reverse=reverse)

                #Rearrange items in sorted positions
                for index, (val, k) in enumerate(l):
                        tview.move(k, '', index)

                #Reverse sort next time
                tview.heading(column, command=lambda: self.sort_column(tview, column, not reverse))

        def update_systems_menu(self):
                system = database().fetchall("SELECT SystemName from tbl_System ORDER BY SystemName")
                update_systems_menu = ['All']
                for row in system:
                        update_systems_menu.append(row[0])
                self.system_menu_option.config (values = update_systems_menu)

        def delete_game(self, GameID):
               
                if GameID == "":
                        messagebox.showwarning ("Delete", "No game selected!")
                        return
               
                Title = database().fetchone("SELECT Title FROM tbl_Games where GameID = ?", (GameID,))

                del_prompt = messagebox.askyesno("Delete", "Are you sure you want to delete " + Title[0] + "?", default = 'no')
                
                if del_prompt == 1:
                        database().execute ("DELETE FROM tbl_Games where GameID = ?", (GameID,))
                        
                        #Updates variable to indicate changes have been made
                        self.changes = True

                        self.update_game_list()
                        self.update_systems_menu()

        def duplicate_game(self, GameID):
                
                #Grabs current Treeview selection record data.
                old_game = database().fetchone ("""SELECT tbl_Games.GameID, SystemID, Title, Year, CompanyID, GenreID, Format, Region 
                        FROM tbl_Games
                        WHERE GameID = ?""", (GameID,))  
               
                #Duplicates game (leaves out 'Stats' fields)
                database().execute("INSERT INTO tbl_Games (GameID, SystemID, Title, Year, CompanyID, GenreID, Format, Region, Progress, Playtime, Date_Completed, Rating, Notes) VALUES (NULL, :SystemID, :Title, :Year, :CompanyID, :GenreID, :Format, :Region, :Progress, :Playtime, :Date_Completed, :Rating, :Notes)",
                        {

                        'SystemID': old_game[1],
                        'Title': old_game[2] + " - Copy",
                        'Year': old_game[3],
                        'CompanyID': old_game[4],
                        'GenreID': old_game[5],
                        'Format': old_game[6],
                        'Region': old_game[7],
                        'Progress': "",                       
                        'Playtime': "",
                        'Date_Completed': "",
                        'Rating': "",
                        'Notes': ""                                
                        })
                
                messagebox.showwarning ("Duplicate Game", old_game[2] + " duplicated!")

                #Updates variable to indicate changes have been made
                self.changes = True

                self.update_game_list()

                #Grabs new GameID (the latest record) and opens it in a new window
                LastRecord = database().fetchone("SELECT GameID FROM tbl_Games ORDER BY GameID DESC LIMIT 1")
                NewGameID = LastRecord[0]
                game_info_window(self).view_game_window(NewGameID)
                
        def update_right_click(self, GameID, Field, Value):
               
                if GameID == "":
                        messagebox.showwarning ("Update Game", "No game selected!")
                        return

                #Built for possible expansion of more right-click menu options
                if Field == "Progress":
                        database().execute("UPDATE tbl_Games SET Progress = ? WHERE GameID = ?", (Value, GameID,))

                if Field == "Rating":
                        database().execute("UPDATE tbl_Games SET Rating = ? WHERE GameID = ?", (Value, GameID,))

                #Updates variable to indicate changes have been made
                self.changes = True

                self.update_game_list()

        def search_web(self, GameID, Website):
                
                if GameID == "":
                        messagebox.showwarning ("Search Web", "No game selected!")
                        return

                #Finds System Name and Title of selected game
                result = database().fetchone("SELECT tbl_System.SystemName, Title FROM tbl_Games LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_Games.SystemID Where GameID = ?", (GameID,))
                SystemName = result[0]
                Title = result[1]

                #Sets URL based on selection
                if Website == "Google":
                        URL = "https://www.google.com/search?q=" + Title + " " + SystemName
                
                if Website == "YouTube":
                        URL = "https://www.youtube.com/results?search_query=" + Title + " " + SystemName

                if Website == "Wikipedia":
                        URL = "https://en.wikipedia.org/wiki/Special:Search?go=Go&search=" + Title + " " + SystemName

                if Website == "Price Charting":
                        URL = "https://www.pricecharting.com/search-products?type=prices&q=" + Title + " " + SystemName

                if Website == "GameFAQs":
                        URL = "https://gamefaqs.gamespot.com/search?game=" + Title

                if Website == "HowLongToBeat":
                        URL = "https://howlongtobeat.com/?q=" + Title

                if Website == "Metacritic":
                        URL = "https://www.metacritic.com/search/game/" + Title + "/results"

                webbrowser.open(URL)

        def clear_search(self):
                self.txt_search_bar.delete(0, END)
                self.update_game_list()

        def reset_filter (self):
                self.ProgressSelection.set("All")
                self.FormatSelection.set("All")
                self.system_menu_option.set("All")
                self.txt_search_bar.delete(0, END)
                self.update_game_list()

        def close_app(self):
                        
                #Adds warning if changes are made
                if self.changes:
                        response = messagebox.askyesno ("Close", "Changes have been made to the database! Would you like to update Google Sheets?")
                        if response:
                                export().gsheets()

                #Saves current filters and window state to 'vgames.ini' file
                config = configparser.ConfigParser()
                config['FILTERS'] = {
                        'SystemName': self.system_menu_option.get(), 
                        'Progress': self.ProgressSelection.get(),
                        'Format': self.FormatSelection.get(),
                        'Region': self.RegionSelection.get(),
                        'View': self.ViewSelection.get(),
                        'SearchString': self.txt_search_bar.get()
                                }

                config['WINDOW'] = {
                        'State': self.master.state()}                
      
                with open("vgames.ini","w") as f:
                        config.write(f)

                self.master.destroy()

class main_window_popup_menu:
                       
                def __init__(self, main_window, event): 
                        self.main_window = main_window
                        self.event = event
                                                                                 
                def Right_Click(self):
                        #Highlights selection in Treeview when right click is pressed
                        iid = self.main_window.games_list.identify_row(self.event.y)
                        self.main_window.games_list.selection_set(iid)
                        self.main_window.games_list.focus(iid)
                
                        #Displays menu
                        x = self.event.x_root
                        y = self.event.y_root
                        self.main_window.popup_right_click.tk_popup(x, y, 0)

                def Web(self):
                        #Display Web Search popup menu
                        self.main_window.popup_search_web.tk_popup()

                def Stats(self):
                        #Displays stats popup menu
                        x = self.main_window.btn_stats.winfo_rootx()
                        y = self.main_window.btn_stats.winfo_rooty() - 75
                        self.main_window.popup_stats.tk_popup(x, y, 0)
                
                def Export(self):
                        #Displays Export popup menu
                        x = self.main_window.btn_export.winfo_rootx()
                        y = self.main_window.btn_export.winfo_rooty() - 40
                        self.main_window.popup_export.tk_popup(x, y, 0)

class game_info_window:
        
        def __init__(self, main_window):
                #Grabs variables from 'main_window' class
                self.main_window = main_window

                #Draws Game Info Window
                self.game_info_window=Toplevel()
                self.game_info_window.geometry("725x425")
                self.game_info_window.iconbitmap("vgames.ico")
                self.game_info_window.configure(bg='#404040')
                self.game_info_window.bind('<Escape>', lambda event: self.game_info_window.destroy())
        
                self.frametop=LabelFrame(self.game_info_window, padx=5, pady=5, fg="yellow", bg="black")
                self.frametop.pack (side= TOP, padx=5, pady=5)
                
                self.framesystem=LabelFrame(self.frametop, text="System", font='bold', padx=5, pady=5, fg="yellow", bg="black")
                self.framesystem.pack (side= LEFT, padx=5)
                
                self.frametitle=LabelFrame(self.frametop, text="Title", font='bold', padx=5, pady=5, fg="yellow", bg="black")
                self.frametitle.pack (side= LEFT, padx=5)

                self.framemiddle=LabelFrame(self.game_info_window, labelanchor=N, padx=5, pady=5, fg="yellow", bg="black")
                self.framemiddle.pack (side=TOP)
                
                self.framegameinfo=LabelFrame(self.framemiddle, text="Game Info", font='bold', padx=20, pady=5, fg="yellow", bg="black")
                self.framegameinfo.pack (side= LEFT, padx=5, pady=5)

                self.framestats=LabelFrame(self.framemiddle, text="Stats", font='bold', padx=20, pady=5, fg="yellow", bg="black")
                self.framestats.pack (side= LEFT, padx=5, pady=5)
        
                self.framebottom=LabelFrame(self.game_info_window, padx=5, pady=5, fg="white", bg="black")
                self.framebottom.pack (side=TOP, padx=5, pady=5)

                self.framemiscinfo=LabelFrame(self.framebottom, text="Misc", font='bold', padx=5, pady=5, fg="yellow", bg="black")
                self.framemiscinfo.pack (side=TOP, padx=5, pady=5)

                self.framebuttons=LabelFrame(self.game_info_window,  padx=5, pady=5, fg="yellow", bg="black")
                self.framebuttons.pack (side=BOTTOM, padx=5, pady=5)
                
                self.system = database().fetchall("SELECT SystemName from tbl_System ORDER BY SystemName")
                self.systems_list = []
                for row in self.system:
                        self.systems_list.append(row[0])
                self.txt_system = AutocompleteCombobox(self.framesystem, width = 20, value=self.systems_list, completevalues=self.systems_list)
                # self.txt_system = ttk.Combobox(self.framesystem, value=self.systems_list, width = 20)
                self.txt_system.grid(row=0, column=1)
                self.txt_system.focus()

                self.txt_title = Entry (self.frametitle, fg = "black", bg = "white", width=50)
                self.txt_title.grid(row = 0, column= 0)
    
                self.btn_quick_search = Button(
                        self.frametitle,
                        text = "Search Web",
                        width = 10,
                        height= 1,
                        bg="green",
                        fg="white",
                        command=lambda: self.search_web(self.txt_system.get(), self.txt_title.get())
                
                ) 

                self.btn_quick_search.grid(row=0, column=1, padx=10)

                self.lbl_year = Label (self.framegameinfo, text= "Year:", fg="white", bg="black")
                self.lbl_year.grid(row = 1, column=0, sticky=E, padx = 5)
                self.txt_year = Entry (self.framegameinfo, fg = "black", bg = "white", width=10)
                self.txt_year.grid(row = 1, column= 1, sticky=W)

                self.lbl_Company = Label (self.framegameinfo, text= "Company:", fg="white", bg="black")
                self.lbl_Company.grid(row = 2, column=0, sticky=E, padx = 5)
                #Creates Company List for Combo Box
                self.company = database().fetchall("SELECT CompanyName from tbl_Company ORDER BY CompanyName")
                self.company_list = []
                for row in self.company:
                        self.company_list.append(row[0])
                self.txt_Company = AutocompleteCombobox(self.framegameinfo, width = 30, value=self.company_list, completevalues=self.company_list)
                # self.txt_Company = ttk.Combobox(self.framegameinfo, value=self.company_list, width = 47)
                self.txt_Company.grid(row=2, column=1, sticky=W)

                self.lbl_Genre = Label (self.framegameinfo, text= "Genre:", fg="white", bg="black")
                self.lbl_Genre.grid(row = 3, column=0, sticky=E, padx = 5)
                #Creates Genre List for Combo Box
                self.genre = database().fetchall("SELECT GenreName from tbl_Genre ORDER BY GenreName")
                self.genres_list = []
                for row in self.genre:
                        self.genres_list.append(row[0])
                self.txt_Genre = AutocompleteCombobox(self.framegameinfo, width = 30, value=self.genres_list, completevalues=self.genres_list)
                # self.txt_Genre = ttk.Combobox(self.framegameinfo, value=self.genres_list, width = 47)
                self.txt_Genre.grid(row=3, column=1, sticky=W)

                self.lbl_Format = Label (self.framegameinfo, text= "Format:", fg="white", bg="black")
                self.lbl_Format.grid(row = 4, column=0, sticky=E, padx = 5)
                self.format_list = ['Physical', 'Digital', 'Other']
                self.txt_Format = ttk.Combobox(self.framegameinfo, value = self.format_list, state="readonly", width = 8)
                self.txt_Format.grid(row = 4, column= 1, sticky=W)

                self.lbl_Region = Label (self.framegameinfo, text= "Region:", fg="white", bg="black")
                self.lbl_Region.grid(row = 5, column=0, sticky=E, padx = 5)
                self.region_list = ['NTSC-U/C', 'NTSC-J', 'NTSC-C', 'PAL']
                self.txt_Region = ttk.Combobox(self.framegameinfo, value = self.region_list, state="readonly", width = 12)
                self.txt_Region.grid(row = 5, column= 1, sticky=W)

                self.lbl_Progress = Label (self.framestats, text= "Progress:", fg="white", bg="black")
                self.lbl_Progress.grid(row = 1, column=0, sticky=E, padx = 5)
                self.progress_list = ['Incomplete', 'Complete', 'Currently Playing', 'Backlog', 'N/A']
                self.txt_Progress = ttk.Combobox(self.framestats, value = self.progress_list, state="readonly", width = 15)
                self.txt_Progress.grid(row = 1, column= 1, sticky=W)

                self.lbl_Playtime = Label (self.framestats, text= "Playtime:", fg="white", bg="black")
                self.lbl_Playtime.grid(row = 2, column=0, sticky=E, padx = 5)
                self.txt_Playtime = Entry (self.framestats, fg = "black", bg = "white", width=18)
                self.txt_Playtime.grid(row = 2, column= 1, sticky=W)

                self.lbl_Date_Completed= Label (self.framestats, text= "Date Completed:", fg="white", bg="black")
                self.lbl_Date_Completed.grid(row = 3, column=0, sticky=E, padx = 5)
                self.txt_Date_Completed = DateEntry(self.framestats, date_pattern = 'yyyy-mm-dd', width= 15, background= "black", foreground= "white",bd=2)
                self.txt_Date_Completed.grid(row = 3, column= 1, sticky=W)
                self.txt_Date_Completed.delete (0, END)
                self.txt_Date_Completed.config(state='readonly')

                self.lbl_Rating = Label (self.framestats, text= "Rating:", fg="white", bg="black")
                self.lbl_Rating.grid(row = 4, column=0, sticky=E, padx = 5)
                self.ratings_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                self.txt_Rating = ttk.Combobox(self.framestats, value = self.ratings_list, width = 5)
                self.txt_Rating.grid(row = 4, column= 1, sticky=W)

                #Bottom Spacer for the "Stats" frame
                self.lbl_Space = Label (self.framestats, text= "", fg="white", bg="black")
                self.lbl_Space.grid(row = 5, column=0, sticky=E, padx = 5)

                #Button to clear the "Date Completed" field
                self.btn_clear_Date_Completed = Button (
                        self.framestats,
                        text = "Clear",
                        width = 5,
                        height= 1,
                        bg="grey",
                        fg="white",
                        command=self.clear_Date_Completed
                )
                self.btn_clear_Date_Completed.grid(row=3, column=2, padx=5)

                self.lbl_Notes = Label (self.framemiscinfo, text= "Notes:", fg="white", bg="black")
                self.lbl_Notes.grid(row = 8, column=0, sticky=E, padx = 5)
                self.txt_Notes = Entry (self.framemiscinfo, fg = "black", bg = "white", width=50)
                self.txt_Notes.grid(row = 8, column= 1)
   
        def new_game_window(self, SystemName, Format):

                self.game_info_window.title("New Game")

                #Automatically adds 'System' field based on system selection drop down
                if SystemName != "All":
                        self.txt_system.set(SystemName)
                        self.txt_title.focus()
                
                #Automatically adds 'Format' field based on Format selection
                if Format != "All":
                        self.txt_Format.set(Format)

                btn_save_close = Button(
                self.framebuttons,
                text = "Save and Close",
                width = 15,
                height= 2,
                bg="green",
                fg="white",
                command=lambda: self.save_game (None, True, False)
                
                ) 
                btn_save_close.grid(row=0, column=0, padx=5, pady=5)

                btn_save_new = Button(
                self.framebuttons,
                text = "Save and New",
                width = 15,
                height= 2,
                bg="#000099",
                fg="white",
                command=lambda: self.save_game (None, True, True)

                ) 
                btn_save_new.grid(row=0, column=1, padx=5, pady=5)

                btn_cancel = Button(
                        self.framebuttons,
                        text = "Cancel",
                        width = 15,
                        height= 2,
                        bg="red",
                        fg="white",
                        command=self.game_info_window.destroy
                
                ) 
                btn_cancel.grid(row=0, column=2, padx=5, pady=5)
                
                self.game_info_window.mainloop()

        def view_game_window(self, GameID):

                self.game_info_window.title("View/Edit Game")

                if GameID == "":
                        self.game_info_window.destroy()
                        messagebox.showwarning ("View/Edit Game", "No game selected!")
                        return

                #Grabs current Treeview selection record data.
                old_field = database().fetchone ("""SELECT tbl_Games.GameID, tbl_System.SystemName, Title, Year, tbl_Company.CompanyName as 'Company', tbl_Genre.GenreName, Progress, Format, Region, Playtime, Date_Completed, Rating, tbl_Games.Notes 
                                FROM tbl_Games
                                LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_Games.SystemID
                                LEFT JOIN tbl_Genre ON tbl_Genre.GenreID = tbl_Games.GenreID
                                LEFT JOIN tbl_Company ON tbl_Company.CompanyID = tbl_Games.CompanyID 
                                WHERE GameID = ?
                                ORDER BY SystemName, Title""", (GameID,))  

                #Inserts old fields
                self.txt_system.set(old_field[1])
                self.txt_title.insert(0, old_field[2])
                self.txt_year.insert(0, old_field[3])
                self.txt_Company.set(old_field[4])
                self.txt_Genre.set(old_field[5])
                self.txt_Progress.set(old_field[6])
                self.txt_Format.set(old_field[7])
                self.txt_Region.set(old_field[8])
                self.txt_Playtime.insert(0, old_field[9])

                #'Date_Completed' field is temporary enabled to insert old field text. 
                self.txt_Date_Completed.config(state=NORMAL)
                self.txt_Date_Completed.insert(0, old_field[10])      
                self.txt_Date_Completed.config(state='readonly')

                self.txt_Rating.set(old_field[11])
                self.txt_Notes.insert(0, old_field[12])

                btn_update = Button(
                        self.framebuttons,
                        text = "Update",
                        width = 15,
                        height= 2,
                        bg="green",
                        fg="white",
                        command=lambda: self.save_game(GameID, False, False)
                
                ) 
                btn_update.grid(row=0, column=0, padx=5, pady=5)

                btn_save_new = Button(
                        self.framebuttons,
                        text = "Save As New",
                        width = 15,
                        height= 2,
                        bg="#000099",
                        fg="white",
                        command=lambda: self.save_game(GameID, True, False)
                
                ) 
                btn_save_new.grid(row=0, column=1, padx=5, pady=5)

                btn_cancel = Button(
                        self.framebuttons,
                        text = "Cancel",
                        width = 15,
                        height= 2,
                        bg="red",
                        fg="white",
                        command=self.game_info_window.destroy
                
                ) 
                btn_cancel.grid(row=0, column=2, padx=5, pady=5)

                self.game_info_window.mainloop()

        def move_to_database_window(self, System, Title):

                self.game_info_window.title("Move to Database")
                self.game_info_window.protocol("WM_DELETE_WINDOW", self.block_close_button) 

                #Inserts System Name and title from wishlist record
                self.txt_system.set (System)
                self.txt_title.insert (0, Title)

                #Sets focus to 'Year' text box
                self.txt_year.focus()

                btn_move_to_database = Button(
                        self.framebuttons,
                        text = "Save",
                        width = 15,
                        height= 2,
                        bg="Green",
                        fg="white",
                        command=lambda: self.save_game(None, True, False)
                
                ) 
                btn_move_to_database.grid(row=0, column=0)

                self.game_info_window.mainloop()

        def save_game(self, GameID, New, SaveAndNew):
                
                #Checks if System and Title are entered
                if self.txt_system.get() == "" or self.txt_title.get() == "":
                        messagebox.showwarning ("Video Games Database", "System and Title must be filled out!")
                        self.game_info_window.focus_force()
                        return

                #Checks if System Name is in the tbl_System table. If it is not, it will prompt whether it should be added.
                SystemName = (self.txt_system.get())
                if SystemName not in self.systems_list:
                        SystemResponse = messagebox.askyesno ("Warning", "You are about to create a new System: '" + SystemName +"'\nAre you sure you want to continue?")
                        if SystemResponse == False:
                                self.game_info_window.focus_force()
                                return
                        database().execute ("INSERT INTO tbl_System (SystemID, SystemName) VALUES (null, ?)", (SystemName,))
                #Converts System field to SystemID (from tbl_System)
                SystemID = database().fetchone ("SELECT SystemID FROM tbl_System WHERE SystemName = ?", (SystemName,))   
                
                #Checks if Genre Name is in the tbl_Genre table. If it is not, it will prompt whether it should be added.
                GenreName = (self.txt_Genre.get())
                if GenreName not in self.genres_list:
                        GenreResponse = messagebox.askyesno ("Warning", "You are about to create a new Genre: '" + GenreName +"'\nAre you sure you want to continue?")
                        if GenreResponse == False:
                                self.game_info_window.focus_force()
                                return
                        database().execute ("INSERT INTO tbl_Genre (GenreID, GenreName) VALUES (null, ?)", (GenreName,))
                #Converts Genre field to GenreID (from tbl_Genre)
                GenreID = database().fetchone ("SELECT GenreID FROM tbl_Genre WHERE GenreName = ?", (GenreName,))        

                #Checks if Company name is in the tbl_Compmany table. If not, it will be added.
                CompanyName = (self.txt_Company.get())
                if CompanyName not in self.company_list:
                        database().execute ("INSERT INTO tbl_Company (CompanyID, CompanyName) VALUES (null, ?)", (CompanyName,))
                #Converts Genre field to CompanyID (from tbl_Genre)
                CompanyID = database().fetchone ("SELECT CompanyID FROM tbl_Company WHERE CompanyName = ?", (CompanyName,))        

                #Creates a new record
                if New:

                        database().execute("INSERT INTO tbl_Games (GameID, SystemID, Title, Year, CompanyID, GenreID, Format, Region, Progress, Playtime, Date_Completed, Rating, Notes) VALUES (NULL, :SystemID, :Title, :Year, :CompanyID, :GenreID, :Format, :Region, :Progress, :Playtime, :Date_Completed, :Rating, :Notes)",
                                {
                                'SystemID': SystemID[0],
                                'Title': self.txt_title.get(),
                                'Year': self.txt_year.get(),
                                'CompanyID': CompanyID[0],
                                'GenreID': GenreID[0],
                                'Format': self.txt_Format.get(),
                                'Region': self.txt_Region.get(),
                                'Progress': self.txt_Progress.get(),
                                'Playtime': self.txt_Playtime.get(),
                                'Date_Completed': self.txt_Date_Completed.get(),
                                'Rating': self.txt_Rating.get(),
                                'Notes': self.txt_Notes.get()                                
                                })
                                        
                        messagebox.showinfo ("New Game", "Game Saved!")
                
                #Updates record
                else:
                        
                        database().execute("UPDATE tbl_Games SET SystemID = :SystemID, Title = :Title, Year = :Year, CompanyID = :Company, GenreID = :GenreID, Format = :Format, Region = :Region, Progress = :Progress, Playtime = :Playtime, Date_Completed = :Date_Completed, Rating = :Rating, Notes = :Notes WHERE GameID = :GameID",
                        {
                                'SystemID': SystemID[0],
                                'Title': self.txt_title.get(),
                                'Year': self.txt_year.get(),
                                'Company': CompanyID[0],
                                'GenreID': GenreID[0],
                                'Format': self.txt_Format.get(),
                                'Region': self.txt_Region.get(),
                                'Notes': self.txt_Notes.get(),
                                'Progress': self.txt_Progress.get(),
                                'Playtime': self.txt_Playtime.get(),
                                'Date_Completed': self.txt_Date_Completed.get(),
                                'Rating': self.txt_Rating.get(),
                                'GameID': GameID
                        })

                        messagebox.showinfo ("Update Game", "Game Updated!")

                        #Deletes unused CompanyNames from tbl_Company
                        unused_companies = database().fetchall("""SELECT tbl_Company.CompanyID from tbl_Company
                                LEFT JOIN tbl_Games ON tbl_Company.CompanyID = tbl_Games.CompanyID
                                WHERE Title is NULL""")
                        for row in unused_companies:
                                database().execute ("DELETE FROM tbl_Company WHERE CompanyID = ?", (row[0],))

                #Updates changes variable in 'main_window' class to indicate changes have been made
                self.main_window.changes = True

                self.game_info_window.destroy()

                self.main_window.update_game_list()
                self.main_window.update_systems_menu()

                #Opens another 'New Game' window if "Save and New" is pressed
                if SaveAndNew:
                        game_info_window(self.main_window).new_game_window(self.main_window.system_menu_option.get(), self.main_window.FormatSelection.get())


        def search_web(self, SystemName, Title):
                if SystemName == "" or Title == "":
                        messagebox.showwarning ("Search Web", "You must fill out both System and Title!")
                        return
                
                webbrowser.open("https://www.google.com/search?q=" + Title + " " + SystemName)

        def clear_Date_Completed(self):
                
                self.txt_Date_Completed.config(state=NORMAL)
                self.txt_Date_Completed.delete (0, END)
                self.btn_clear_Date_Completed.focus_set()
                self.txt_Date_Completed.config(state='readonly')
        
        def block_close_button(self):
                #This method is called to disable closing the window with 'X' in the 'Move_to_Database' method
                pass

class wish_list_window:
        def __init__(self, main_window):

                #Passes 'self' from 'main_window' class
                self.main_window = main_window

                self.wish_list_window=Toplevel()
                self.wish_list_window.geometry("625x425")
                self.wish_list_window.iconbitmap("vgames.ico")
                self.wish_list_window.configure(bg='#404040')
                self.wish_list_window.title("Wish List")
                self.wish_list_window.protocol("WM_DELETE_WINDOW")
        
                self.frametop=LabelFrame(self.wish_list_window, padx=5, pady=5, fg="yellow", bg="black")
                self.frametop.pack (side= TOP, padx=5, pady=5)                
                self.framesystem=LabelFrame(self.frametop, text="System", padx=5, pady=5, fg="yellow", bg="black")
                self.framesystem.pack (side= LEFT, padx=5)              
                self.frametitle=LabelFrame(self.frametop, text="Title", padx=5, pady=5, fg="yellow", bg="black")
                self.frametitle.pack (side= LEFT, padx=5)
                self.framewishlist=LabelFrame(self.wish_list_window, labelanchor=N, padx=5, pady=5)
                self.framewishlist.pack (side=TOP)                          
                self.framebottom=LabelFrame(self.wish_list_window, fg="white", bg="black", padx=5, pady=5)
                self.framebottom.pack (side=BOTTOM, padx=10, pady=10)
               
                system = database().fetchall("SELECT SystemName from tbl_System ORDER BY SystemName")
                self.systems_list = []
                for row in system:
                        self.systems_list.append(row[0])
                self.txt_system = ttk.Combobox(self.framesystem, value=self.systems_list, width = 20)
                self.txt_system.grid(row=0, column=1)
                self.txt_system.focus()

                self.txt_title = Entry (self.frametitle, fg = "black", bg = "white", width=50)
                self.txt_title.grid(row = 0, column= 0)
                self.txt_title.bind("<Return>", lambda event: self.add_wishlist_game())
    
                self.btn_add = Button(
                        self.frametitle,
                        text = "Add",
                        width = 10,
                        height= 1,
                        bg="green",
                        fg="white",
                        command=lambda: self.add_wishlist_game()              
                )
               
                self.btn_add.grid(row=0, column=1, padx=10)

                #Wish list (in Treeview)
                style = ttk.Style()
                style.theme_use("clam")
                style.configure("Treeview.Heading", background="red", foreground="white")
                self.wish_list = ttk.Treeview(self.framewishlist, height = 10)
                self.wish_list['columns'] = ('System', 'Title')

                self.wish_list.column("#0", width=0, stretch=NO)
                self.wish_list.column("System",anchor=W, width=150)
                self.wish_list.column("Title",anchor=W,width=350)
                
                self.wish_list.heading("#0",text="",anchor=W)
                self.wish_list.heading("System",text="System",anchor=W, command=lambda: self.sort_column (self.games_list, "System", False))
                self.wish_list.heading("Title",text="Title",anchor=W, command=lambda: self.sort_column (self.games_list, "Title", False))

                self.wish_list.grid(row=0, column=0)

                #Adds scrollbar to Treeview Wishlist
                self.wish_list_scrollbar = ttk.Scrollbar(self.framewishlist, orient=VERTICAL, command=self.wish_list.yview)
                self.wish_list.configure(yscroll=self.wish_list_scrollbar.set)
                self.wish_list_scrollbar.grid(row=0, column=1, sticky='ns')

                #Adds label showing total number of games on Wish List
                self.lblwishlistgamecount = Label (self.framewishlist)
                self.lblwishlistgamecount.grid(row=1, column=0, columnspan=1)
           
                self.update_wish_list()

                self.btn_move_to_database = Button(
                        self.framebottom,
                        text = "Move to Database",
                        width = 15,
                        height= 2,
                        bg="green",
                        fg="white",
                        command=lambda: self.move_to_database()
                )
        
                self.btn_move_to_database.grid(row=0, column=0, padx=5, pady=5)

                self.btn_delete = Button(
                        self.framebottom,
                        text = "Delete",
                        width = 15,
                        height= 2,
                        bg="red",
                        fg="white",
                        command=lambda: self.delete_wishlist_game()
                )

                self.btn_delete.grid(row=0, column=1, padx=5, pady=5)

                self.btn_export_gsheets = Button(
                        self.framebottom,
                        text = "Export to GSheets",
                        width = 15,
                        height= 2,
                        bg="#004d00",
                        fg="white",
                        command=self.export_wishlist_gsheets
                )

                self.btn_export_gsheets.grid(row=0, column=2, padx=5, pady=5)     

                self.btn_close = Button(
                        self.framebottom,
                        text = "Close",
                        width = 15,
                        height= 2,
                        bg="#33334d",
                        fg="white",
                        command=self.wish_list_window.destroy
                )

                self.btn_close.grid(row=0, column=3, padx=5, pady=5)                
           
                self.wish_list_window.mainloop()

        def update_wish_list(self):
                
                #Clears current Treeview
                x = self.wish_list.get_children()
                for item in x:
                        self.wish_list.delete(item)

                #Grabs games from tbl_WishList
                Records = database().fetchall("""SELECT WishListID, tbl_System.SystemName as 'System', Title
                        FROM tbl_WishList
                        LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_WishList.SystemID
                        ORDER BY SystemName, CASE WHEN Title like 'The %' THEN substring(Title, 5, 1000) ELSE Title END""")
                
                wishlistgamecount = 0
                #Displays wish list Treeview. NOTE: The iid is set to the GameID in the tbl_Wishlist table.
                for column in Records:
                        self.wish_list.insert("", index='end',iid=column[0], text="",
                        values =(column[1], column[2]))
                        wishlistgamecount += 1

                self.update_wishlist_game_count(wishlistgamecount)
                       
        def update_wishlist_game_count(self, wishlistgamecount):
                #Updates Wish List count label text
                self.lblwishlistgamecount.config (text="Count: " + str(wishlistgamecount), font=('Helvetica', 10, 'bold'))

                #Updates Wish List button in 'main_window' class
                self.main_window.btn_wishlist.config(text="Wish List (" + str(wishlistgamecount) + ")")
                        
        def add_wishlist_game (self):
                if self.txt_system.get() == "" or self.txt_title.get() == "":
                        messagebox.showwarning ("Wish List", "You must fill out both System and Title!")
                        self.wish_list_window.focus_force()
                        return

                #Checks if System Name is in the tbl_System table. If it is not, it will prompt whether it should be added.
                SystemName = self.txt_system.get()
                if SystemName not in self.systems_list:
                        SystemResponse = messagebox.askyesno ("Warning", "You are about to create a new SYSTEM: '" + SystemName +"'\nAre you sure you want to continue?")
                        if SystemResponse == False:
                                self.wish_list_window.focus_force()
                                return
                        database().execute ("INSERT INTO tbl_System (SystemID, SystemName) VALUES (null, ?)", (SystemName,))
                #Converts System field to SystemID (from tbl_System)
                SystemID = database().fetchone ("SELECT SystemID FROM tbl_System WHERE SystemName = ?", (SystemName,))   

                database().execute("INSERT INTO tbl_Wishlist VALUES (NULL, :SystemID, :Title)",
                                        {
                                        'SystemID': SystemID[0],
                                        'Title': self.txt_title.get(),                        
                                        })

                #Clears System and Title fields
                self.txt_system.set("")
                self.txt_title.delete(0, END)
                self.txt_system.focus()

                self.update_wish_list()

        def move_to_database(self):
                
                if self.wish_list.focus() == "":
                        messagebox.showwarning ("Move to Database", "No game selected!")
                        self.wish_list_window.focus_force()
                        return

                response = messagebox.askyesno ("Move to Database", "You are sure you want to move this game to the main database?")

                if response:

                        #Creates System and Title fields to send to game_info_window class
                        wishlist_field = database().fetchone ("""SELECT tbl_System.SystemName as 'System', Title
                        FROM tbl_WishList
                        LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_WishList.SystemID
                        WHERE WishListID = ?""", (self.wish_list.focus(),))
                        
                        System = wishlist_field[0]
                        Title = wishlist_field[1]

                        #Deletes game from Wish List
                        database().execute ("DELETE FROM tbl_Wishlist where WishListID = ?", (self.wish_list.focus(),))

                        #Updates wish list count and closes Wishlist window.
                        self.update_wish_list()
                        self.wish_list_window.destroy()                      
                        
                        #Sends wish list item to a new game info window
                        game_info_window(self.main_window).move_to_database_window(System, Title)
                                                                   
                else:
                        self.wish_list_window.focus_force()
        
        def delete_wishlist_game(self):
                if self.wish_list.focus() == "":
                        messagebox.showwarning ("Delete", "No game selected!")
                        self.wish_list_window.focus_force()
                        return
                
                database().execute ("DELETE FROM tbl_Wishlist where WishListID = ?", (self.wish_list.focus(),))

                self.update_wish_list()
        
        def export_wishlist_gsheets(self):
                
                #Creates a Pandas dataframe of Wishlist table
                conn = database().open()
                df = pd.read_sql("""SELECT tbl_System.SystemName as 'System', Title
                        FROM tbl_WishList
                        LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_WishList.SystemID     
                        ORDER BY System, CASE WHEN Title like 'The %' THEN substring(Title, 5, 1000) ELSE Title END""", conn)
                database().close()

                df.to_clipboard(excel=True, index=False)

                opengsheetprompt = messagebox.askyesno ("Google Sheets", "Wishlist copied to clipboard.\n\nWould you like to open Google Sheets?")
        
                if opengsheetprompt == True:
                        webbrowser.open("https://docs.google.com/spreadsheets/u/0/")
                        
class random_game_window:

        def __init__(self, main_window):

                self.main_window = main_window

                self.random_game_window=Toplevel()
                self.random_game_window.geometry("450x150")
                self.random_game_window.title("Random Game")
                self.random_game_window.iconbitmap("vgames.ico")
                self.random_game_window.configure(bg='#404040')

                self.frametop=LabelFrame(self.random_game_window, padx=5, pady=5, bg = 'black')
                self.frametop.pack (side= TOP, padx=5, pady=5)
                self.framebottom=LabelFrame(self.random_game_window, bg = 'black', padx = 5, pady =5)
                self.framebottom.pack (side=BOTTOM, padx=5, pady =5)

                self.lbl_title = Label (self.frametop, bg='black', fg='white', font=('Helvetica', 12, 'bold'))
                self.lbl_title.grid(row = 0, column=0)
                self.lbl_system = Label (self.frametop, bg='black', fg = 'white', font=('Helvetica', 10, 'bold'))
                self.lbl_system.grid(row = 1, column=0)

                self.btn_reroll = Button(
                self.framebottom,
                text = "Reroll",
                width = 15,
                height= 2,
                bg="green",
                fg="white",
                command=self.randomize

                ) 
                self.btn_reroll.grid(row=0, column=0, padx=5, pady=5)

                self.btn_close = Button(
                self.framebottom,
                text = "Close",
                width = 15,
                height= 2,
                bg="red",
                fg="white",
                command=self.random_game_window.destroy

                ) 
                self.btn_close.grid(row=0, column=1, padx=5, pady=5)

                self.randomize()

                self.random_game_window.mainloop()


        def randomize(self):
        
                #Grabs total number of games in Treeview
                count = 0
                random_games_list = []
                x = self.main_window.games_list.get_children()
                for item in x:
                        random_games_list.append(item)
                        count += 1

                #Randomizes total number of games in Treeview
                Rand_Num = random.randint(0, count)
                Rand_GameID = (random_games_list[Rand_Num-1])

                #Fetches random game in list
                Rand_Game = database().fetchone("""SELECT Title, tbl_System.SystemName as 'System'
                        FROM tbl_Games
                        LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_Games.SystemID WHERE GameID = ? """ , (Rand_GameID,))

                #Displays randomly generated game in a labels
                self.lbl_title.config (text= Rand_Game[0])
                self.lbl_system.config (text= Rand_Game[1])

class sql_query_window:
        
        def __init__(self, main_window):
                
                self.main_window = main_window

                self.sql_query_window=Toplevel()
                self.sql_query_window.geometry("500x150")
                self.sql_query_window.title("Execute SQL Query")
                self.sql_query_window.iconbitmap("vgames.ico")
                self.sql_query_window.configure(bg='#404040')

                self.frametop=LabelFrame(self.sql_query_window, padx=10, pady=10, bg = 'black')
                self.frametop.pack (side= TOP, padx=5, pady=5)
                self.framebottom=LabelFrame(self.sql_query_window, bg = 'black', padx = 5, pady =5)
                self.framebottom.pack (side=BOTTOM, padx=5, pady =5)

                self.lbl_sqlquery = Label (self.frametop, text= "Enter SQL Query:", font = "bold", fg="white", bg="black")
                self.lbl_sqlquery.grid(row = 0, column=0, sticky=W, padx = 5)
                self.txt_sqlquery = Entry (self.frametop, font = "bold", fg = "black", bg = "white", width=50)
                self.txt_sqlquery.grid(row = 1, column= 0, sticky=W)

                self.btn_execute = Button(
                self.framebottom,
                text = "Execute",
                width = 15,
                height= 2,
                bg="green",
                fg="white",
                command=self.execute

                ) 
                self.btn_execute.grid(row=0, column=0, padx=5, pady=5)

                self.btn_cancel = Button(
                self.framebottom,
                text = "Cancel",
                width = 15,
                height= 2,
                bg="red",
                fg="white",
                command=self.sql_query_window.destroy

                ) 
                self.btn_cancel.grid(row=0, column=1, padx=5, pady=5)

        def execute(self):

                sql_query = self.txt_sqlquery.get()
                msgbox_text = "Are you sure you want to run the SQL query below? THIS CAN'T BE UNDONE!\n\n" + sql_query

                response = messagebox.askyesno ("Execute SQL Query", msgbox_text)
                if response:
                        try:
                                database().execute(sql_query)
                                self.main_window.changes = True
                                self.main_window.update_game_list()
                                self.sql_query_window.destroy()
                        except:
                                messagebox.showwarning ("Execute SQL Query", "SQL Query Failed!")
                                self.sql_query_window.destroy()


class hangman:
        
        def __init__(self):
                
                #Draws Hangman Window
                self.hangman_window=Toplevel()
                self.hangman_window.geometry("750x500")
                self.hangman_window.iconbitmap("vgames.ico")
                self.hangman_window.title("Hangman")
                self.hangman_window.configure(bg='#404040')
                self.hangman_window.state("zoomed")

                #Frames
                self.frametop=LabelFrame(self.hangman_window, padx=100, pady=10, bg = 'black')
                self.frametop.pack (side= TOP, padx=5, pady=5)
                self.framemiddle=LabelFrame(self.hangman_window, padx=5, pady=5, fg="yellow", bg = 'black')
                self.framemiddle.pack (side=TOP, padx=5, pady=5)

                self.framehangman=LabelFrame(self.frametop, padx=5, pady=5, bg = 'black')
                self.framehangman.pack (side=TOP, padx=5, pady=5)

                self.frameword=LabelFrame(self.frametop, padx=5, pady=5, borderwidth=0, highlightthickness=0, bg = 'black')
                self.frameword.pack (side=TOP, padx=5, pady=5)

                self.framehint=LabelFrame(self.frametop, text = "Hint", font="bold", padx=5, pady=5, fg="yellow", bg = 'black')
                self.framehint.pack(side=BOTTOM)

                self.frameguess=LabelFrame(self.framemiddle, text = "Guess", padx=5, pady=5, font="bold", fg="yellow", bg = 'black')
                self.frameguess.pack (side = LEFT, padx=5, pady=5)
                self.framealreadyguessed=LabelFrame(self.framemiddle, text = "Already Guessed", padx=20, pady=5, font="bold", fg="yellow", bg = 'black')
                self.framealreadyguessed.pack (side = LEFT, padx=5, pady=5)
                self.frametries=LabelFrame(self.framemiddle, text = "Tries Left", padx=20, pady=5, font="bold", fg="yellow", bg = 'black')
                self.frametries.pack (side = RIGHT, padx=5, pady=5)

                self.frameinfo=LabelFrame(self.hangman_window, padx=5, pady=5, font="bold", fg="yellow", bg = 'black')
                self.frameinfo.pack(side=TOP)

                self.framebuttons=LabelFrame(self.hangman_window, padx=5, pady=5, fg="yellow", bg="black")
                self.framebuttons.pack (side=BOTTOM, padx=5, pady=5)

                #Hangman
                self.lbl_hangman = Label (self.framehangman, font = "bold", fg="white", bg="black", padx=10, justify="left")
                self.lbl_hangman.grid(row=0, column=0)

                #Word
                self.lbl_word = Label (self.frameword, font="bold", fg="white", bg="black")
                self.lbl_word.grid (row=0, column=0)

                #Hint
                self.lbl_hint = Label (self.framehint, font="bold", fg="white", bg="black")
                self.lbl_hint.grid(row=1, column=1)

                #Guess box
                self.txt_guess = Entry(self.frameguess, font="bold", width = 4)
                self.txt_guess.grid(row=0, column=0, padx=5, pady=5)
                
                #Guess button
                self.btn_guess = Button(
                        self.frameguess,
                        text = "Guess",
                        width = 5,
                        height= 1,
                        bg="blue",
                        fg="white",
                        command=self.guess
                )
                self.btn_guess.grid(row=0, column=1, padx=10)

                #Guessed label and text box
                self.lbl_alreadyguessed = Label(self.framealreadyguessed, font="bold", fg="white", bg="black")
                self.lbl_alreadyguessed.grid (row=0, column=0, padx=5, pady=5)

                #Tries label
                self.lbl_tries= Label(self.frametries, font="bold", fg="white", bg="black")
                self.lbl_tries.grid (row=0, column=0, padx=5, pady=5)

                #Info label
                self.lbl_info = Label (self.frameinfo, font="bold", fg="white", bg="black")
                self.lbl_info.grid (row=0, column=0, padx=5, pady=5)

                #Bottom buttons
                self.btn_newgame = Button(
                self.framebuttons,
                text = "New Game",
                width = 15,
                height= 2,
                bg="green",
                fg="white",
                command=self.new_game

                ) 
                self.btn_newgame.grid(row=0, column=0, padx=5, pady=5)

                self.btn_close = Button(
                self.framebuttons,
                text = "Close",
                width = 15,
                height= 2,
                bg="red",
                fg="white",
                command=self.hangman_window.destroy

                ) 
                self.btn_close.grid(row=0, column=1, padx=5, pady=5)

                self.new_game()
               
                self.hangman_window.mainloop()

        def new_game(self):
               
                self.btn_guess.config (state=NORMAL)
                self.txt_guess.config (state=NORMAL)
                self.txt_guess.delete (0, END)
                self.txt_guess.focus()
                self.txt_guess.bind("<Return>", lambda event: self.guess())

                #Sets tries variable and label
                self.tries = 7
                self.lbl_tries.config (text = str(self.tries))

                #Fetches random game from database
                randomgame = database().fetchone("""SELECT tbl_System.SystemName as 'System', Title, Year, tbl_Company.CompanyName as 'Company', tbl_Genre.GenreName as 'Genre'
                        FROM tbl_Games
                        LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_Games.SystemID
                        LEFT JOIN tbl_Genre ON tbl_Genre.GenreID = tbl_Games.GenreID 
			LEFT JOIN tbl_Company ON tbl_Company.CompanyID = tbl_Games.CompanyID
                        ORDER BY random()
                        LIMIT 1
                        """)
                
                if randomgame is None:
                        messagebox.showwarning ("Hangman", "No games in database!")
                        self.hangman_window.destroy()

                #Word Creation
                title = randomgame[1]
                wordcreate = ""
                for i, letter in enumerate(title):                       
                        if letter == " ":
                                wordcreate += " "
                        #Removes special characters from title
                        elif letter.isalnum() == False:
                                wordcreate += ""
                        else:
                                wordcreate += letter
                self.word = wordcreate.upper()
                
                #Sets hint (either System, Year, Company, or Genre)
                self.hint = random.choice ([randomgame[0], randomgame[2], randomgame[3], randomgame[4]])
                self.lbl_hint.config (text = self.hint)

                #Sets Already Guessed variable and label
                self.alreadyguessed = ""
                self.alreadyguessed_show = ""
                self.lbl_alreadyguessed.config (text = self.alreadyguessed_show)

                #Sets "Info" label
                self.lbl_info.config (text = "Make a guess!")

                self.update_hangman()
                self.update_word_display()

        def update_word_display(self):

                self.word_display = ""

                #Shows letter if not in "Already Guessed" box
                for i, letter in enumerate(self.word):
                        if letter == " ":
                                self.word_display += "    "
                        elif letter in self.alreadyguessed:
                                self.word_display += " " + letter + " "                     
                        elif letter not in self.alreadyguessed:
                                self.word_display += " _ "

                #Updates word label
                self.lbl_word.config (text = self.word_display)

        def update_hangman(self):

                if self.tries == 7:

                        self.lbl_hangman.config (text =
                "________\n"
                "|                \n"
                "|                \n"
                "|\n"
                "|\n"
                "|\n"
                "|\n"
                "|_________"

                        )

                elif self.tries == 6:

                        self.lbl_hangman.config (text =
                "________\n"
                "|               |\n"
                "|               |\n"
                "|\n"
                "|\n"
                "|\n"
                "|\n"
                "|_________"

                        )

                elif self.tries == 5:

                        self.lbl_hangman.config (text =
                "________\n"
                "|               |\n"
                "|               |\n"
                "|                O\n"
                "|\n"
                "|\n"
                "|\n"
                "|_________"

                        )
        
                elif self.tries == 4:

                        self.lbl_hangman.config (text =
                "________\n"
                "|               |\n"
                "|               |\n"
                "|               O\n"
                "|               |\n"
                "|\n"
                "|\n"
                "|_________"

                        )

                elif self.tries == 3:

                        self.lbl_hangman.config (text =
                "________\n"
                "|               |\n"
                "|               |\n"
                "|               O\n"
                "|              /|\n"
                "|\n"
                "|\n"
                "|_________"

                        )
                
                
                elif self.tries == 2:

                        self.lbl_hangman.config (text =
                "________\n"
                "|               |\n"
                "|               |\n"
                "|               O\n"
                "|              /|\ \n"
                "|\n"
                "|\n"
                "|_________"

                        )

                elif self.tries == 1:

                        self.lbl_hangman.config (text =
                "________\n"
                "|               |\n"
                "|               |\n"
                "|               O\n"
                "|              /|\ \n"
                "|              / \n"
                "|\n"
                "|_________"

                        )

                elif self.tries == 0:

                        self.lbl_hangman.config (text =
                "________\n"
                "|               |\n"
                "|               |\n"
                "|               O\n"
                "|              /|\ \n"
                "|              / \ \n"
                "|\n"
                "|_________"

                        )

        def guess(self):

                #Converts guessed letter to uppercase
                guess = self.txt_guess.get().upper()

                #Guess validation
                if len(guess) > 1:
                        self.lbl_info.config(text = "Only enter 1 letter or number!")
                        self.txt_guess.delete (0, END)
                        self.txt_guess.focus()
                        return

                if guess == "":
                        self.lbl_info.config(text = "No letters or numbers entered!")
                        self.txt_guess.focus()
                        return
                
                if guess in self.alreadyguessed:
                        self.lbl_info.config(text = guess + " has already been guessed!")
                        self.txt_guess.delete (0, END)
                        self.txt_guess.focus()
                        return

                if guess.isalnum() == False:
                        self.lbl_info.config(text = "Only enter letters or numbers!")
                        self.txt_guess.delete (0, END)
                        self.txt_guess.focus()
                        return

                #Updates "Already Guessed" variable
                self.alreadyguessed += guess
                #Only show letter/number in the "Already Guessed" label if it's NOT in word
                if guess not in self.word:
                        self.alreadyguessed_show += guess + " "
                self.lbl_alreadyguessed.config (text = self.alreadyguessed_show)

                #Checks if guess is good or bad
                if guess not in self.word:
                        #Updates "Tries" variable and label
                        self.tries -= 1
                        self.lbl_tries.config (text = str(self.tries))

                        self.lbl_info.config(text = guess + " is NOT in the word!")

                        #Game ends when out of tries
                        if self.tries == 0:
                                self.lbl_info.config(text = "Out of tries! Game over!")
                                self.end_game()                            
                        self.hangman_window.focus()
                        self.update_hangman()

                elif guess in self.word:
                        self.lbl_info.config(text = guess + " is in the word!")
                        self.update_word_display()
                        #Checks for win - no blank ( _ ) spaces
                        if "_" not in self.word_display:
                                self.lbl_info.config(text = "You won!!")
                                self.end_game()
                
                #Clears "Guess" text box and sets focus
                self.txt_guess.delete(0, END)
                self.txt_guess.focus()
        
        def end_game(self):

                #Reveals word
                self.word_display = ""
                for i, letter in enumerate(self.word):
                        if letter == " ":
                                self.word_display += "    "
                        else:
                                self.word_display += " " + letter + " "
                self.lbl_word.config (text = self.word_display)

                #Disables guess text box, guess button, and bindings
                self.btn_guess.config (state=DISABLED)
                self.txt_guess.delete (0, END)
                self.txt_guess.config (state=DISABLED)
                self.txt_guess.unbind("<Return>")

class export:

        def __init__(self):
                #Creates Panadas Dataframe with all records
                conn = database().open()
                self.df = pd.read_sql_query("""SELECT tbl_System.SystemName as 'System', Title, Year, tbl_Company.CompanyName as 'Company', tbl_Genre.GenreName as 'Genre', Format, Region, Progress, Playtime, Date_Completed, Rating, Notes
                FROM tbl_Games
                LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_Games.SystemID
                LEFT JOIN tbl_Genre ON tbl_Genre.GenreID = tbl_Games.GenreID
                LEFT JOIN tbl_Company ON tbl_Company.CompanyID = tbl_Games.CompanyID  
                ORDER BY System, CASE WHEN Title like 'The %' THEN substring(Title, 5, 1000) ELSE Title END""", conn)
                database().close()

        def csv(self):

                #Save dialog box
                filedate = datetime.date.today()
                csv_export_file = asksaveasfilename (initialfile = 'vgames-' + str(filedate), defaultextension=".csv",filetypes=[("All Files","*.*"),("Text Documents","*.txt")])
                if csv_export_file == "": 
                        return

                #Exports DataFrame to CSV file
                self.df.to_csv(csv_export_file, index=False)
                
                response = messagebox.askyesno ("Export to CSV", "CSV file exported successfully! Would you like to open it?")
                if response:
                        os.system ("start " + csv_export_file)
        
        def gsheets(self):
                
                self.df.to_clipboard(excel=True, index=False)

                opengsheetprompt = messagebox.askyesno ("Google Sheets", "Games copied to clipboard.\n\nWould you like to open Google Sheets?")

                if opengsheetprompt == True:
                        webbrowser.open("https://docs.google.com/spreadsheets/u/0/")


class stats:

        def __init__(self, SystemName):
                self.SystemName = SystemName
                
                #Sets values when "All" is selected as System
                if self.SystemName == "All":
                        self.SystemName = "%"
                        
                #Creates Pandas DataFrame from SQL query
                conn = database().open()
                self.df = pd.read_sql_query("""SELECT tbl_System.SystemName as 'System', Title, Year, tbl_Company.CompanyName as 'Company', tbl_Genre.GenreName as 'Genre', Format, Region, Progress, Playtime, Date_Completed, Rating
                                FROM tbl_Games
                                LEFT JOIN tbl_System ON tbl_System.SystemID = tbl_Games.SystemID
                                LEFT JOIN tbl_Genre ON tbl_Genre.GenreID = tbl_Games.GenreID 
                                LEFT JOIN tbl_Company ON tbl_Company.CompanyID = tbl_Games.CompanyID 
                                WHERE SystemName LIKE '%""" + self.SystemName + "%'", conn)
                database().close()
    
        def Progress(self):
                if self.SystemName == "%":
                        Title = "Progress - All Systems"
                else:
                        Title = "Progress - " + self.SystemName
                plt.figure(Title)
                plt.get_current_fig_manager().window.state('zoomed')
                self.df.Progress.value_counts(sort=False).plot(kind='pie', autopct='%1.2f%%', ylabel='', shadow=True)           
                plt.title(Title)
                plt.show()


        def Playtime(self):
                if self.SystemName == "%":
                        Title = "Highest Playtime - All Systems"
                else:
                        Title = "Highest Playtime - " + self.SystemName
                        
                plt.figure(Title)
                plt.get_current_fig_manager().window.state('zoomed')
                              
                self.df = self.df.astype(str).sort_values(by=['Playtime'], ascending=True)
                Games = self.df.Title.tail(5) + " (" + self.df.System.tail(5) + ")"
                GamesSpaced = [ '\n'.join(wrap(Game, 10)) for Game in Games ]   
                Playtime = self.df.Playtime.tail(5)
        
                plt.barh (GamesSpaced, [int(x) for x in Playtime])
                plt.title(Title)
                plt.tick_params (labelsize = 8)
                plt.xlabel ("Hours")
                plt.ylabel ("Game")
                plt.show()
                

        def Genre(self):
                if self.SystemName == "%":
                        Title = "Total Games by Genre - All Systems"
                else:
                        Title = "Total Games by Genre - " + self.SystemName
                
                plt.figure(Title)
                plt.get_current_fig_manager().window.state('zoomed')
                GenreCount = self.df.Genre.value_counts(ascending=True)
                GenreCount.plot(kind='barh')
                plt.title(Title)
                plt.xlabel ("Total")
                plt.xticks(rotation=90)

                #Adds values to bars
                for i, v in enumerate(GenreCount):
                        plt.text(v + 1, i - .25, str(v))
                plt.show()
        
        def Format(self):
                if self.SystemName == "%":
                        Title = "Games By Format - All Systems"
                else:
                        Title = "Games By Format - " + self.SystemName
                plt.figure(Title)
                plt.get_current_fig_manager().window.state('zoomed')
                self.df.Format.value_counts(sort=False).plot(kind='pie', autopct='%1.2f%%', ylabel='', shadow=True)           
                plt.title(Title)
                plt.show()

        def Region(self):
                if self.SystemName == "%":
                        Title = "Games By Region - All Systems"
                else:
                        Title = "Games By Region - " + self.SystemName
                plt.figure(Title)
                plt.get_current_fig_manager().window.state('zoomed')
                self.df.Region.value_counts(sort=False).plot(kind='pie', autopct='%1.2f%%', ylabel='', shadow=True)           
                plt.title(Title)
                plt.show()     

        def Decade(self):
                if self.SystemName == "%":
                        Title = "Total Games by Decade - All Systems"
                else:
                        Title = "Total Games by Decade - " + self.SystemName

                plt.figure(Title)
                plt.get_current_fig_manager().window.state('zoomed')         
            
                #Converts year to a decade
                decade = self.df.value_counts((self.df.Year//10)*10).sort_index(ascending=False)

                decade.plot(kind='barh')
                plt.title(Title)
                plt.xlabel ("Total")
                plt.ylabel ("Decade")
                plt.xticks(rotation=90)

                #Adds values to bars
                for i, v in enumerate(decade):
                        plt.text(v + 1, i - .25, str(v))
                
                plt.show()  
    
        def System(self):
                #Re-runs the Stats class with "All" if system selection is not set to "All"
                if self.SystemName != "%":
                        stats("All").System()
                        return
                                
                Title = "Total Games Per System"
                plt.figure(Title)
                plt.get_current_fig_manager().window.state('zoomed')
                TotalGames = self.df.System.value_counts(ascending=True)
                TotalGames.plot(kind='barh')
                plt.title(Title)
                plt.xlabel ("Total")
                plt.xticks(rotation=90)

                #Adds values to bars
                for i, v in enumerate(TotalGames):
                        plt.text(v + 1, i - .25, str(v))          
                plt.show()  

        def Top10Companies(self):
                if self.SystemName == "%":
                        Title = "Top 10 Companies - All Systems"
                else:
                        Title = "Top 10 Companies - " + self.SystemName
                        
                plt.figure(Title)
                plt.get_current_fig_manager().window.state('zoomed')

                Top10Companies = self.df.Company.value_counts(ascending=True).tail(10)
                Top10Companies.plot(kind='barh')
               
                plt.title(Title)
                plt.tick_params (labelsize = 8)
                plt.xlabel ("Total")
                plt.ylabel ("Company")

                #Adds values to bars
                for i, v in enumerate(Top10Companies):
                        plt.text(v + 1, i - .25, str(v))          
                
                plt.show()  
                
root = Tk()
app = main_window(root)

root.mainloop()
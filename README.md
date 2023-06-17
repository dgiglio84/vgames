<b>NOTE: Please read the <i>Install.txt</i> file for installation instructions.</b>

<b>UPDATES</b>

6-16-2023
- Added additional changes to the <i>Notes</i> field:
  1. The field can now contain multiple lines.
  2. On the Main Window, a <i>Notes</i> column has been added. Games that contain a note will show a ● in this column.
- Added a new preference called "Load saved filter on startup." If this is switched on, the filter from your previous session will be loaded. If this is switched off, the default filter will be displayed.
- Titles that start with the words "A" or "An" will be ignored as the list is alphabetized.

6-12-2023
- Added two more options on the <b>Preferences</b> window:
  1. Instant Search (On/Off) - If switched on, search results will appear as you type. If switched off, you will have to press Enter to complete a search.
  2. Google Sheets Warning on Exit (On/Off) - If switched on, you will prompted to export your database to Google Sheets if changes have been made. If switched off, you will not be prompted.

4-30-2023
- Added a <b>Preferences</b> window. This can be found on the <i>Tools</i> menu. At this time, two preferences can be changed:
  1. The ability to toggle AutoComplete on and off on the Game Info Window.
  2. When opening Google Sheets after an export, the URL can now be customized to open to a specific sheet.
  
4-16-2023
- On the main window, the <b>System</b> column will hide when a specific system is selected.
- Fixed a bug with sorting columns on the Wish List window.

4-2-2023
- Added an <b>Edit Lists</b> window. This will allow you to rename System, Genre, and Company fields. You can find it by clicking on <i>Tools > Lists> Edit Lists</i>.

4-1-2023
- The default <b>Systems</b> and <b>Genres</b> lists are now optional. They can be added via the <i>Tools</i> menu, or when the database is opened for the first time. 

3-30-2023
- Added <b>Created</b> and <b>Updated</b> timestamps. They are displayed on the status bar of the Game Info window.

3-29-2023
- Fixed a bug in the <b>Highest Playtime</b> and <b>Total Games</b> graphs.

3-22-2023
- Added a <b>Date Started</b> field. On the main window, the <b>Total Days</b> column will automatically calculate the difference between <b>Date Started</b> and <b>Date Completed</b>.

3-20-2023
- Added a Backup/Restore feature. This can be found in <b>Tools > Backup/Restore Database</b>.
- A backup of the database is still created upon startup. However, you can now restore this backup by clicking <b>Tools > Backup/Restore Database > Restore Auto-Backup</b>.

3-14-2023
- A backup of the vgames.db database file is now created on startup. The file is called <b>vgames.old.db</b>.

3-13-2023
- Added a hidden window that allows you to execute SQL queries. To access it, hold down CTRL and right-click on the "Tools" button.

2-9-2023
- Added a "Region" field.

2-5-2023
- Fixed a few bugs in the Hangman mini-game.

2-4-2023
- Added a Hangman mini-game.
- Minor UI changes on the main window.

1-28-2023
- Filters and window state will now save on exit.
- Game count now shows total games.
- Added a "Reset Filter" button.

1-7-2023
- Fixed the "Move to Database" button on Wish List.

1-4-2023
- Added a "View" selection on the main window to filter between Game Info and Stats.
- Added a "Rating" field.
- All fields can now be left blank (excluding "System" and Title.")

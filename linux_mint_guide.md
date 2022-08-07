# Linux Mint Setup Guide

This guide has been tested on Linux Mint 20.3 ["Una"](https://www.linuxmint.com/edition.php?id=292). May work on other versions.

## About

## Getting Started

### Prerequisites <!-- optional -->

**Installed Linux Mint 20.3+**

Download Linux Mint ISO from [linuxmint.com](https://linuxmint.com/). Follow the default installation instructions.

## Usage <!-- optional -->

There are 2 parts to the tweaks: running the script & manual configuration. Manual configuration is necessary as I'm too lazy to find the specific gsettings to configure everything via a script.

The script is divided into 5 sections:

- Basics
- MacOS Theme
- [Optional] Additional Configurations: Pretty prompt, aliases, better autocompletion.
- Extras: Command line utilities.
- Apps: VLC, VS Code.

### Executing the Script

1. Launch Firefox.
2. Download `./install.sh` & place in user home directory (`~`).
3. Run the following commands. For `./install.sh`, it is recommended to agree to all the optional features, but the script will work fine even if not.
   - ```sh
     chmod ug+x ./install.sh
     ./install.sh
     ```

### Manual Configurations

*NOTE: The "Windows" key is referred to as the "Super" key.*

*NOTE: Launch the Menu via the Super key.*

**Applying MacOS Theme**

1. Menu -> Themes
2. Select "WhiteSur-Dark" for "Icons", "Applications", & "Desktop".
3. Select "WhiteSur-Cursors" for "Mouse Pointer".
4. Menu -> Windows
5. Select "Left" for "Buttons Layout".
6. Under "Alt-Tab" group, select "Coverflow (3D)" for "Alt-Tab Switcher Style".

**Menu Bar**

1. Right-click panel, then move panel to top.
2. Menu -> Panel. Reduce "Panel Height" to 25.
3. Menu -> Applets.
4. Disable "Menu", "Show Desktop", & "Grouped Window List". We will be replacing the default Menu.
5. Configure "Calendar". Enable "Use a Custom Date Format", & type `%B %e %H:%M` for the "Date Format". 
6. Under "Download" group, download "Cinnamenu".
7. Under "Manage" group, enable "Cinnamenu".
8. Configure "Cinnamenu":
   - Select "Top" for "Sidebar Location".
   - Disable "Show Bookmarks and Places", "Show Recent Items".
   - Under "Search", select "None" for "Web Search Option".
   - Disable "Web Search Suggestions".
   - Under "Appearance", enable "Use a Custom Icon".
   - Decrease "Applications Grid Icon Size (Pixels)" to 32.
9. Right-click panel, then enable "Panel Edit Mode". Drag Cinnamenu to the left. Disable "Panel Edit Mode".

**Plank (Dock)**

1. Menu -> Plank
2. Ctrl Right-click the Plank, then select "Theme-Dark" for "Theme".
3. [Optional] Decrease "Icon Size" to 32.
4. Under "Docklets" group, drag "Trash" to Plank.
5. Menu -> Startup Applications. We will be adding Plank to startup.
6. Add -> Choose Application -> Plank
7. [Optional] Add your applications to Plank.

**File Menu (Nautilus)**

1. Menu -> Preferred Applications
2. Select "Nautilus" for "File Manager". If 2 "Files" are shown, select the 2nd option.
3. [Optional] Configure other preferred applications here.

**Firefox**

1. Firefox -> Application Menu -> More Tools -> Customize Toolbar
2. Drag "New Tab" button to the right of the address bar.
3. Uncheck "Title Bar" at the bottom.
4. [Optional] Additional Firefox customisation.

**[Optional] Terminator**

1. Edit `~/.config/terminator/config`:
   - Replace `[[default]]` contents with:
   - ```
      icon_bell = False
      background_color = "#282c34"
      background_darkness = 0.95
      background_type = transparent
      cursor_color = "#bbbbbb"
      foreground_color = "#abb2bf"
      show_titlebar = False
      scrollbar_position = hidden
      palette = "#000000:#eb6e67:#95ee8f:#f8c456:#6eaafb:#d886f3:#6cdcf7:#b2b2b2:#50536b:#eb6e67:#95ee8f:#f8c456:#6eaafb:#d886f3:#6cdcf7:#dfdfdf"
      use_system_font = False
      copy_on_selection = True
     ```
2. Menu -> Preferred Applications
3. Select "Terminator" for "Terminal".

**[Optional] Fonts**

1. Menu -> Font Selection
2. Select "DejaVu Sans Book" font for "Default Font", "Desktop Font", "Document Font", "Window Title Font".
3. Select "DejaVu Sans Mono Book" font for "Monospace Font".

**[Optional] gTile (Window Tiler)**

1. Download `gTile_config.json`.
2. Menu -> Extensions -> "Download" group
3. Download & enable gTile.
4. Click "More Options", then "Import From a File", & select `gTile_config.json`.

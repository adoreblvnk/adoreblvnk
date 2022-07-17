# Linux Mint Guide

work in progress

## Pre-Installation

Linux Mint 20.3 "Una" Cinnamon

## Installation

**Multimedia Codecs**

1. select Install Multimedia Codecs.

**Who are you?**

1. [Optional] enable Encrypt My Home Folder.

## Post Installation

### Basics

_NOTE: all commands are executed in home directory unless specified._

**Get Latest Updates**

    sudo apt update && sudo apt upgrade --with-new-pkgs

**[Optional] Install Drivers**

1. System Settings -> install drivers from Driver Manager

**Install Basic Utils**

    sudo apt install apt-transport-https ca-certificates curl software-properties-common

**Install Git**

    sudo apt install git
    git config --global user.email "<you@example.com>"
    git config --global user.name "<Your Name>"

1. [Optional] add Git logline alias:
   - ```
     git config --global alias.logline "log --graph --pretty=format:'%Cred%h%C(yellow)%d %Creset%s %C(bold blue)<%an>'"
     ```

**Install Python 3.9**

    sudo add-apt-repository ppa:deadsnakes/ppa
    sudo apt update
    sudo apt install python3.9 python3-pip python3.9-venv

1. [Optional] see **Bash Aliases** in [[Optional] QoL (Quality of Life)](#optional-qol-quality-of-life) for adding Python aliases.

### MacOS Theme

**Basics**

1. right click Panel -> select Move -> move to top
2. select Applets:
   - Downloads -> download `cinnamenu` from Search
   - Manage -> enable Cinnamenu
   - [Optional] Configure -> Layout And Content:
     - select Top for Sidebar Location
     - disable Show Favorites On Sidebar, Show Bookmarks And Places, & Show Recent Items.
   - [Optional] Search:
     - select None for Web Search Option
     - disable Web Search Suggestions
   - Appearance:
     - enable Use A Custom Icon.
     - select Panel Icon -> search for `start-here` -> Select
     - Panel Text -> type "Application Menu"
     - Applications Grid Icon Size -> 48
3. enable Panel Edit Mode:
   - select Remove 'Menu', Remove 'Show Desktop', Remove 'Show Group Window List'.
   - move Cinnamenu to the left.
4. disable Panel Edit Mode.
5. Panel Settings -> modify Panel Height to 22
6. select Applets -> configure Calendar -> enable Use A Custom Date Format -> type `%B %e %H:%M` into Date Format
7. System Settings -> Windows:
   - Buttons Layout -> select Left
   - Alt-Tab -> Alt-Tab Switcher Style -> Icons Only

**Transparent Taskbar**

```sh
# install polib dependency.
# https://github.com/izimobil/polib
pip install polib
git clone https://github.com/germanfr/cinnamon-transparent-panels.git
cd cinnamon-transparent-panels/ && ./utils.sh install
```

1. System Settings -> Extensions -> Manage -> enable Transparent Panels
2. Configure:
   - Type Of Transparency -> Semi-transparent
   - enable Use Current Theme Styles.

**MacOS Theme Set**

```sh
# WhiteSur GTK Theme
git clone https://github.com/vinceliuice/WhiteSur-gtk-theme.git
cd WhiteSur-gtk-theme/ && ./install.sh
# WhiteSur Icon Theme
git clone https://github.com/vinceliuice/WhiteSur-icon-theme.git
cd WhiteSur-icon-theme/ && ./install.sh
# WhiteSur Cursors
git clone https://github.com/vinceliuice/WhiteSur-cursors.git
cd WhiteSur-cursors/ && sudo ./install.sh
```

3. System Settings -> Themes:
   - Window Borders -> WhiteSur-Dark
   - Icons -> WhiteSur-dark
   - Controls -> WhiteSur-Dark
   - Mouse Pointer -> WhiteSur-cursors
   - Desktop -> WhiteSur-Dark

**WhiteSur Firefox Theme**

    git clone https://github.com/vinceliuice/WhiteSur-firefox-theme.git
    cd WhiteSur-firefox-theme/ && ./install.sh

1. Firefox -> Customize Toolbar -> drag New Tab into titlebar instead of tab-switcher

**Plank (Dock)**

```sh
# https://launchpad.net/plank
sudo apt install plank
cp -r ~/WhiteSur-gtk-theme/src/other/plank/theme-Light ~/WhiteSur-gtk-theme/src/other/plank/theme-Dark ~/.local/share/plank/themes
```

1. launch Plank.
2. control + right click dock -> Preferences:
   - Theme -> select Theme-Dark
   - Icon Size -> select 32
   - enable Icon Zoom -> select 115
   - Docklets -> drag Trash to bottom right
3. System Settings -> Startup Applications -> Add -> Choose Application -> select Plank

**Nautilus (File Manager)**

```sh
# https://gitlab.gnome.org/GNOME/nautilus
sudo apt install nautilus
```

1. System Settings -> Preferred Applications -> File manager -> select the 2nd Files from the dropdown

### [Optional] Additional Tweaks

**DejaVu Font**

1. System Settings -> Font Selection:
   - Default Font -> DejaVu Sans Book
   - Desktop Font -> DejaVu Sans Book
   - Monospace Font -> DejaVu Sans Mono Book
   - Window Title Font -> DejaVu Sans Book

**GTile**

1. System Settings -> Extensions -> Download -> gTile
2. Manage -> enable gTile
3. Configure -> Hotkeys
   - Global Hotkey For gTile -> Super+W for activator
4. Layout:
   - |       Layout        | Columns | Rows |
     | :-----------------: | :-----: | :--: |
     | Layout For Button 1 |    1    |  1   |
     | Layout For Button 2 |  1, 1   |  1   |
     | Layout For Button 3 | 1, 1, 1 |  1   |
     | Layout For Button 4 |  1, 1   | 1, 1 |

## Utilities & Additional

### Apps

**VLC**

```sh
# https://www.videolan.org/vlc/
sudo apt update
sudo apt install vlc
```

1. System Settings -> Preferred Applications:
   - Music -> VLC Media Player
   - Video -> VLC Media Player

**VS Code**

1. Download from [code.visualstudio.com/download](https://code.visualstudio.com/download).
2. `sudo dpkg -i ~/Downloads/<vs_code>.deb`
3. System Settings -> Preferred Applications -> Plain Text -> Visual Studio Code

**qBittorrent**

```sh
# https://www.qbittorrent.org/
sudo apt update
sudo apt install qbittorrent
```

**Docker**

```sh
sudo apt install docker.io docker-compose
sudo systemctl start docker
# or use `sudo systemctl enable --now docker` to start on boot.
# execute docker commands without using sudo by adding user to docker group.
sudo usermod -aG docker <user_id>
```

**Microsoft Fonts**

```sh
sudo apt install ttf-mscorefonts-installer
```

**Bitwarden**

1. download the AppImage from [bitwarden.com](https://bitwarden.com/download/).

**Discord**

1. download from [discord.com](https://discord.com/download) & install.

### [Optional] QoL (Quality of Life)

**Tree**

```sh
# https://gitlab.com/OldManProgrammer/unix-tree
sudo apt install tree
```

**Bash Prompt (w/ Git Branch)**

```sh
# downloading git-prompt.sh from https://github.com/git/git & creating ~/.git-prompt file.
curl https://raw.githubusercontent.com/git/git/master/contrib/completion/git-prompt.sh > ~/.git-prompt.sh
# customising bash prompt.
echo "
# bash prompt w/ git branch
source ~/.git-prompt.sh
PS1='${debian_chroot:+($debian_chroot)}'
# add username
PS1+='\e[1;32m\u'
# add working directory
PS1+=' \e[0;33m\w'
# add git branch if exists
PS1+='\e[1;34m\$(__git_ps1)'
# prompt symbol
PS1+=' \e[1;35m\\$'
# switch back to white for command
PS1+=' \e[00m'" \
>> ~/.bashrc && source ~/.bashrc
```

**Bash Aliases**

```sh
echo "
# bash aliases
alias c=clear" \
>> ~/.bashrc
```

1. prerequisite: **Install Python 3.9** in [Basics](#basics):
   - for Python 3.9+:
      - add the following to `bash aliases` in `~/.bashrc`:
        - ```sh
          alias python=python3.9
          alias py=python3.9
          ```

**Bash Better Auto-completion**

```sh
# file ~/.inputrc should not exist.
echo \
# bash better auto-completion
set show-all-if-ambiguous on
set completion-ignore-case on
" > ~/.inputrc
```

**trash-cli**

```sh
# https://github.com/andreafrancia/trash-cli
sudo apt install trash-cli
```

### [Optional] Fun

**Neofetch**

    sudo apt update
    sudo apt install neofetch

**Asciiquarium**

```sh
# https://robobunny.com/projects/asciiquarium/html/
# https://github.com/YtvwlD/asciiquarium-debian
sudo add-apt-repository ppa:ytvwld/asciiquarium
sudo apt update && sudo apt install asciiquarium
```

### [Optional] Hardware

#!/bin/bash
echo "BASICS"

printf "\ngetting latest updates & upgrading . . .\n"
sudo apt-get update && sudo apt-get upgrade -y --with-new-pkgs
printf "\ninstalling multi-media codecs.\n"
sudo apt-get install -y mint-meta-codecs
printf "\ndownloading basic utils.\n"
sudo apt-get install -y apt-get-transport-https ca-certificates software-properties-common

printf "\ninstalling git.\n"
sudo apt-get install -y git
read -p "add Git logline alias (y/n)? " logline_input
if [ $logline_input == "y" ]; then
     git config --global alias.logline "log --graph --pretty=format:'%Cred%h%C(yellow)%d %Creset%s %C(bold blue)<%an>'"
fi

printf "\ninstalling python3.0.\n"
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.9 python3-pip python3.9-venv

printf "\ninstalling Microsoft fonts.\n"
sudo apt-get install -y ttf-mscorefonts-installer


echo "INSTALLING MACOS THEME"

printf "\ninstalling transparent taskbar.\n"
# install polib dependency.
# https://github.com/izimobil/polib
pip install polib
git clone https://github.com/germanfr/cinnamon-transparent-panels.git
cd cinnamon-transparent-panels/ && ./utils.sh install; cd

printf "\ninstalling WhiteSur GTK theme.\n"
git clone https://github.com/vinceliuice/WhiteSur-gtk-theme.git
cd WhiteSur-gtk-theme/ && ./install.sh; cd
printf "\ninstalling WhiteSur icon theme.\n"
git clone https://github.com/vinceliuice/WhiteSur-icon-theme.git
cd WhiteSur-icon-theme/ && ./install.sh; cd
printf "\ninstalling WhiteSur cursors.\n"
git clone https://github.com/vinceliuice/WhiteSur-cursors.git
cd WhiteSur-cursors/ && sudo ./install.sh; cd
printf "\ninstalling WhiteSur Firefox theme.\n"
git clone https://github.com/vinceliuice/WhiteSur-firefox-theme.git
cd WhiteSur-firefox-theme/ && ./install.sh; cd

printf "\ninstalling plank dock.\n"
# https://launchpad.net/plank
sudo apt-get install -y plank
plank
cp -r ~/WhiteSur-gtk-theme/src/other/plank/theme-Light ~/WhiteSur-gtk-theme/src/other/plank/theme-Dark ~/.local/share/plank/themes

printf "\ninstalling Nautilus file manager.\n"
# https://gitlab.gnome.org/GNOME/nautilus
sudo apt-get install -y nautilus


echo "ENABLE ADDITIONAL CONFIGURATIONS"

read -p "enable additional configurations (eg tree, bash prompt modification, bash auto-completion) (y/n)? " add_conf_input
if [ $add_conf_input == "y" ]; then
    printf "\nmodifying bash prompt.\n"
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

    printf "\nadding aliases.\n"
    echo "
    # bash aliases
    alias c=clear" \
    >> ~/.bashrc && source ~/.bashrc
    if [[ -n $(which python3.9) ]]; then
        echo \
        "alias python=python3.9
        alias py=python3.9" \
        >> ~/.bashrc && source ~/.bashrc
        echo "added aliases for python3.9."
    else
        echo "python3.9 does not exist. skipping its aliases."
    fi

    printf "\nbash better auto-completion.\n"
    if [ ! -f "~/.inputrc" ]; then
        echo "
        # bash better auto-completion
        set show-all-if-ambiguous on
        set completion-ignore-case on
        " > ~/.inputrc
    else
        echo "~/.inputrc file exists. adding bash better autocompletion skipped."
    fi
fi


echo "EXTRAS"

printf "\ninstalling tree.\n"
# https://gitlab.com/OldManProgrammer/unix-tree
sudo apt-get install -y tree

printf "\ninstalling trash-cli.\n"
# https://github.com/andreafrancia/trash-cli
sudo apt-get install -y trash-cli

printf "\ninstalling neofetch.\n"
sudo apt-get install -y neofetch


echo "APPS"

printf "\ninstalling VLC.\n"
sudo apt-get install -y vlc

printf "\ninstalling VS Code.\n"
curl -o code.deb -L http://go.microsoft.com/fwlink/?LinkID=760868
sudo apt install -y ./code.deb
rm -f code.deb
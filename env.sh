#!/bin/bash

option_1 () {
    title="Addon Directory Structure"; echo "Creating $title..."

    BASE_ADDON_DIR="plugin.video.vaultreaming"
    TEMPLATE_DIR="template"

    if [ -d $BASE_ADDON_DIR ]; then
        echo -e "\e[31m<<Directory $BASE_ADDON_DIR, already exists!>>\033[0m"
    else
        mkdir -p "$BASE_ADDON_DIR/resources" && mkdir -p "$BASE_ADDON_DIR/libs"

        cp "$TEMPLATE_DIR/addon.xml" "$BASE_ADDON_DIR/"
        cp "$TEMPLATE_DIR/default.py" "$BASE_ADDON_DIR/"
        cp "$TEMPLATE_DIR/settings.xml" "$BASE_ADDON_DIR/"

        echo -e "\e[32m<<OK>>\033[0m"
    fi
}

option_2 () {
    echo "Look at the comments..."
    # pip3 install...
    # > sudo apt update && sudo apt install python3-pip -y

    # venv install...
    # > sudo apt install python3-venv -y

    # environment...
    # > python3 -m venv .venv
    # > source .venv/bin/activate
    # > deactivate
    # > rm -rf .venv

    # install dependencies...
    # > pip/3 install package_name
    # > pip3 list

    # export dependencies...
    # > pip freeze > requirements.txt

    # install from requirements...
    # > pip install -r requirements.txt
}

while true; do
    clear
    echo -e "========================================\n> OPTIONS <\n========================================\n"
    echo -e "1) Option 1: > Create directory structure <\n"
    echo -e "2) Option 2: > Python Environment <\n"
    echo -e "3) Option 3: >> Exit... <<\n"

    read -p "Select Option: " option
    enter_message="Press [Enter] to continue..."

    case $option in
        1)
            option_1
            read -p "$enter_message"
        ;;
        2)
            option_2
            read -p "$enter_message"
        ;;
        3)
            echo -e "\e[32mOption 3 > Exiting...\033[0m"
            exit
        ;;
        *)
            echo -e "\e[31mInvalid Option!\033[0m\n"
            sleep 1
        ;;
    esac
done
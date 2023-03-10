#!/bin/bash/

foldingpath="$HOME/.folding"
bashrcpath="$HOME/.bashrc"

if [ ! -d "$foldingpath" ]; then
    echo "Creating directory at ${foldingpath}"
    mkdir "$foldingpath"
fi

if [ ! -e "${foldingpath}/folding.sh" ];then
    echo "Adding folding.sh in ${foldingpath}"
    cp "folding.sh" "$foldingpath"
fi

ALIAS="alias preparefold='bash ${foldingpath}/folding.sh'" 
if ! grep -q "$ALIAS" "$bashrcpath"; then
    echo "Adding 'folding.sh' as 'preparefold' alias in your ${bashrcpath}"
    echo $ALIAS >> "$bashrcpath"
fi


if [ ! -e "${foldingpath}/starttext.txt" ]; then
    echo "Copying 'starttext.txt' to ${foldingpath}"
    cp "starttext.txt" "${foldingpath}" 
fi

starttext="clear && cat $foldingpath/starttext.txt"
if ! grep -q "$starttext" "$bashrcpath"; then
    echo "Adding starttext to $bashrcpath"
    echo "$starttext" >> "$bashrcpath"
fi


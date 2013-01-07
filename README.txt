This is a pretty simple browser regular expressions fuzzer. When launching, it
generates files and writes them to folder "samples/". After files have been
generated, open launch.html in your browser and fuzz.

main.py - generator:
regex-fuzz>main.py

    Options:
        -n      amount of samples to generate
        -p      fuzz pattern attibute for input tag
        -d      fuzz database (if available for browser)
        -j      fuzz JavaScript regex
        -e      preferred encoding

    At least one of fuzzing options (p,d,j) must be specified.

cleanup.py - this script will erase all files in folder "samples/"
log.php - logger that will write log files to folder "logs/"

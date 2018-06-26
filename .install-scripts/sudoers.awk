# sudoers.awk - Ensure password free sudo for the admin group

# Instructions are separated by blank lines
BEGIN { RS = "" ; FS = "\n" }
{
    if ($2  ~ "^%admin") next
    print $1
    if ($2 != "") print $2
    print ""

    if ($2 ~ "^%sudo") {
        print "# Members of the admin group may gain root privileges"
        print "%admin ALL=(ALL) NOPASSWD:ALL"
        print ""
    }
}

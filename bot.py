from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import datetime
import sched
import time

# Constants

PATH = "C:\Program Files (x86)\chromedriver.exe"
LOCATIONS = {
    "vaughan": "655",
    "whitby": "1141",
    "oshawa": "928",
    "milton": "931",
    "markham": "1096",
    "kitchener": "482",
    "gwillimbury": "669",
    "cambridge": "1099",
    "burlington": "1092",
    "burlington_north": "560",
    "barrie": "1052",
    "barrie_cundle": "1178",
    "aurora": "1103"
}

# Pre:          Takes time as an integer
# Post:         Returns time in string format
# Description:  Takes integer from 6-23 and returns it in string format "XX:00 AM/PM"
def convertIntToTime(numTime):
    
    # Prefix for hours with only 1 digit and postfix for am/pm
    preFix = "0"
    postFix = "AM"

    # Sets baseline for regular time
    regTime = numTime

    # Checks if time is greater than 12 to change it back to miltiary time
    if numTime > 12:
        regTime = numTime - 12

    # Checks if time
    if numTime >= 12:
        postFix = "PM"

    if regTime >= 10 and regTime <= 12:
        preFix = ""

    return preFix + str(regTime) + ":00 " + postFix

# Pre:          Takes time to look for 
# Post:         Returns True if slot was found
# Description:  Returns true if slot was booked
def reserve(res_time):

    # Table element and rows in table
    table = driver.find_element_by_id("tblSchedule")
    rows = table.find_elements_by_tag_name("tr")
    found = False

    # Checks if there is a table
    if (len(rows) == 0):
        found = False

    # Loops through every element in rows
    for row in rows:
        # Puts the elements of the row into a list
        col = row.find_elements_by_tag_name("td")

        # Checks if the row isn't empty to avoid error as some rows come out empty
        if col != []:
            # Checks if requested time equals to one of the columns and if the type of slot matches requested slot
            if res_time == col[0].text:
                if col[2].text == "RESERVED":
                    print("Time for ", res_time, " already reserved.")
                    found = False
                else:
                    found = True
                    col[2].click()

    # Checks if the time slot was found, notifies console and reserves slot
    if found:
        print("Found slot at " + res_time)

        try:
            element = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='btn btn-default' and text()='OK']"))
            )

            # Clicks OK when prompted after reserve
            okBtn = driver.find_element_by_xpath("//button[@class='btn btn-default' and text()='OK']")
            okBtn.click()
        except:
            print("Something went wrong...")
            found = False
        
        try:
            # wait for loading element to appear
            # - required to prevent prematurely checking if element
            #   has disappeared, before it has had a chance to appear
            WebDriverWait(driver, 5
                ).until(EC.presence_of_element_located((By.ID, "ctl00_MainContent_ucScheduleBooking_imgPrgress")))

            # then wait for the element to disappear
            WebDriverWait(driver, 10
                ).until_not(EC.presence_of_element_located((By.ID, "ctl00_MainContent_ucScheduleBooking_imgPrgress")))

        except:
            driver.refresh()
            print("Connection timed out...")
            return False

        try:
            find = driver.find_element_by_id("ctl00_MainContent_ucScheduleBooking_lblErrorMessage")
            print("Reservations for this day already full")
            return False
        except:
            print("Booked:\t" + " @ ", res_time, " successfully...")
            return True

    else:
        print(res_time, " is not available..")

    return found
    
def login(username, password):

    # Grabs form elements username, password, and sign in button
    userNameTxt = driver.find_element_by_id("txtUser")
    passWordTxt = driver.find_element_by_id("txtPassword")
    signInBtn = driver.find_element_by_id("ctl00_MainContent_Login1_btnLogin")

    # Fills in form with specified username and password
    userNameTxt.send_keys(username)
    passWordTxt.send_keys(password)

    # Clicks sign in button
    signInBtn.click()

    print("Login successful")

def isLoggedIn():
    try:
        userNameTxt = driver.find_element_by_id("ctl00_MainContent_Login1_btnLogin")
        return False
    except:
        return True

# BEGGINING OF MENU #

print("Login to LA Fitness")
my_username = input("Username:\t")
my_password = input("Password:\t")

print("Select times in priority sequence, for this you must type in the times you want in priority so if you want to get 5pm first and 3pm incase 5pm isn't available you must type in '17 15'\nNotice how it is in military time. Times must be delimited by spaces.")

times_string = input("Time:\t")
times = times_string.split(" ")
times = list(map(int, times))
times = list(map(convertIntToTime, times))

print("Now select the club you would like to make an appointment for:")
for places in LOCATIONS:
    print(places)

location = input("Type the exact name from the list above (capital sensitive):\t")

current_location = LOCATIONS.get(location)
club_page = "https://lafitness.com/Pages/ClubReservation.aspx?clubID=" + current_location

# END OF MENU #

# OPEN CHROME

driver = webdriver.Chrome(PATH)

# OPEN LA FITNESS RESERVATIONS PAGE

driver.get(club_page)

print("Attempting to search for times in", location)

startTime = time.time()
while True:
    currentTime = datetime.datetime.now()
    print("Refresh @:\t" + str(currentTime))
    
    try:
        if isLoggedIn():
            print("Logged in, checking schedule...")

            for timeSlot in times:
                reserve(timeSlot)

        else:
            print("User has been logged out, logging back in...")
            login(my_username, my_password)
            driver.get(club_page)
            continue
    except:
        driver.get(club_page)
        print("Something went wrong...")

    # Program sleeps for 5 seconds before refreshing
    time.sleep(3.0 - ((time.time() - startTime) % 3.0))
    driver.refresh()


driver.close()
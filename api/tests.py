from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from api.models import CustomUser
import requests

class AccountTests(StaticLiveServerTestCase):

    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)  # Default waiting time
        self.frontend_url = "http://localhost:5173"  # Frontend URL

        # Ensure no test users exist to prevent conflicts
        CustomUser.objects.filter(username__in=["testuser", "testuser1"]).delete()

    def tearDown(self):
        self.driver.quit()

    def handle_alert(self):
        """Dismiss any open alert and return its text."""
        try:
            WebDriverWait(self.driver, 10).until(EC.alert_is_present())  # Wait for alert
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            return alert_text
        except Exception as e:
            print(f"No alert found: {e}")
            return None

    def create_user(self, username, email, password, dob):
        """Helper function to create a user via the signup page."""
        CustomUser.objects.filter(username=username).delete()
        CustomUser.objects.filter(email=email).delete()
        self.driver.get(f"{self.frontend_url}/signup/")

        # Fill in signup form
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']"))
        )
        self.driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys(username)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Name']").send_keys(f"{username} User")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Email']").send_keys(email)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Date of Birth']").send_keys(dob)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(password)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Confirm Password']").send_keys(password)

        # Select hobbies
        self.driver.find_element(By.XPATH, "//input[@value='1']").click()
        self.driver.find_element(By.XPATH, "//input[@value='2']").click()
        self.driver.find_element(By.XPATH, "//input[@value='3']").click()

        # Submit form
        self.driver.find_element(By.XPATH, "//button[text()='Sign Up']").click()

        # Handle success alert
        alert_text = self.handle_alert()
        self.assertIn("Signup successful!", alert_text)

    def login_user(self, username, password):
        """Helper function to log in a user."""
        self.driver.get(f"{self.frontend_url}/login/")
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username']"))
        )
        self.driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys(username)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(password)
        self.driver.find_element(By.XPATH, "//button[text()='Login']").click()

        # Wait for successful login
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Logged in as:')]"))
        )
        self.assertIn(f"Logged in as: {username}", self.driver.page_source)

    def test_friend_request(self):
        """Test sending and accepting a friend request."""
        # Create test users
        self.create_user("testuser4", "testuser4@example.com", "testpassword", "01/01/2000")
        self.create_user("testuser5", "testuser5@example.com", "testpassword", "01/01/2000")

        # Log in as testuser4 and send a friend request to testuser5
        self.login_user("testuser4", "testpassword")
        self.driver.get(f"{self.frontend_url}/similar-users/")

        # Locate the card for testuser5 and send a friend request
        user_card = self.driver.find_element(By.XPATH, "//h3[text()='testuser5 User']/..")
        send_request_button = user_card.find_element(By.XPATH, ".//button[contains(text(), 'Send Friend Request')]")
        self.driver.execute_script("arguments[0].scrollIntoView();", send_request_button)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(send_request_button))
        send_request_button.click()

        # Handle success alert
        alert_text = self.handle_alert()
        self.assertIsNotNone(alert_text, "Expected an alert after sending the friend request, but none was found.")
        self.assertIn("Friend request sent successfully!", alert_text)

        # Log out testuser4
        self.driver.find_element(By.XPATH, "//button[text()='Logout']").click()
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(f"{self.frontend_url}/login/")
        )

        # Log in as testuser5 and accept the friend request
        self.login_user("testuser5", "testpassword")
        self.driver.get(f"{self.frontend_url}/friend-requests/")

        # Accept the friend request
        friend_request_card = self.driver.find_element(
            By.XPATH, "//p[contains(text(), 'testuser4 sent you a friend request.')]"
        )
        accept_button = friend_request_card.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        self.driver.execute_script("arguments[0].scrollIntoView();", accept_button)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(accept_button))
        accept_button.click()

        # Handle success alert
        alert_text = self.handle_alert()
        self.assertIsNotNone(alert_text, "Expected an alert after accepting the friend request, but none was found.")
        self.assertIn("Friend request accepted successfully!", alert_text)

        # Verify the friend request is no longer visible
        with self.assertRaises(Exception):
            self.driver.find_element(By.XPATH, "//p[contains(text(), 'testuser4 sent you a friend request.')]")

        # Log out testuser5
        self.driver.find_element(By.XPATH, "//button[text()='Logout']").click()
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(f"{self.frontend_url}/login/")
        )

    def edit_user_profile(self, name, email, dob):
        """Helper function to edit the user's profile."""
        # Navigate to the user's profile edit page
        self.driver.get(f"{self.frontend_url}")

        # Wait for the "Edit Profile" button (Assuming there's a button that opens the modal)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Edit Profile']"))).click()

        # Wait for the modal to open and the form elements to be visible
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='modal-content']")))

        # Wait for the page to load and the elements to be present
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='name']")))

        # Edit profile fields
        self.driver.find_element(By.XPATH, "//*[@id='name']").clear()
        self.driver.find_element(By.XPATH, "//*[@id='name']").send_keys(name)
        
        self.driver.find_element(By.XPATH, "//*[@id='email']").clear()
        self.driver.find_element(By.XPATH, "//*[@id='email']").send_keys(email)
        
        self.driver.find_element(By.XPATH, "//*[@id='dob']").clear()
        self.driver.find_element(By.XPATH, "//*[@id='dob']").send_keys(dob)
        
        # Submit the form
        self.driver.find_element(By.XPATH, "//button[text()='Save Changes']").click()

        # Verify the changes
        WebDriverWait(self.driver, 10).until(
            lambda driver: name in driver.page_source and email in driver.page_source and dob in driver.page_source
        )

    def test_signup_and_login(self):
        """Test the user can sign up and log in."""
        # UK formatted dob (DD/MM/YYYY)
        self.create_user("testuser", "testuser@example.com", "testpassword", "15/12/1999")
        self.login_user("testuser", "testpassword")

    def test_edit_profile(self):
        """Test the user can edit their profile information."""
        #  dob (DD/MM/YYYY)
        self.create_user("testuser1", "testuser1@example.com", "testpassword", "25/04/1990")
        self.login_user("testuser1", "testpassword")
        self.edit_user_profile("Updated Test User", "updatedemail@example.com", "15/05/1995")  

    def test_filter_by_age(self):
        """Test filtering users by age."""
        # Create users with different ages using UK formatted dob
        self.create_user("younguser", "younguser@example.com", "testpassword", "01/01/2005")  # Young user
        self.create_user("olduser", "olduser@example.com", "testpassword", "01/01/1980")  # Old user
        self.create_user("testuser2", "testuser2@example.com", "testpassword", "01/01/1990")  # Neutral age user
        self.login_user("testuser2", "testpassword")

        # Navigate to the users page
        self.driver.get(f"{self.frontend_url}/similar-users/")

        # Wait for the filter elements to load
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "//*[@id='min-age']")))

        # Set filters (Assuming there's a filter input field for age)
        self.driver.find_element(By.XPATH, "//*[@id='min-age']").send_keys("20")
        self.driver.find_element(By.XPATH, "//*[@id='max-age']").send_keys("30")

        # Wait for the data to update after the input (ensure the filter updates the results)
        WebDriverWait(self.driver, 10).until(
            lambda driver: "younguser" in driver.page_source and "olduser" not in driver.page_source
        )

        # Verify only users within the age range appear
        self.assertIn("younguser", self.driver.page_source)
        self.assertNotIn("olduser", self.driver.page_source)

    def delete_user(self, username):
        """Delete a test user using the API."""
        response = requests.delete(f"{self.api_url}/delete-user/{username}/")
        assert response.status_code == 200, f"Failed to delete user {username}: {response.text}"

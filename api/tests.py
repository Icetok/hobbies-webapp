from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase


class AccountTests(StaticLiveServerTestCase):
    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.frontend_url = "http://localhost:5173"  # Frontend URL

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

    def login(self, username, password):
        """Reusable method to log in a user."""
        # Navigate to login page
        self.driver.get(f"{self.frontend_url}/login/")
        
        # Fill out login form
        self.driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys(username)
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys(password)
        
        # Submit form
        self.driver.find_element(By.XPATH, "//button[text()='Login']").click()
        
        # Wait for successful login
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Logged in as:')]"))
        )
        self.assertIn(f"Logged in as: {username}", self.driver.page_source)
        
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from api.models import CustomUser

class AccountTests(StaticLiveServerTestCase):
    def setUp(self):
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.driver.implicitly_wait(10)
        self.frontend_url = "http://localhost:5173"  # Frontend URL

        # Ensure no test users exist
        CustomUser.objects.filter(username="testuser").delete()

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

    def test_signup(self):
        # Navigate to signup page
        self.driver.get(f"{self.frontend_url}/signup/")
        
        # Fill out signup form
        self.driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys("testuser")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Name']").send_keys("Test User")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Email']").send_keys("testuser@example.com")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Date of Birth']").send_keys("2000-01-01")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys("testpassword")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Confirm Password']").send_keys("testpassword")
        
        # Select hobbies (checkboxes with values 1, 2, 3)
        self.driver.find_element(By.XPATH, "//input[@value='1']").click()
        self.driver.find_element(By.XPATH, "//input[@value='2']").click()
        self.driver.find_element(By.XPATH, "//input[@value='3']").click()
        
        # Submit form
        self.driver.find_element(By.XPATH, "//button[text()='Sign Up']").click()
        
        # Handle success alert
        alert_text = self.handle_alert()
        self.assertIsNotNone(alert_text, "Expected an alert after signup, but none was found.")
        self.assertIn("Signup successful!", alert_text)

        # Wait for redirection to login page
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(f"{self.frontend_url}/login/")
        )

        # Assert successful redirection
        self.assertIn("Login", self.driver.page_source)

    def test_login(self):
        # Create a user via the signup test
        try:
            self.test_signup()
        except AssertionError as e:
            self.fail(f"Signup failed during login test setup: {e}")

        # Navigate to login page
        self.driver.get(f"{self.frontend_url}/login/")
        
        # Fill out login form
        self.driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys("testuser")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys("testpassword")
        
        # Submit form
        self.driver.find_element(By.XPATH, "//button[text()='Login']").click()
        
        # Handle success alert (if any)
        alert_text = self.handle_alert()
        if alert_text:
            print(f"Login alert: {alert_text}")

        # Wait for redirection to main page
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(f"{self.frontend_url}/")
        )

        # Assert successful login
        self.assertIn("Logged in as: testuser", self.driver.page_source)

    def test_friend_request(self):
        # Log in as the first user and send a friend request to the second user
        self.driver.get(f"{self.frontend_url}/login/")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys("testuser1")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys("testpassword")
        self.driver.find_element(By.XPATH, "//button[text()='Login']").click()

        # Wait for redirection to the main page
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(f"{self.frontend_url}/")
        )

        # Navigate to the similar users page
        self.driver.get(f"{self.frontend_url}/similar-users/")

        # Find the button corresponding to the second user and click it to send a friend request
        user_card = self.driver.find_element(By.XPATH, "//h3[text()='Test User 2']/..")
        send_request_button = user_card.find_element(By.XPATH, ".//button[contains(text(), 'Send Friend Request')]")

        # Scroll into view and click
        self.driver.execute_script("arguments[0].scrollIntoView();", send_request_button)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(send_request_button))
        send_request_button.click()

        # Handle success alert
        alert_text = self.handle_alert()
        self.assertIsNotNone(alert_text, "Expected an alert after sending the friend request, but none was found.")
        self.assertIn("Friend request sent successfully!", alert_text)

        # Log out the first user
        self.driver.find_element(By.XPATH, "//button[text()='Logout']").click()

        # Log in as the second user to accept the friend request
        self.driver.get(f"{self.frontend_url}/login/")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys("testuser2")
        self.driver.find_element(By.XPATH, "//input[@placeholder='Password']").send_keys("testpassword")
        self.driver.find_element(By.XPATH, "//button[text()='Login']").click()

        # Wait for redirection to the main page
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(f"{self.frontend_url}/")
        )

        # Navigate to the friend requests page
        self.driver.get(f"{self.frontend_url}/friend-requests/")

        # Locate the specific friend request from the first user
        friend_request_card = self.driver.find_element(
            By.XPATH, "//p[contains(text(), 'testuser1 sent you a friend request.')]"
        )
        accept_button = friend_request_card.find_element(By.XPATH, ".//button[contains(@class, 'btn-success')]")

        # Scroll into view and click
        self.driver.execute_script("arguments[0].scrollIntoView();", accept_button)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(accept_button))
        accept_button.click()

        # Handle success alert
        alert_text = self.handle_alert()
        self.assertIsNotNone(alert_text, "Expected an alert after accepting the friend request, but none was found.")
        self.assertIn("Friend request accepted successfully!", alert_text)

        # Verify the friend request is no longer visible
        with self.assertRaises(Exception):
            self.driver.find_element(By.XPATH, "//p[contains(text(), 'testuser1 sent you a friend request.')]")

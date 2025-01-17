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
        self.driver.implicitly_wait(10)
        self.frontend_url = "http://localhost:5173"  # Frontend URL
        self.api_url = "http://127.0.0.1:8000/api"  # Backend API URL

    def tearDown(self):
        # Delete test users via API
        self.driver.quit()

    def create_user(self, username, name, email, password, date_of_birth, hobbies):
        """Create a test user using the API."""
        response = requests.post(
            f"{self.api_url}/signup/",
            json={
                "username": username,
                "name": name,
                "email": email,
                "password1": password,
                "password2": password,
                "date_of_birth": date_of_birth,
                "hobbies": hobbies,
            },
        )
        assert response.status_code == 200, f"Failed to create user {username}: {response.text}"

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
        
    def delete_user(self, username):
        """Delete a test user using the API."""
        response = requests.delete(f"{self.api_url}/delete-user/{username}/")
        assert response.status_code == 200, f"Failed to delete user {username}: {response.text}"

    def test_signup(self):
        # Create test users via API
        self.create_user(
            username="testuser1",
            name="Test User 1",
            email="testuser1@example.com",
            password="testpassword",
            date_of_birth="2000-01-01",
            hobbies=[2],
        )
        self.create_user(
            username="testuser2",
            name="Test User 2",
            email="testuser2@example.com",
            password="testpassword",
            date_of_birth="2000-01-01",
            hobbies=[2],
        )
        
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
        self.delete_user("testuser")

    def test_login(self):
        self.create_user(
            username="testuser3",
            name="Test User 3",
            email="testuser3@example.com",
            password="testpassword",
            date_of_birth="2000-01-01",
            hobbies=[1],
        )

        # Navigate to login page
        self.driver.get(f"{self.frontend_url}/login/")
        # Fill out login form
        self.driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys("testuser3")
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
        self.assertIn("Logged in as: testuser3", self.driver.page_source)

        # Log out the user
        self.driver.find_element(By.XPATH, "//button[text()='Logout']").click()
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(f"{self.frontend_url}/login/")
        )
        self.delete_user("testuser3")

    def test_friend_request(self):
        # Log in as the first user and send a friend request
        self.login("testuser1", "testpassword")
        self.driver.get(f"{self.frontend_url}/similar-users/")

        # Locate the card for testuser2 and send a friend request
        user_card = self.driver.find_element(By.XPATH, "//h3[text()='Test User 2']/..")
        send_request_button = user_card.find_element(By.XPATH, ".//button[contains(text(), 'Send Friend Request')]")
        self.driver.execute_script("arguments[0].scrollIntoView();", send_request_button)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(send_request_button))
        send_request_button.click()

        # Handle success alert
        alert_text = self.handle_alert()
        self.assertIsNotNone(alert_text, "Expected an alert after sending the friend request, but none was found.")
        self.assertIn("Friend request sent successfully!", alert_text)

        # Log out testuser1
        self.driver.find_element(By.XPATH, "//button[text()='Logout']").click()

        # Log in as testuser2 and accept the friend request
        self.login("testuser2", "testpassword")
        self.driver.get(f"{self.frontend_url}/friend-requests/")

        # Accept the friend request
        friend_request_card = self.driver.find_element(
            By.XPATH, "//p[contains(text(), 'testuser1 sent you a friend request.')]"
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
            self.driver.find_element(By.XPATH, "//p[contains(text(), 'testuser1 sent you a friend request.')]")
        self.delete_user("testuser1")
        self.delete_user("testuser2")
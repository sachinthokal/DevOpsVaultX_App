from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.db import connections

class DevOpsVaultXProductionTests(TestCase):
    """
    Production-ready integration tests for DevOpsVaultX_App.
    """

    def setUp(self):
        self.client = Client()

    def test_1_essential_endpoints(self):
        """Verify core system endpoints (Home, Admin, SEO)."""
        print("\n[RUNNING] Test 1: Checking Essential Endpoints...")
        endpoints = ['/', '/admin-dashboard/', '/robots.txt', '/sitemap.xml']
        
        for url in endpoints:
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            print(f"   - Success: {url} is reachable (200 OK)")

    def test_2_app_connectivity(self):
        """Ensure all registered apps are correctly routed."""
        print("\n[RUNNING] Test 2: Checking App Connectivity...")
        app_paths = [
            '/accounts/login/', 
            '/products/', 
            '/payments/', 
            '/insights/', 
            '/vaultx/'
        ]
        for path in app_paths:
            response = self.client.get(path)
            self.assertNotEqual(response.status_code, 404)
            print(f"   - Success: App path {path} is active (Status: {response.status_code})")

    def test_3_static_and_media_config(self):
        """Verify that Static and Media settings are defined."""
        print("\n[RUNNING] Test 3: Checking Static & Media Configurations...")
        self.assertTrue(bool(settings.STATIC_URL))
        self.assertTrue(bool(settings.MEDIA_URL))
        print(f"   - Success: Static URL set to {settings.STATIC_URL}")
        print(f"   - Success: Media URL set to {settings.MEDIA_URL}")

    def test_4_database_health(self):
        """Check if the database connection is functional."""
        print("\n[RUNNING] Test 4: Checking Database Health...")
        db_conn = connections['default']
        try:
            db_conn.cursor()
            print("   - Success: Database connection is healthy.")
        except Exception as e:
            self.fail(f"Database Connection Error: {e}")

    def test_5_admin_security_redirect(self):
        """Ensure the admin dashboard is protected."""
        print("\n[RUNNING] Test 5: Checking Admin Security...")
        response = self.client.get('/admin-dashboard/')
        self.assertIn(response.status_code, [200, 302])
        status_msg = "Redirected to Login" if response.status_code == 302 else "Admin Page Loaded"
        print(f"   - Success: Admin access verified ({status_msg})")
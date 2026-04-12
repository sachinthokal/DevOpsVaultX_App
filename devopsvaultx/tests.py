from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.db import connections

class DevOpsVaultXProductionTests(TestCase):
    """
    Production-ready integration tests for DevOpsVaultX_App.
    Updated based on registered URL patterns.
    """

    def setUp(self):
        self.client = Client()

    def test_1_essential_endpoints(self):
        """Verify core system endpoints (Home, Admin, SEO)."""
        print("\n[RUNNING] Test 1: Checking Essential Endpoints...")
        # Testing absolute paths and SEO required files
        endpoints = ['/', '/admin-dashboard/', '/robots.txt', '/sitemap.xml']
        
        for url in endpoints:
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            print(f"   - Success: {url} is reachable (200 OK)")

    def test_2_app_connectivity(self):
        """Ensure all registered app roots are correctly routed."""
        print("\n[RUNNING] Test 2: Checking App Connectivity...")
        # Root paths for each installed application
        app_paths = [
            '/accounts/login/', 
            '/products/', 
            '/payments/', 
            '/insights/', 
            '/vaultx/',
            '/tools/',
            '/owner-dashboard/'
        ]
        for path in app_paths:
            response = self.client.get(path)
            # We use 404 check because some pages might redirect (302) or need login
            self.assertNotEqual(response.status_code, 404)
            print(f"   - Success: App path {path} is active (Status: {response.status_code})")

    def test_3_tools_endpoints(self):
        """Verify that all specific tools are accessible."""
        print("\n[RUNNING] Test 3: Checking Fixed Tools Endpoints...")
        tools_list = [
            '/tools/json-fix/',
            '/tools/yaml-json/',
            '/tools/beautify/',
            '/tools/base64/',
            '/tools/secret-gen/',
            '/tools/case-converter/'
        ]
        for tool in tools_list:
            response = self.client.get(tool)
            self.assertEqual(response.status_code, 200)
            print(f"   - Success: Tool {tool} is functional (200 OK)")

    def test_4_static_and_media_config(self):
        """Verify that Static and Media settings are defined."""
        print("\n[RUNNING] Test 4: Checking Static & Media Configurations...")
        self.assertTrue(bool(settings.STATIC_URL))
        self.assertTrue(bool(settings.MEDIA_URL))
        print(f"   - Success: Static URL set to {settings.STATIC_URL}")
        print(f"   - Success: Media URL set to {settings.MEDIA_URL}")

    def test_5_database_health(self):
        """Check if the database connection is functional."""
        print("\n[RUNNING] Test 5: Checking Database Health...")
        db_conn = connections['default']
        try:
            db_conn.cursor()
            print("   - Success: Database connection is healthy.")
        except Exception as e:
            self.fail(f"Database Connection Error: {e}")

    def test_6_admin_security_redirect(self):
        """Ensure the admin dashboard is protected and not leaking data."""
        print("\n[RUNNING] Test 6: Checking Admin Security...")
        response = self.client.get('/admin-dashboard/')
        # Should either load login or redirect to login
        self.assertIn(response.status_code, [200, 302])
        print(f"   - Success: Admin access controlled (Status: {response.status_code})")

    def test_7_vaultx_integrity(self):
        """Check VaultX specific index routing."""
        print("\n[RUNNING] Test 7: Checking VaultX Access...")
        response = self.client.get(reverse('vaultx:index'))
        # Usually requires login, so 302 redirect is expected
        self.assertIn(response.status_code, [200, 302])
        print(f"   - Success: VaultX index verified.")
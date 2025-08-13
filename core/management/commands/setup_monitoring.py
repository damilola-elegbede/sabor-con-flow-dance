"""
Management command to set up monitoring infrastructure.
SPEC_06 Group C Task 9: Automated monitoring setup.
"""

import logging
import requests
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Set up comprehensive monitoring infrastructure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--setup-uptimerobot',
            action='store_true',
            help='Set up UptimeRobot monitoring',
        )
        parser.add_argument(
            '--test-alerts',
            action='store_true',
            help='Test all alert channels',
        )
        parser.add_argument(
            '--verify-health',
            action='store_true',
            help='Verify all health check endpoints',
        )
        parser.add_argument(
            '--setup-all',
            action='store_true',
            help='Set up all monitoring components',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Setting up comprehensive monitoring infrastructure...')
        )

        if options['setup_all']:
            options['setup_uptimerobot'] = True
            options['test_alerts'] = True
            options['verify_health'] = True

        try:
            if options['verify_health']:
                self._verify_health_endpoints()

            if options['setup_uptimerobot']:
                self._setup_uptimerobot()

            if options['test_alerts']:
                self._test_alerts()

            self.stdout.write(
                self.style.SUCCESS('✅ Monitoring setup completed successfully!')
            )

        except Exception as e:
            logger.error(f"Monitoring setup failed: {str(e)}")
            raise CommandError(f'Monitoring setup failed: {str(e)}')

    def _verify_health_endpoints(self):
        """Verify all health check endpoints are working."""
        self.stdout.write('🔍 Verifying health check endpoints...')
        
        # Health check endpoints to verify
        endpoints = [
            '/health/',
            '/health/simple/',
            '/uptime/',
            '/api/metrics/',
            '/api/monitoring/status/',
        ]
        
        base_url = self._get_base_url()
        
        for endpoint in endpoints:
            try:
                url = f"{base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✅ {endpoint} - OK ({response.status_code})')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️  {endpoint} - {response.status_code}')
                    )
                    
            except requests.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ {endpoint} - Error: {str(e)}')
                )

    def _setup_uptimerobot(self):
        """Set up UptimeRobot monitoring."""
        self.stdout.write('📡 Setting up UptimeRobot monitoring...')
        
        api_key = getattr(settings, 'UPTIMEROBOT_API_KEY', None)
        monitor_url = getattr(settings, 'UPTIMEROBOT_MONITOR_URL', None)
        
        if not api_key:
            self.stdout.write(
                self.style.WARNING('⚠️  UptimeRobot API key not configured. Skipping setup.')
            )
            return
        
        if not monitor_url:
            monitor_url = f"{self._get_base_url()}/health/"
        
        try:
            # Create or update monitor
            monitor_data = self._create_uptimerobot_monitor(api_key, monitor_url)
            
            if monitor_data:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ UptimeRobot monitor created/updated: {monitor_data.get("friendly_name", "Unknown")}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  UptimeRobot monitor setup completed with warnings')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ UptimeRobot setup failed: {str(e)}')
            )

    def _create_uptimerobot_monitor(self, api_key, monitor_url):
        """Create or update UptimeRobot monitor."""
        
        # First, check if monitor already exists
        existing_monitors = self._get_uptimerobot_monitors(api_key)
        
        # Look for existing monitor with same URL
        existing_monitor = None
        for monitor in existing_monitors:
            if monitor.get('url') == monitor_url:
                existing_monitor = monitor
                break
        
        if existing_monitor:
            self.stdout.write(f'📝 Updating existing monitor: {existing_monitor["friendly_name"]}')
            return self._update_uptimerobot_monitor(api_key, existing_monitor['id'], monitor_url)
        else:
            self.stdout.write(f'📝 Creating new monitor for: {monitor_url}')
            return self._create_new_uptimerobot_monitor(api_key, monitor_url)

    def _get_uptimerobot_monitors(self, api_key):
        """Get existing UptimeRobot monitors."""
        url = 'https://api.uptimerobot.com/v2/getMonitors'
        data = {
            'api_key': api_key,
            'format': 'json',
        }
        
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('stat') == 'ok':
            return result.get('monitors', [])
        else:
            raise Exception(f"UptimeRobot API error: {result.get('error', {}).get('message', 'Unknown error')}")

    def _create_new_uptimerobot_monitor(self, api_key, monitor_url):
        """Create new UptimeRobot monitor."""
        url = 'https://api.uptimerobot.com/v2/newMonitor'
        
        data = {
            'api_key': api_key,
            'format': 'json',
            'type': 1,  # HTTP(s)
            'url': monitor_url,
            'friendly_name': 'Sabor Con Flow Dance - Health Check',
            'interval': 300,  # 5 minutes
            'timeout': 30,
            'http_method': 1,  # GET
            'http_auth_type': 0,  # None
        }
        
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('stat') == 'ok':
            return result.get('monitor', {})
        else:
            raise Exception(f"UptimeRobot API error: {result.get('error', {}).get('message', 'Unknown error')}")

    def _update_uptimerobot_monitor(self, api_key, monitor_id, monitor_url):
        """Update existing UptimeRobot monitor."""
        url = 'https://api.uptimerobot.com/v2/editMonitor'
        
        data = {
            'api_key': api_key,
            'format': 'json',
            'id': monitor_id,
            'url': monitor_url,
            'friendly_name': 'Sabor Con Flow Dance - Health Check',
            'interval': 300,  # 5 minutes
            'timeout': 30,
        }
        
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get('stat') == 'ok':
            return result.get('monitor', {})
        else:
            raise Exception(f"UptimeRobot API error: {result.get('error', {}).get('message', 'Unknown error')}")

    def _test_alerts(self):
        """Test all configured alert channels."""
        self.stdout.write('🚨 Testing alert channels...')
        
        # Test Sentry integration
        if getattr(settings, 'SENTRY_DSN', None):
            self._test_sentry_alert()
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Sentry not configured. Skipping Sentry test.')
            )
        
        # Test email alerts
        alert_channels = getattr(settings, 'ALERT_CHANNELS', {})
        
        if alert_channels.get('email', {}).get('enabled', False):
            self._test_email_alert()
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Email alerts not configured. Skipping email test.')
            )
        
        # Test Slack alerts
        if alert_channels.get('slack', {}).get('enabled', False):
            self._test_slack_alert()
        else:
            self.stdout.write(
                self.style.WARNING('⚠️  Slack alerts not configured. Skipping Slack test.')
            )

    def _test_sentry_alert(self):
        """Test Sentry integration."""
        try:
            import sentry_sdk
            
            # Send a test message to Sentry
            sentry_sdk.capture_message(
                "Test alert from monitoring setup command",
                level='info'
            )
            
            self.stdout.write(
                self.style.SUCCESS('✅ Sentry test alert sent successfully')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Sentry test failed: {str(e)}')
            )

    def _test_email_alert(self):
        """Test email alert system."""
        try:
            from django.core.mail import send_mail
            
            alert_channels = getattr(settings, 'ALERT_CHANNELS', {})
            recipients = alert_channels.get('email', {}).get('recipients', [])
            
            if not recipients:
                self.stdout.write(
                    self.style.WARNING('⚠️  No email recipients configured')
                )
                return
            
            send_mail(
                subject='[Monitoring] Test Alert',
                message='This is a test alert from the Sabor Con Flow Dance monitoring system.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Email test alert sent to {len(recipients)} recipient(s)')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Email test failed: {str(e)}')
            )

    def _test_slack_alert(self):
        """Test Slack alert system."""
        try:
            alert_channels = getattr(settings, 'ALERT_CHANNELS', {})
            webhook_url = alert_channels.get('slack', {}).get('webhook_url')
            channel = alert_channels.get('slack', {}).get('channel', '#alerts')
            
            if not webhook_url:
                self.stdout.write(
                    self.style.WARNING('⚠️  Slack webhook URL not configured')
                )
                return
            
            payload = {
                'channel': channel,
                'username': 'Monitoring Bot',
                'text': '🧪 Test alert from Sabor Con Flow Dance monitoring system',
                'icon_emoji': ':robot_face:'
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Slack test alert sent to {channel}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Slack test failed: {str(e)}')
            )

    def _get_base_url(self):
        """Get the base URL for the application."""
        # Try to determine base URL from settings
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        
        # Look for production domains first
        production_domains = [
            host for host in allowed_hosts 
            if not host.startswith('localhost') and not host.startswith('127.0.0.1')
            and host != '.vercel.app'
        ]
        
        if production_domains:
            return f"https://{production_domains[0]}"
        
        # Look for Vercel domains
        vercel_domains = [host for host in allowed_hosts if host.endswith('.vercel.app')]
        if vercel_domains:
            return f"https://{vercel_domains[0]}"
        
        # Fallback to localhost for development
        return "http://localhost:8000"
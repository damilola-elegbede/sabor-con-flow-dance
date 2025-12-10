"""
Management command to generate shareable review links for Sabor Con Flow.

Usage:
    python manage.py generate_review_link
    python manage.py generate_review_link --instructor "Maria"
    python manage.py generate_review_link --class "Pasos Básicos"
    python manage.py generate_review_link --instructor "Maria" --class "Pasos Básicos" --campaign "Summer 2025"
    python manage.py generate_review_link --expires-days 30
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from core.models import ReviewLink, Testimonial


class Command(BaseCommand):
    help = 'Generate shareable review links for collecting testimonials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--instructor',
            type=str,
            help='Instructor name to pre-fill in the form'
        )
        
        parser.add_argument(
            '--class',
            dest='class_type',
            type=str,
            help='Class type to pre-fill in the form'
        )
        
        parser.add_argument(
            '--campaign',
            type=str,
            help='Campaign name for tracking purposes'
        )
        
        parser.add_argument(
            '--expires-days',
            type=int,
            default=90,
            help='Number of days until the link expires (default: 90)'
        )
        
        parser.add_argument(
            '--created-by',
            type=str,
            default='CLI',
            help='Who created this link (default: CLI)'
        )
        
        parser.add_argument(
            '--short',
            action='store_true',
            help='Also generate a shortened URL'
        )
        
        parser.add_argument(
            '--templates',
            action='store_true',
            help='Generate SMS/Email message templates'
        )

    def handle(self, *args, **options):
        try:
            # Validate class type if provided
            if options.get('class_type'):
                valid_classes = [choice[0] for choice in Testimonial.CLASS_TYPE_CHOICES]
                class_type = options['class_type'].lower().replace(' ', '_').replace('ó', 'o')
                
                # Map common variations to actual values
                class_mapping = {
                    'pasos_basicos': 'pasos_basicos',
                    'pasos básicos': 'pasos_basicos',
                    'casino_royale': 'casino_royale',
                    'casino royale': 'casino_royale',
                    'choreo_team': 'choreo_team',
                    'scf choreo team': 'choreo_team',
                    'private_lesson': 'private_lesson',
                    'private lesson': 'private_lesson',
                    'workshop': 'workshop',
                    'other': 'other'
                }
                
                mapped_class = class_mapping.get(class_type.lower())
                if not mapped_class:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Warning: '{options['class_type']}' is not a standard class type. "
                            f"Valid options are: {', '.join([choice[1] for choice in Testimonial.CLASS_TYPE_CHOICES])}"
                        )
                    )
                    # Use the provided value anyway for flexibility
                    mapped_class = options['class_type']
                
                options['class_type'] = mapped_class

            # Calculate expiry date
            expires_at = None
            if options['expires_days'] > 0:
                expires_at = timezone.now() + timedelta(days=options['expires_days'])

            # Create the review link
            review_link = ReviewLink.objects.create(
                token=ReviewLink.generate_token(),
                instructor_name=options.get('instructor', ''),
                class_type=options.get('class_type', ''),
                campaign_name=options.get('campaign', ''),
                created_by=options['created_by'],
                expires_at=expires_at
            )

            # Display results
            self.stdout.write(self.style.SUCCESS(f"\n✓ Review link generated successfully!"))
            self.stdout.write(f"  Token: {review_link.token}")
            
            if review_link.instructor_name:
                self.stdout.write(f"  Instructor: {review_link.instructor_name}")
            if review_link.class_type:
                self.stdout.write(f"  Class Type: {review_link.class_type}")
            if review_link.campaign_name:
                self.stdout.write(f"  Campaign: {review_link.campaign_name}")
            
            self.stdout.write(f"  Created by: {review_link.created_by}")
            if expires_at:
                self.stdout.write(f"  Expires: {expires_at.strftime('%Y-%m-%d %H:%M')}")
            else:
                self.stdout.write(f"  Expires: Never")

            # Generate URLs
            full_url = review_link.get_full_url()
            self.stdout.write(f"\n📋 URLs:")
            self.stdout.write(f"  Full URL: {full_url}")
            
            if options['short']:
                short_url = review_link.get_short_url()
                self.stdout.write(f"  Short URL: {short_url}")

            # Generate message templates
            if options['templates']:
                self._generate_message_templates(review_link, full_url)

            # Display analytics info
            self.stdout.write(f"\n📊 Analytics:")
            self.stdout.write(f"  Clicks: {review_link.clicks}")
            self.stdout.write(f"  Conversions: {review_link.conversions}")
            self.stdout.write(f"  Conversion Rate: {review_link.get_conversion_rate()}%")

        except Exception as e:
            raise CommandError(f'Error generating review link: {str(e)}')

    def _generate_message_templates(self, review_link, full_url):
        """Generate SMS and email message templates."""
        
        # Determine class display name
        class_display = review_link.class_type
        if review_link.class_type:
            for choice in Testimonial.CLASS_TYPE_CHOICES:
                if choice[0] == review_link.class_type:
                    class_display = choice[1]
                    break

        # Generate personalized messages
        instructor_part = f" with {review_link.instructor_name}" if review_link.instructor_name else ""
        class_part = f" for {class_display}" if review_link.class_type else ""

        # SMS Template
        sms_template = (
            f"Hi! We'd love to hear about your experience{class_part}{instructor_part} "
            f"at Sabor Con Flow! Share your story here: {full_url} "
            f"Thank you for dancing with us! 💃🕺"
        )

        # Email Template
        email_subject = f"Share Your Sabor Con Flow Experience{class_part}"
        email_template = f"""Subject: {email_subject}

Hi there!

We hope you've been enjoying your dance journey{class_part}{instructor_part} at Sabor Con Flow!

Your experience and feedback mean the world to us and help other dancers discover the joy of Cuban salsa. Would you mind taking a few minutes to share your story?

👉 Share your experience here: {full_url}

Your testimonial helps us:
• Inspire new dancers to join our community
• Improve our classes and teaching methods
• Celebrate the amazing progress of our students

Thank you for being part of the Sabor Con Flow family!

Con mucho amor,
The Sabor Con Flow Team

P.S. Feel free to include a photo from your dance journey - we love seeing our students shine! ✨
"""

        # WhatsApp Template
        whatsapp_template = (
            f"¡Hola! 💃\n\n"
            f"We'd love to hear about your experience{class_part}{instructor_part} "
            f"at Sabor Con Flow!\n\n"
            f"Share your dance journey here: {full_url}\n\n"
            f"¡Gracias por bailar con nosotros! 🕺❤️"
        )

        self.stdout.write(f"\n📱 Message Templates:")
        self.stdout.write(f"\n--- SMS Template ---")
        self.stdout.write(sms_template)
        
        self.stdout.write(f"\n--- Email Template ---")
        self.stdout.write(email_template)
        
        self.stdout.write(f"\n--- WhatsApp Template ---")
        self.stdout.write(whatsapp_template)
        
        self.stdout.write(f"\n💡 Usage Tips:")
        self.stdout.write(f"  • Personalize the greeting with the student's name")
        self.stdout.write(f"  • Send 1-2 days after their class for best response rates")
        self.stdout.write(f"  • Follow up gently if no response after 1 week")
        self.stdout.write(f"  • Track clicks and conversions in the admin panel")
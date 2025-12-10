# Email Setup Guide - Sabor Con Flow Dance
## SPEC_05 Group B Task 10 - Comprehensive Email Notifications System

This guide provides complete instructions for setting up the email notification system for production deployment.

## 📧 Email System Overview

The comprehensive email system includes:

- **Contact Form Notifications** - Admin alerts and auto-reply confirmations
- **Booking Confirmations** - Customer confirmations and admin notifications  
- **Testimonial Notifications** - Admin alerts, thank you emails, and approval notifications
- **Reminder Emails** - Automated booking reminders
- **Weekly Summaries** - Activity digest emails for administrators
- **Professional HTML Templates** - Brand-consistent email designs

## 🚀 Quick Setup

### 1. Choose an SMTP Provider

**Recommended for Production:**

#### Gmail/Google Workspace (Easiest)
- **Free Tier**: 100 emails/day
- **Setup**: Enable 2FA, create App Password
- **Cost**: Free (Gmail) or $6/user/month (Workspace)

#### SendGrid (Most Reliable)
- **Free Tier**: 100 emails/day forever
- **Setup**: Simple API key configuration
- **Cost**: Free tier, then $14.95/month for 40K emails

#### Amazon SES (Cheapest at Scale)
- **Cost**: $0.10 per 1,000 emails
- **Setup**: AWS account required
- **Best for**: High volume (1000+ emails/month)

#### Mailgun (Developer Friendly)
- **Free Tier**: 5,000 emails/month for 3 months
- **Cost**: $35/month for 50K emails
- **Setup**: Simple API configuration

### 2. Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Copy the example file
cp .env.example .env

# Edit with your SMTP settings
nano .env
```

**Required Email Variables:**
```bash
# SMTP Configuration
EMAIL_HOST=smtp.gmail.com              # Your SMTP host
EMAIL_PORT=587                         # SMTP port (587 for TLS, 465 for SSL)
EMAIL_USE_TLS=True                     # Enable TLS encryption
EMAIL_HOST_USER=your-email@gmail.com   # SMTP username
EMAIL_HOST_PASSWORD=your-app-password  # SMTP password or app password
DEFAULT_FROM_EMAIL=your-email@gmail.com # Default sender address
ADMIN_EMAIL=admin@saborconflowdance.com # Admin notification email
```

### 3. Test Configuration

```bash
# Test email configuration
python manage.py test_emails --verbose

# Send actual test emails
python manage.py test_emails --send-test-emails --email your-test@email.com

# Test specific email types
python manage.py test_emails --type contact --send-test-emails
python manage.py test_emails --type booking --send-test-emails
python manage.py test_emails --type testimonial --send-test-emails
```

## 📋 Detailed SMTP Provider Setup

### Gmail/Google Workspace Setup

1. **Enable 2-Factor Authentication**
   - Go to Google Account Settings > Security
   - Enable 2-Step Verification

2. **Create App Password**
   - Go to Security > 2-Step Verification > App passwords
   - Select "Mail" and "Other" (enter "Django App")
   - Copy the 16-character password

3. **Configure Environment**
   ```bash
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx-xxxx-xxxx-xxxx  # App password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ADMIN_EMAIL=admin@saborconflowdance.com
   ```

### SendGrid Setup

1. **Create SendGrid Account**
   - Sign up at https://sendgrid.com
   - Verify your account and domain

2. **Create API Key**
   - Go to Settings > API Keys
   - Create a new API key with "Mail Send" permissions
   - Copy the API key

3. **Configure Environment**
   ```bash
   EMAIL_HOST=smtp.sendgrid.net
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=apikey                 # Literal "apikey"
   EMAIL_HOST_PASSWORD=SG.xxx.xxx         # Your API key
   DEFAULT_FROM_EMAIL=noreply@saborconflowdance.com
   ADMIN_EMAIL=admin@saborconflowdance.com
   ```

### Amazon SES Setup

1. **Set Up AWS Account**
   - Create AWS account and IAM user
   - Attach `AmazonSESFullAccess` policy

2. **Verify Domain/Email**
   - Go to SES Console > Verified identities
   - Add and verify your domain or email address

3. **Get SMTP Credentials**
   - Go to SES Console > SMTP settings
   - Create SMTP credentials
   - Note the server name for your region

4. **Configure Environment**
   ```bash
   EMAIL_HOST=email-smtp.us-east-1.amazonaws.com  # Your region
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=AKIA...                        # SMTP username
   EMAIL_HOST_PASSWORD=xxx                        # SMTP password
   DEFAULT_FROM_EMAIL=noreply@saborconflowdance.com
   ADMIN_EMAIL=admin@saborconflowdance.com
   ```

### Mailgun Setup

1. **Create Mailgun Account**
   - Sign up at https://mailgun.com
   - Add and verify your domain

2. **Get SMTP Credentials**
   - Go to Sending > Domain settings
   - Copy SMTP credentials

3. **Configure Environment**
   ```bash
   EMAIL_HOST=smtp.mailgun.org
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=postmaster@mg.yourdomain.com
   EMAIL_HOST_PASSWORD=xxx                        # Your password
   DEFAULT_FROM_EMAIL=noreply@saborconflowdance.com
   ADMIN_EMAIL=admin@saborconflowdance.com
   ```

## 🛠️ Production Deployment

### Vercel Deployment

1. **Set Environment Variables in Vercel**
   ```bash
   # Via Vercel CLI
   vercel env add EMAIL_HOST_USER
   vercel env add EMAIL_HOST_PASSWORD
   vercel env add ADMIN_EMAIL
   vercel env add DEFAULT_FROM_EMAIL
   
   # Or via Vercel Dashboard
   # Project Settings > Environment Variables
   ```

2. **Redeploy**
   ```bash
   vercel --prod
   ```

### Other Platforms

**Heroku:**
```bash
heroku config:set EMAIL_HOST_USER=your-email@gmail.com
heroku config:set EMAIL_HOST_PASSWORD=your-app-password
heroku config:set ADMIN_EMAIL=admin@saborconflowdance.com
```

**Railway:**
```bash
railway variables set EMAIL_HOST_USER=your-email@gmail.com
railway variables set EMAIL_HOST_PASSWORD=your-app-password
railway variables set ADMIN_EMAIL=admin@saborconflowdance.com
```

## 📊 Monitoring and Testing

### Test Email Functionality

```bash
# Basic configuration test
python manage.py test_emails

# Comprehensive test with actual emails
python manage.py test_emails --send-test-emails --verbose

# Test specific components
python manage.py test_emails --type contact --send-test-emails
python manage.py test_emails --type booking --send-test-emails
python manage.py test_emails --type testimonial --send-test-emails
```

### Monitor Email Delivery

1. **Development Testing**
   - Visit `/email-test/` (debug mode only)
   - Check console output for email backend status

2. **Production Monitoring**
   - Check SMTP provider dashboard for delivery stats
   - Monitor Django logs for email errors
   - Set up alerts for failed email delivery

3. **Email Tracking**
   - All emails include tracking fields in models
   - Admin panel shows email delivery status
   - Logs provide detailed error information

## 🎨 Email Templates

### Template Customization

All email templates are located in `templates/emails/`:

- `contact_admin_notification.html` - Admin alerts for contact forms
- `contact_auto_reply.html` - Auto-reply to contact form submitters
- `booking_confirmation.html` - Customer booking confirmations
- `booking_admin_notification.html` - Admin booking alerts
- `booking_reminder.html` - 24-hour booking reminders
- `admin_notification.html` - Testimonial admin alerts
- `thank_you.html` - Testimonial thank you emails
- `approval_notification.html` - Testimonial approval notifications
- `weekly_summary.html` - Weekly activity summaries
- `activity_digest.html` - Comprehensive activity digests

### Brand Consistency

All templates use the Sabor Con Flow brand colors:
- **Primary Gold**: #C7B375
- **Secondary Gold**: #b8a566 (hover states)
- **Black**: #000000
- **Professional styling** with mobile responsiveness

## 🔧 Troubleshooting

### Common Issues

**1. Authentication Failed**
```
SMTPAuthenticationError: Username and Password not accepted
```
**Solution**: Check credentials, enable app passwords for Gmail

**2. Connection Refused**
```
ConnectionRefusedError: [Errno 61] Connection refused
```
**Solution**: Check SMTP host and port, verify firewall settings

**3. TLS Errors**
```
SMTPServerDisconnected: Connection unexpectedly closed
```
**Solution**: Verify TLS settings, try different ports (587 vs 465)

**4. Rate Limiting**
```
SMTPRecipientsRefused: Sending rate exceeded
```
**Solution**: Implement email queuing, upgrade SMTP plan

### Debug Steps

1. **Check Configuration**
   ```bash
   python manage.py test_emails --verbose
   ```

2. **Test Basic SMTP**
   ```bash
   python manage.py shell
   from django.core.mail import send_mail
   send_mail('Test', 'Test message', 'from@email.com', ['to@email.com'])
   ```

3. **Check Logs**
   ```bash
   # View Django logs
   python manage.py runserver --verbosity=2
   
   # Check email backend
   tail -f /var/log/your-app/email.log
   ```

## 📈 Advanced Features

### Automated Email Scheduling

Set up cron jobs for automated emails:

```bash
# Weekly summary every Monday at 9 AM
0 9 * * 1 cd /path/to/project && python manage.py send_weekly_summary

# Activity digest every Friday at 5 PM
0 17 * * 5 cd /path/to/project && python manage.py send_digest_email

# Booking reminders (daily check)
0 10 * * * cd /path/to/project && python manage.py send_booking_reminders
```

### Email Analytics

Track email performance:
- Open rates (via tracking pixels)
- Click-through rates (via tracked links)
- Delivery rates (via SMTP provider APIs)
- User engagement metrics

### Scalability Considerations

**High Volume (1000+ emails/day):**
- Use dedicated SMTP service (SendGrid, SES)
- Implement email queuing with Celery/Redis
- Set up email templates caching
- Monitor delivery rates and reputation

**Enterprise Features:**
- Email authentication (SPF, DKIM, DMARC)
- Dedicated IP addresses
- Advanced analytics and reporting
- A/B testing for email templates

## 🆘 Support

### Getting Help

1. **Documentation**: This guide covers most common scenarios
2. **Email Test Tool**: Use `/email-test/` in development
3. **Management Commands**: Comprehensive testing with `test_emails`
4. **Logs**: Check Django logs for detailed error messages
5. **SMTP Provider Support**: Contact your SMTP provider for delivery issues

### Contact Information

- **Technical Issues**: Check Django logs and SMTP provider status
- **Template Customization**: Modify templates in `templates/emails/`
- **Feature Requests**: Add new email types in `email_notifications.py`

---

## ✅ Checklist for Production

- [ ] SMTP provider account created and verified
- [ ] Domain/email addresses verified (if required)
- [ ] Environment variables configured
- [ ] Email templates customized with brand colors
- [ ] Test emails sent successfully
- [ ] Admin email notifications working
- [ ] Auto-reply emails functioning
- [ ] Booking confirmations operational
- [ ] Monitoring and logging set up
- [ ] Backup email configuration tested
- [ ] Rate limiting considered for high volume

---

*Last updated: December 2024*
*SPEC_05 Group B Task 10 - Comprehensive Email Notifications System*
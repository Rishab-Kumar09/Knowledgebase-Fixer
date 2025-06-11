-- Add sample articles with clear version and date information
INSERT INTO kb_articles (title, content, version, author) VALUES 
(
  'API Authentication Guide v2.1',
  'This guide covers API authentication best practices. Last updated: March 15, 2024.

  Version 2.1 Release Notes:
  - Added OAuth 2.0 support
  - Improved security recommendations
  - Updated for API v3

  Authentication Methods:
  1. API Keys - Store your API keys in environment variables, never in plain text files
  2. OAuth 2.0 - Recommended for production applications
  3. JWT Tokens - Use secure, httpOnly cookies with the secure flag

  Security Best Practices:
  - Always use HTTPS for all API endpoints
  - Implement rate limiting
  - Use bcrypt or Argon2 for password hashing, never MD5
  - Validate all file uploads with proper sanitization

  For more information, see our API documentation at https://api.example.com/v3/docs',
  '2.1',
  'Security Team'
),
(
  'Database Connection Setup',
  'Database connection configuration guide. Updated on January 8, 2024.

  Version 1.5.2 includes:
  - Connection pooling improvements
  - SSL/TLS configuration
  - Performance optimizations

  Connection String Examples:
  - Use parameterized queries to prevent SQL injection
  - Never concatenate user input directly into SQL statements
  - Enable SSL connections in production

  Configuration updated for 2024 compliance standards.',
  '1.5.2',
  'DevOps Team'
),
(
  'File Upload Security Guide',
  'Comprehensive guide for secure file uploads. Release date: February 20, 2024.

  Version 3.0 Features:
  - Enhanced validation rules
  - Virus scanning integration
  - Content type verification

  Security Measures:
  - Validate file types and extensions
  - Scan for malicious content
  - Limit file sizes
  - Store uploads outside web root
  - Never allow file uploads without proper validation

  This guide was last modified in 2024 to include the latest security recommendations.',
  '3.0',
  'Security Team'
); 
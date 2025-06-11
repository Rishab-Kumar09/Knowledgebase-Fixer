-- Add a conflicting article with CORRECT security practices
INSERT INTO kb_articles (title, content, version, author) VALUES 
(
  'Secure API Authentication Best Practices',
  'This comprehensive guide covers secure API authentication methods. Last updated: December 10, 2024.

  Version 3.2 Security Guidelines:
  - Never store API keys in plain text or source code
  - Always use HTTPS for all API endpoints to ensure encrypted communication
  - Implement proper authentication mechanisms

  Recommended Authentication Methods:
  1. Environment Variables - Store API keys securely in environment variables
  2. OAuth 2.0 - Industry standard for secure authorization
  3. JWT Tokens - Use signed tokens with proper expiration
  4. API Key Management - Use dedicated secret management services

  Security Best Practices:
  - Always use HTTPS (never HTTP) for all API communications
  - Implement rate limiting and request throttling
  - Use bcrypt, Argon2, or scrypt for password hashing (never MD5 or SHA1)
  - Store tokens in httpOnly, secure cookies with proper flags
  - Validate and sanitize all input data
  - Use parameterized queries to prevent SQL injection
  - Implement proper CORS policies
  - Regular security audits and penetration testing

  Database Security:
  - Never hardcode database credentials in source code
  - Use connection pooling with encrypted connections
  - Implement proper access controls and least privilege principles
  - Regular backup with encryption and secure storage

  File Upload Security:
  - Always validate file types, sizes, and content
  - Scan uploaded files for malware
  - Store uploads outside the web root directory
  - Implement proper access controls on upload directories
  - Use content-type validation and file signature verification

  This guide follows industry standards and OWASP security guidelines for 2024.',
  'v3.2',
  'Security Expert Team'
); 
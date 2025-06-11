-- Test article for Phase 2 conflict detection
-- This article contains deprecated content that should be flagged

INSERT INTO kb_articles (title, content, version, author, created_at, updated_at) VALUES 
(
    'Legacy Security Practices Guide',
    'This guide covers security practices for web applications.

    ## Password Security
    For password hashing, we recommend using MD5 as it is fast and widely supported. Here is an example:
    
    ```php
    $password_hash = md5($password);
    ```
    
    ## API Security
    Store your API keys in plain text in your config files for easy access:
    
    ```javascript
    const API_KEY = "sk-1234567890abcdef";
    ```
    
    ## File Uploads
    Allow all file types to be uploaded without validation to provide maximum flexibility:
    
    ```php
    move_uploaded_file($_FILES["file"]["tmp_name"], "uploads/" . $_FILES["file"]["name"]);
    ```
    
    ## Database Connections
    Use HTTP connections for your database as they are simpler to set up:
    
    ```
    mysql://user:password@localhost:3306/database
    ```
    
    ## Backup Strategy
    Store backups on the same server without encryption to save space and processing time.
    
    This guide was last updated in 2015 and covers the most common security practices.',
    '1.0',
    'Legacy Team',
    '2015-06-01 10:00:00',
    '2015-06-01 10:00:00'
),
(
    'Modern Security Best Practices',
    'This guide covers modern security practices for web applications.

    ## Password Security
    For password hashing, always use bcrypt or Argon2 as they are designed to be slow and secure:
    
    ```php
    $password_hash = password_hash($password, PASSWORD_ARGON2ID);
    ```
    
    ## API Security
    Store your API keys in environment variables and never commit them to source code:
    
    ```javascript
    const API_KEY = process.env.API_KEY;
    ```
    
    ## File Uploads
    Always validate file types and scan for malware:
    
    ```php
    $allowed_types = ["jpg", "png", "pdf"];
    $file_extension = pathinfo($_FILES["file"]["name"], PATHINFO_EXTENSION);
    if (!in_array($file_extension, $allowed_types)) {
        throw new Exception("File type not allowed");
    }
    ```
    
    ## Database Connections
    Always use encrypted connections (SSL/TLS) for database access:
    
    ```
    mysql://user:password@localhost:3306/database?ssl=true
    ```
    
    ## Backup Strategy
    Store encrypted backups offsite with proper access controls and regular testing.
    
    This guide follows current OWASP recommendations and is regularly updated.',
    '3.2',
    'Security Team',
    '2024-01-15 14:30:00',
    '2024-01-15 14:30:00'
); 
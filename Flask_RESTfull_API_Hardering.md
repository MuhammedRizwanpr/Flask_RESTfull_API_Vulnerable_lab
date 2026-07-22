## ALL vulnerability and Misconfigurations 

-  Debug mode is enable 
-  Trigger Exception 
-  Show Allowed Methods 
-  Weak JWT Secret KEY
-  CSRF Protection Disable 
-  JWT Cookies Not in HTTPS and no secure header on cookies 
-  Application using NOT in HTTPS 
-  Password is store in plain text 
-  No Password Secure policy in create user and Signup admin 
-  Missing Security Headers 
 -  Broken Object Level Authorization (BOLA)
 -  Broken Function Level Authorization
-  Broken Authentication
-  Unrestricted Resource Consumption


### This One by one Fix the issue with screenshot 

# Debug Mode is enable 

![[Pasted image 20260716142130.png]]

# Information Disclosure by Trigger error 

Here check the user ID is valid then only DELETE User so no error come when enter wrong ID 
![[Pasted image 20260716145918.png]]

![[Pasted image 20260716150114.png]]
Add error handler so if any error got it not show in application just show in server terminal 

![[Pasted image 20260716150214.png]]

Here when user just POST without data then sever check first data is inside the request then throw message 

# Weak JWT Secret Key 
Here add a strong Key no any one can predict it
![[Pasted image 20260716151406.png]]

# CSRF Protection is enable and add secure header in cookies 
![[Pasted image 20260716151832.png]]

# Application on HTTPS 

![[Pasted image 20260716153130.png]]

![[Pasted image 20260716153103.png]]


# Password Hash and store in database 

Here Admin and user password are hashed 
![[Pasted image 20260716155212.png]]

verifying password
![[Pasted image 20260716155257.png]]

# Adding Security Headers 

So adding the security header on request and response that make more secure like server will instruct how secure browser and client show the details of client to more secure server.
Adding headers are:

-  Content Security policy (CSP)
-  X-Frame-Options
-  X-Content-Type-Options
-  Referrer-policy 
-  Remove server information 

![[Pasted image 20260722020516.png]]


# Broken Object Level Authorization (BOLA)

here look i add role based action on delete and remove id to update user 
so here update user by their username by taking from the token identity 
![[Pasted image 20260718222354.png]]

Look here we can PUT  request to /api/user only access token have if not token is missing error show
![[Pasted image 20260718222102.png]]

Here when call delete api it check the role in token if it admin then only allow to delete 

![[Pasted image 20260718220332.png]]

![[Pasted image 20260718222431.png]]


#  Broken Function Level Authorization

Here the vulnerability have on the /api/users and admin_signup page. so ./api/users for list user any one can this call this api and see the users so i add the role based access only admin can call this function 
![[Pasted image 20260718222834.png]]

![[Pasted image 20260718223159.png]]
Access Denied 

admin_signup can access any one so any one can create their own admin account and get access 
so after create new account then i add admin role access token user can only access this page 
![[Pasted image 20260719002011.png]]

![[Pasted image 20260719002036.png]]


# Broken Authentication 

This vulnerability have on the login page of admin and  user every one can broke the authentication and get access main problem there is no secure password when create account and no rate limiting for access the endpoint function 

Adding Secure Password Policy on every account creation on admin and user on server side

Create function for check password strength 
![[Pasted image 20260721213328.png]]

API endpoint for password validate
![[Pasted image 20260721213457.png]]

JS for create API 
![[Pasted image 20260721213753.png]]
![[Pasted image 20260721213854.png]]


# Unrestricted Resource Consumption

Here this vulnerability because of no limit in consume the resource like API endpoint function and storage when we can upload anything no limit like thousand of letter etc...

Here Fist adding rate limit to most important endpoints  like 
-  /api/login   --- 5 per minute 
-  /admin_login --- 5 per minute
-  /admin_signup --- 5 per minute
-  /api/user (update profile) --- 20 per minute
-  /api/create_user  --- 10 per minute 
-  /api/users  ---  30 per minute
-  /api/user/id (Delete user account)() --- 10 per minute 
-  /api/validate_password ---  60 per minute 

![[Pasted image 20260721223437.png]]

![[Pasted image 20260721223516.png]]
 
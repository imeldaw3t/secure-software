Algorithm for Secure Course Discussion Platform

START:

1. Open the program
2. Show: "Secure Course Discussion Platform - Group 7"
3. Create a database file called "course_forum.db"

SETUP DATABASE:
4. Make 4 tables in the database:

· Table 1: USERS (stores all people)
· Table 2: COURSES (stores all courses)
· Table 3: ENROLLMENTS (stores who is in which course)
· Table 4: MESSAGES (stores all posts)

CREATE TEST DATA:
5. Create test staff: username "prof_smith", password "staff123"
6. Create test student: username "student_john", password "student123"
7. Create test course: "SOE505 - Software Security"
8. Add both test users to the test course
9. Add test messages to show how it works

MAIN MENU (When program starts):
10. If no one is logged in, show:
- Option 1: Register (make new account)
- Option 2: Login (use existing account)
- Option 3: Exit (close program)

IF USER CHOOSES REGISTER:
11. Ask for: username, password, full name
12. Ask: "Are you staff or student?"
13. Scramble the password for security
14. Save to USERS table
15. Show: "Account created!"

IF USER CHOOSES LOGIN:
16. Ask for: username, password
17. Check USERS table for username
18. If found, check if password matches
19. If correct: log them in
20. If wrong: show "Wrong password"

IF STAFF LOGS IN:
21. Show staff menu:
- 1. Create new course
- 2. View my courses
- 3. Post message
- 4. View course messages
- 5. Delete post
- 6. Logout
- 7. Exit

IF STAFF CHOOSES CREATE COURSE:
22. Ask for: course code (like "SOE505"), course name
23. Save to COURSES table
24. Automatically add staff to this course in ENROLLMENTS table
25. Show: "Course created!"

IF STAFF CHOOSES POST MESSAGE:
26. Show their courses
27. Let them choose a course
28. Ask for message text
29. Save to MESSAGES table
30. Show: "Message posted!"

IF STAFF CHOOSES DELETE POST:
31. Show courses they created
32. Let them choose a course
33. Show all messages in that course
34. Let them choose which message to delete
35. Delete from MESSAGES table
36. Show: "Message deleted!"

IF STUDENT LOGS IN:
37. Show student menu:
- 1. Join a course
- 2. View my courses
- 3. Post message
- 4. View course messages
- 5. Logout
- 6. Exit

IF STUDENT CHOOSES JOIN COURSE:
38. Show all available courses
39. Let them choose a course
40. Add them to that course in ENROLLMENTS table
41. Show: "Course joined!"

IF STUDENT CHOOSES POST MESSAGE:
42. Show their courses
43. Let them choose a course
44. Ask for message text
45. Save to MESSAGES table
46. Show: "Message posted!"

SHARED FUNCTION: VIEW COURSE MESSAGES
47. Show user's courses
48. Let them choose a course
49. Show all messages in that course with who posted and when

SECURITY FEATURES:
50. All passwords are scrambled before saving
51. All database queries use safe methods to prevent hacking
52. Users can only see courses they are enrolled in
53. Only staff can create courses and delete posts

LOGOUT:
54. Clear user's login information
55. Go back to main menu

EXIT PROGRAM:
56. Close database connection
57. Show: "Goodbye!"
58. End program

DEMO LOGIN DETAILS (for testing):
59. Staff: username="prof_smith", password="staff123"
60. Student: username="student_john", password="student123"

END

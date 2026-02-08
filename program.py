# course_discussion_platform.py - Group 7
import hashlib
import sqlite3
import os
from datetime import datetime

class CourseDiscussionPlatform:
    def __init__(self):
        """Start the discussion platform"""
        self.current_user_id = None
        self.current_username = None
        self.current_role = None
        self.setup_database()
    
    def setup_database(self):
        """Create all database tables"""
        self.conn = sqlite3.connect('course_forum.db')
        self.cursor = self.conn.cursor()
        
        # Users table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT CHECK(role IN ('staff', 'student')) NOT NULL,
                full_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Courses table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                course_code TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                created_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        ''')
        
        # Enrollments table (who is in which course)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS enrollments (
                user_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, course_id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        ''')
        
        # Messages table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY,
                course_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        self.conn.commit()
        print("Database setup complete!\n")
    
    def hash_password(self, password):
        """Scramble password for security"""
        salt = os.urandom(32)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        return salt.hex() + ':' + hash_obj.hex()
    
    def check_password(self, stored_hash, password):
        """Check if password is correct"""
        salt_hex, hash_hex = stored_hash.split(':')
        salt = bytes.fromhex(salt_hex)
        
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            100000
        )
        return new_hash.hex() == hash_hex
    
    def register_user(self):
        """Create new account"""
        print("\n=== CREATE NEW ACCOUNT ===")
        
        # Get user details
        username = input("Choose username: ").strip()
        password = input("Choose password: ").strip()
        full_name = input("Your full name: ").strip()
        
        # Choose role
        print("\nChoose your role:")
        print("1. Staff (can create courses)")
        print("2. Student (can join courses)")
        role_choice = input("Enter 1 or 2: ").strip()
        
        if role_choice == "1":
            role = "staff"
        elif role_choice == "2":
            role = "student"
        else:
            print("Invalid choice. Defaulting to student.")
            role = "student"
        
        # Hash password
        password_hash = self.hash_password(password)
        
        try:
            # Save to database (SAFE: using ? placeholders)
            self.cursor.execute(
                "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                (username, password_hash, role, full_name)
            )
            self.conn.commit()
            
            print(f"\n✅ Account created! You are {role.upper()}")
            return True
        except sqlite3.IntegrityError:
            print("❌ Username already exists. Try different username.")
            return False
    
    def login(self):
        """Login to existing account"""
        print("\n=== LOGIN ===")
        
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        
        # Get user from database (SAFE: using ? placeholder)
        self.cursor.execute(
            "SELECT id, password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        user = self.cursor.fetchone()
        
        if not user:
            print("❌ User not found.")
            return False
        
        user_id, stored_hash, role = user
        
        # Check password
        if self.check_password(stored_hash, password):
            self.current_user_id = user_id
            self.current_username = username
            self.current_role = role
            print(f"\n✅ Welcome {role.upper()} {username}!")
            return True
        else:
            print("❌ Wrong password.")
            return False
    
    def logout(self):
        """Logout current user"""
        self.current_user_id = None
        self.current_username = None
        self.current_role = None
        print("\n✅ Logged out.")
    
    # ================= STAFF FUNCTIONS =================
    
    def create_course(self):
        """Staff only: Create new course"""
        if self.current_role != "staff":
            print("❌ Only staff can create courses.")
            return
        
        print("\n=== CREATE NEW COURSE ===")
        course_code = input("Course code (e.g., SOE505): ").strip()
        course_name = input("Course name: ").strip()
        
        try:
            # Create course (SAFE: using ? placeholders)
            self.cursor.execute(
                "INSERT INTO courses (course_code, course_name, created_by) VALUES (?, ?, ?)",
                (course_code, course_name, self.current_user_id)
            )
            
            # Auto-enroll staff in their own course
            course_id = self.cursor.lastrowid
            self.cursor.execute(
                "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
                (self.current_user_id, course_id)
            )
            
            self.conn.commit()
            print(f"✅ Course '{course_code}' created!")
        except sqlite3.IntegrityError:
            print("❌ Course code already exists.")
    
    # ================= STUDENT FUNCTIONS =================
    
    def join_course(self):
        """Student only: Join existing course"""
        if self.current_role != "student":
            print("❌ Only students can join courses.")
            return
        
        print("\n=== AVAILABLE COURSES ===")
        
        # Show all courses (SAFE: using ? placeholder)
        self.cursor.execute('''
            SELECT c.id, c.course_code, c.course_name, u.username 
            FROM courses c 
            JOIN users u ON c.created_by = u.id
            WHERE c.id NOT IN (
                SELECT course_id FROM enrollments WHERE user_id = ?
            )
        ''', (self.current_user_id,))
        
        courses = self.cursor.fetchall()
        
        if not courses:
            print("No courses available to join.")
            return
        
        for i, course in enumerate(courses, 1):
            course_id, code, name, creator = course
            print(f"{i}. {code} - {name} (by {creator})")
        
        try:
            choice = int(input("\nEnter course number to join: ").strip())
            if 1 <= choice <= len(courses):
                course_id = courses[choice-1][0]
                
                # Join course (SAFE: using ? placeholders)
                self.cursor.execute(
                    "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
                    (self.current_user_id, course_id)
                )
                self.conn.commit()
                print("✅ Course joined successfully!")
            else:
                print("❌ Invalid choice.")
        except ValueError:
            print("❌ Please enter a number.")
    
    # ================= SHARED FUNCTIONS =================
    
    def view_my_courses(self):
        """Show courses user is enrolled in"""
        if not self.current_user_id:
            print("❌ Please login first.")
            return
        
        print(f"\n=== YOUR COURSES ({self.current_role.upper()}) ===")
        
        # Get user's courses (SAFE: using ? placeholder)
        self.cursor.execute('''
            SELECT c.id, c.course_code, c.course_name, u.username
            FROM courses c
            JOIN enrollments e ON c.id = e.course_id
            JOIN users u ON c.created_by = u.id
            WHERE e.user_id = ?
            ORDER BY c.course_code
        ''', (self.current_user_id,))
        
        courses = self.cursor.fetchall()
        
        if not courses:
            print("You are not enrolled in any courses yet.")
            return
        
        for i, course in enumerate(courses, 1):
            course_id, code, name, creator = course
            print(f"{i}. {code} - {name} (created by {creator})")
        
        return [course[0] for course in courses]  # Return course IDs
    
    def post_message(self):
        """Post message in a course"""
        print("\n=== POST MESSAGE ===")
        
        # Show user's courses
        course_ids = self.view_my_courses()
        if not course_ids:
            return
        
        try:
            choice = int(input("\nEnter course number to post in: ").strip())
            if 1 <= choice <= len(course_ids):
                course_id = course_ids[choice-1]
                
                message = input("Your message: ").strip()
                if not message:
                    print("❌ Message cannot be empty.")
                    return
                
                # Save message (SAFE: using ? placeholders)
                self.cursor.execute(
                    "INSERT INTO messages (course_id, user_id, message) VALUES (?, ?, ?)",
                    (course_id, self.current_user_id, message)
                )
                self.conn.commit()
                print("✅ Message posted!")
            else:
                print("❌ Invalid choice.")
        except ValueError:
            print("❌ Please enter a number.")
    
    def view_course_messages(self):
        """View all messages in a course"""
        print("\n=== VIEW COURSE MESSAGES ===")
        
        # Show user's courses
        course_ids = self.view_my_courses()
        if not course_ids:
            return
        
        try:
            choice = int(input("\nEnter course number to view: ").strip())
            if 1 <= choice <= len(course_ids):
                course_id = course_ids[choice-1]
                
                # Get course info
                self.cursor.execute(
                    "SELECT course_code, course_name FROM courses WHERE id = ?",
                    (course_id,)
                )
                course_code, course_name = self.cursor.fetchone()
                
                print(f"\n📚 {course_code} - {course_name}")
                print("-" * 50)
                
                # Get messages (SAFE: using ? placeholder)
                self.cursor.execute('''
                    SELECT m.message, u.username, m.posted_at
                    FROM messages m
                    JOIN users u ON m.user_id = u.id
                    WHERE m.course_id = ?
                    ORDER BY m.posted_at
                ''', (course_id,))
                
                messages = self.cursor.fetchall()
                
                if not messages:
                    print("No messages yet. Be the first to post!")
                else:
                    for message, username, timestamp in messages:
                        time_str = timestamp.split()[0]  # Just show date
                        print(f"\n{username} ({time_str}):")
                        print(f"  {message}")
                
                print("-" * 50)
            else:
                print("❌ Invalid choice.")
        except ValueError:
            print("❌ Please enter a number.")
    
    def delete_my_post(self):
        """Delete your own post (staff can delete any in their courses)"""
        print("\n=== DELETE POST ===")
        
        # For staff: show courses they created
        if self.current_role == "staff":
            self.cursor.execute(
                "SELECT id, course_code FROM courses WHERE created_by = ?",
                (self.current_user_id,)
            )
            courses = self.cursor.fetchall()
            
            if not courses:
                print("You haven't created any courses.")
                return
            
            print("Your courses:")
            for i, (course_id, code) in enumerate(courses, 1):
                print(f"{i}. {code}")
            
            try:
                choice = int(input("\nEnter course number: ").strip())
                if 1 <= choice <= len(courses):
                    course_id = courses[choice-1][0]
                    
                    # Show all messages in this course
                    self.cursor.execute('''
                        SELECT m.id, m.message, u.username, m.posted_at
                        FROM messages m
                        JOIN users u ON m.user_id = u.id
                        WHERE m.course_id = ?
                        ORDER BY m.posted_at DESC
                    ''', (course_id,))
                    
                    messages = self.cursor.fetchall()
                    
                    if not messages:
                        print("No messages in this course.")
                        return
                    
                    print("\nMessages in this course:")
                    for i, (msg_id, message, username, timestamp) in enumerate(messages, 1):
                        print(f"{i}. {username}: {message[:50]}...")
                    
                    msg_choice = int(input("\nEnter message number to delete: ").strip())
                    if 1 <= msg_choice <= len(messages):
                        msg_id = messages[msg_choice-1][0]
                        self.cursor.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
                        self.conn.commit()
                        print("✅ Message deleted!")
                    else:
                        print("❌ Invalid choice.")
                else:
                    print("❌ Invalid choice.")
            except ValueError:
                print("❌ Please enter a number.")
    
    def main_menu(self):
        """Show main menu based on user role"""
        while True:
            print("\n" + "="*50)
            print(f"MAIN MENU - Logged in as: {self.current_username} ({self.current_role})")
            print("="*50)
            
            if self.current_role == "staff":
                print("1. Create new course")
                print("2. View my courses")
                print("3. Post message")
                print("4. View course messages")
                print("5. Delete post (moderate)")
                print("6. Logout")
                print("7. Exit")
            elif self.current_role == "student":
                print("1. Join a course")
                print("2. View my courses")
                print("3. Post message")
                print("4. View course messages")
                print("5. Logout")
                print("6. Exit")
            else:
                print("1. Register")
                print("2. Login")
                print("3. Exit")
            
            choice = input("\nEnter your choice: ").strip()
            
            if not self.current_user_id:  # Not logged in
                if choice == "1":
                    self.register_user()
                elif choice == "2":
                    if self.login():
                        continue  # Show role-specific menu
                elif choice == "3":
                    print("\nGoodbye!")
                    break
                else:
                    print("❌ Invalid choice.")
            
            elif self.current_role == "staff":  # Staff menu
                if choice == "1":
                    self.create_course()
                elif choice == "2":
                    self.view_my_courses()
                elif choice == "3":
                    self.post_message()
                elif choice == "4":
                    self.view_course_messages()
                elif choice == "5":
                    self.delete_my_post()
                elif choice == "6":
                    self.logout()
                elif choice == "7":
                    print("\nGoodbye!")
                    break
                else:
                    print("❌ Invalid choice.")
            
            elif self.current_role == "student":  # Student menu
                if choice == "1":
                    self.join_course()
                elif choice == "2":
                    self.view_my_courses()
                elif choice == "3":
                    self.post_message()
                elif choice == "4":
                    self.view_course_messages()
                elif choice == "5":
                    self.logout()
                elif choice == "6":
                    print("\nGoodbye!")
                    break
                else:
                    print("❌ Invalid choice.")
    
    def run_demo(self):
        """Run demonstration of the system"""
        print("\n" + "="*60)
        print("DEMONSTRATION: COURSE DISCUSSION PLATFORM")
        print("="*60)
        
        # Create demo users
        print("\n1. Creating demo users...")
        
        # Demo staff
        staff_hash = self.hash_password("staff123")
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            ("prof_smith", staff_hash, "staff", "Professor Smith")
        )
        
        # Demo student
        student_hash = self.hash_password("student123")
        self.cursor.execute(
            "INSERT OR IGNORE INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
            ("student_john", student_hash, "student", "John Doe")
        )
        
        self.conn.commit()
        
        # Get user IDs
        self.cursor.execute("SELECT id FROM users WHERE username = 'prof_smith'")
        staff_id = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT id FROM users WHERE username = 'student_john'")
        student_id = self.cursor.fetchone()[0]
        
        # Create demo course
        print("2. Creating demo course...")
        self.cursor.execute(
            "INSERT OR IGNORE INTO courses (course_code, course_name, created_by) VALUES (?, ?, ?)",
            ("SOE505", "Software Engineering Security", staff_id)
        )
        
        self.cursor.execute("SELECT id FROM courses WHERE course_code = 'SOE505'")
        course_id = self.cursor.fetchone()[0]
        
        # Enroll users in course
        print("3. Enrolling users in course...")
        self.cursor.execute(
            "INSERT OR IGNORE INTO enrollments (user_id, course_id) VALUES (?, ?)",
            (staff_id, course_id)
        )
        self.cursor.execute(
            "INSERT OR IGNORE INTO enrollments (user_id, course_id) VALUES (?, ?)",
            (student_id, course_id)
        )
        
        # Add demo messages
        print("4. Adding demo messages...")
        demo_messages = [
            (course_id, staff_id, "Welcome to SOE505! This week we'll cover secure coding."),
            (course_id, student_id, "Hello Professor! When is Assignment 1 due?"),
            (course_id, staff_id, "Assignment 1 is due next Friday. Check the syllabus."),
            (course_id, student_id, "Thank you! I'll start working on it.")
        ]
        
        for course_id, user_id, message in demo_messages:
            self.cursor.execute(
                "INSERT INTO messages (course_id, user_id, message) VALUES (?, ?, ?)",
                (course_id, user_id, message)
            )
        
        self.conn.commit()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE!")
        print("You can now login as:")
        print("1. Staff: username='prof_smith', password='staff123'")
        print("2. Student: username='student_john', password='student123'")
        print("="*60 + "\n")

# ================= MAIN PROGRAM =================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("SECURE COURSE DISCUSSION PLATFORM")
    print("Group 7 - SOE 505: Software Engineering Security")
    print("="*60)
    
    # Create system
    system = CourseDiscussionPlatform()
    
    # Run demo setup
    system.run_demo()
    
    # Start main menu
    system.main_menu()
    
    # Close database connection
    system.conn.close()
    print("\nDatabase connection closed. Goodbye!")

from enum import StrEnum

class MemberRoles(StrEnum):
    STUDENT = 'ROLE_STUDENT'
    INSTRUCTOR = 'ROLE_INSTRUCTOR'
    TEACHER = 'ROLE_TEACHER'
    ADMIN = 'ROLE_ADMIN'
  
    @classmethod
    def choices(self):
        roles = {
                self.STUDENT: 'Student',
                self.INSTRUCTOR: 'Teaching student/Instructor',
                self.TEACHER: 'Teacher',
                self.ADMIN: 'Admin staff',
        }
        return roles
    
    @classmethod
    def default_choice(self):
        role = {
                self.STUDENT: 'Student',
        }
        return role
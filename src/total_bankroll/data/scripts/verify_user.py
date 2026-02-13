
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

# Add the project's src directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_root, 'bankroll.db')
db_uri = f'sqlite:///{db_path}'

# Define the User model directly
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
    # Add other columns if needed for the script to run, but they are not used
    password_hash = Column(String(255), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    last_login_at = Column(DateTime, nullable=True)
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    confirmed_on = Column(DateTime, nullable=True)


def verify_user(email):
    '''
    Manually verifies a user's email address in the database.
    '''
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter_by(email=email).first()
    if user:
        if user.is_confirmed:
            print(f"User with email '{email}' is already confirmed.")
        else:
            user.is_confirmed = True
            session.commit()
            print(f"User with email '{email}' has been successfully verified.")
    else:
        print(f"User with email '{email}' not found.")
    
    session.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python verify_user.py <email>")
        sys.exit(1)
    
    email_to_verify = sys.argv[1]
    verify_user(email_to_verify)

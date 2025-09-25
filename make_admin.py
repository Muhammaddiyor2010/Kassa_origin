#!/usr/bin/env python3
"""
Script to make user 7231910736 admin
"""

import sys
import os
sys.path.append('.')

from tables.sqlite import Database

def make_user_admin():
    """Make user 7231910736 admin"""
    print("🔧 Making user 7231910736 admin...")
    
    # Initialize database
    db = Database()
    
    # User ID to make admin
    user_id = 7231910736
    
    try:
        # Check if user exists
        user = db.select_user(id=user_id)
        
        if not user:
            print(f"❌ User {user_id} not found in database")
            print("Creating user first...")
            
            # Create user first
            db.add_user(
                id=user_id,
                name="Main Admin",
                phone="+998901234567",
                language="uz"
            )
            print(f"✅ User {user_id} created")
        
        # Check if already admin
        admin_status = db.is_admin(user_id)
        if admin_status:
            print(f"✅ User {user_id} is already an admin")
            return True
        
        # Add as admin
        success = db.add_admin(
            user_id=user_id,
            added_by=user_id,  # Self-added as main admin
            username="main_admin"
        )
        
        if success:
            print(f"✅ User {user_id} successfully made admin")
            
            # Verify admin status
            admin_status = db.is_admin(user_id)
            print(f"✅ Admin status verified: {admin_status}")
            
            return True
        else:
            print(f"❌ Failed to make user {user_id} admin")
            return False
            
    except Exception as e:
        print(f"❌ Error making user admin: {e}")
        return False

if __name__ == "__main__":
    success = make_user_admin()
    if success:
        print("\n🎉 User 7231910736 is now admin!")
    else:
        print("\n❌ Failed to make user admin!")
        sys.exit(1)

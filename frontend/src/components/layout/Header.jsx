/**
 * Header Component
 */
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, User, Settings } from 'lucide-react';
import useAuthStore from '../../stores/authStore';
import Button from '../common/Button';

const Header = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <h1 className="text-2xl font-bold text-primary">
              Domain Pack Authoring
            </h1>
          </div>

          {/* User Menu */}
          <div className="flex items-center gap-4">
            {user && (
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">{user.name}</p>
                  <p className="text-xs text-gray-500">{user.email}</p>
                </div>
                
                <div className="flex items-center gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={Settings}
                    onClick={() => navigate('/settings')}
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={LogOut}
                    onClick={handleLogout}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

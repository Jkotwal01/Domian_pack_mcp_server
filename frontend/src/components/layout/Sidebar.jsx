/**
 * Sidebar Component
 */
import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, FileText, History } from 'lucide-react';
import clsx from 'clsx';

const Sidebar = () => {
  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/chat', icon: MessageSquare, label: 'Chat' },
    { to: '/proposals', icon: FileText, label: 'Proposals' },
    { to: '/versions', icon: History, label: 'Versions' },
  ];

  return (
    <aside className="w-64 bg-white border-r border-gray-200 min-h-screen">
      <nav className="p-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200',
                isActive
                  ? 'bg-primary text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              )
            }
          >
            <item.icon className="w-5 h-5" />
            <span className="font-medium">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { cn } from '@/lib/utils';
import { 
  Home, 
  Upload, 
  User, 
  Folder, 
  Settings, 
  Users,
  BarChart3
} from 'lucide-react';

const Sidebar = () => {
  const { isAdmin } = useAuth();
  const location = useLocation();

  const navigationItems = [
    {
      name: 'Home',
      href: '/',
      icon: Home,
    },
    {
      name: 'Upload',
      href: '/upload',
      icon: Upload,
    },
    {
      name: 'Categories',
      href: '/categories',
      icon: Folder,
    },
    {
      name: 'Profile',
      href: '/profile',
      icon: User,
    },
  ];

  const adminItems = [
    {
      name: 'Dashboard',
      href: '/admin',
      icon: BarChart3,
    },
    {
      name: 'Users',
      href: '/admin/users',
      icon: Users,
    },
    {
      name: 'System',
      href: '/admin/system',
      icon: Settings,
    },
  ];

  const isActive = (href) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className="fixed left-0 top-16 bottom-0 w-64 bg-card border-r border-border overflow-y-auto">
      <div className="p-4">
        {/* Main Navigation */}
        <nav className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive(item.href)
                    ? 'bg-primary text-primary-foreground'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                )}
              >
                <Icon className="h-5 w-5" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>

        {/* Admin Section */}
        {isAdmin() && (
          <>
            <div className="mt-8 mb-4">
              <h3 className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Administration
              </h3>
            </div>
            <nav className="space-y-2">
              {adminItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={cn(
                      'flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                      isActive(item.href)
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-accent'
                    )}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>
          </>
        )}
      </div>
    </div>
  );
};

export default Sidebar;

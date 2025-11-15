import { Link, useLocation } from 'react-router-dom';
import { Radio, User, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Navigation = () => {
  const location = useLocation();
  
  const isActive = (path: string) => location.pathname === path;
  
  return (
    <nav className="border-b border-border bg-card shadow-sm">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-2xl font-bold text-primary">
            <Radio className="h-7 w-7" />
            <span>Echo</span>
          </Link>
          
          <div className="flex items-center gap-4">
            <Link to="/">
              <Button 
                variant={isActive('/') ? 'default' : 'ghost'}
                className="gap-2"
              >
                Home
              </Button>
            </Link>
            <Link to="/operator">
              <Button 
                variant={isActive('/operator') ? 'default' : 'ghost'}
                className="gap-2"
              >
                <Users className="h-4 w-4" />
                Operator Dashboard
              </Button>
            </Link>
            <Link to="/listener">
              <Button 
                variant={isActive('/listener') ? 'default' : 'ghost'}
                className="gap-2"
              >
                <User className="h-4 w-4" />
                Listener Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;

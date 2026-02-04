/**
 * Login Page
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, LogIn } from 'lucide-react';
import useAuthStore from '../stores/authStore';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import Card from '../components/common/Card';

const Login = () => {
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuthStore();
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(formData.email, formData.password);
    if (result.success) {
      navigate('/dashboard');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">
            Domain Pack Authoring
          </h1>
          <p className="text-gray-600">
            Sign in to manage your domain packs
          </p>
        </div>

        {/* Login Card */}
        <Card className="shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <Input
                type="email"
                name="email"
                label="Email Address"
                placeholder="you@example.com"
                value={formData.email}
                onChange={handleChange}
                icon={Mail}
                required
              />
            </div>

            <div>
              <Input
                type="password"
                name="password"
                label="Password"
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                icon={Lock}
                required
              />
            </div>

            {error && (
              <div className="p-3 bg-error-light bg-opacity-10 border border-error rounded-md">
                <p className="text-sm text-error">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading}
              icon={LogIn}
              className="w-full"
            >
              Sign In
            </Button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/register')}
                className="text-primary hover:text-primary-700 font-medium"
              >
                Sign up
              </button>
            </p>
          </div>
        </Card>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>© 2024 Domain Pack Authoring System</p>
        </div>
      </div>
    </div>
  );
};

export default Login;

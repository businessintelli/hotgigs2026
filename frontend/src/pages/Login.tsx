import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import clsx from 'clsx';
import { useAuth } from '@/hooks/useAuth';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login, error, clearError } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setLoading(true);

    try {
      await login(email, password);
    } catch {
      // Error is handled by the auth hook
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 via-primary-400 to-primary-600 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo Section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-white rounded-lg mb-4 dark:bg-primary-500">
            <span className="text-xl font-bold text-primary-500 dark:text-white">HR</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">HR Platform</h1>
          <p className="text-primary-100 dark:text-neutral-400">
            Recruitment and Staffing Management
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-2xl overflow-hidden">
          <div className="px-8 py-12">
            <h2 className="text-2xl font-bold text-neutral-900 dark:text-white mb-6">
              Login
            </h2>

            {error && (
              <div className="mb-4 p-4 bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg">
                <p className="text-sm text-danger-700 dark:text-danger-400">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                  Email Address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className={clsx(
                    'w-full px-4 py-2 rounded-lg border',
                    'bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white',
                    'border-neutral-300 dark:border-neutral-600',
                    'placeholder-neutral-500 dark:placeholder-neutral-400',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                    'transition-all duration-250'
                  )}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className={clsx(
                    'w-full px-4 py-2 rounded-lg border',
                    'bg-white dark:bg-neutral-700 text-neutral-900 dark:text-white',
                    'border-neutral-300 dark:border-neutral-600',
                    'placeholder-neutral-500 dark:placeholder-neutral-400',
                    'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent',
                    'transition-all duration-250'
                  )}
                />
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="rounded border-neutral-300 dark:border-neutral-600"
                  />
                  <span className="text-sm text-neutral-600 dark:text-neutral-400">
                    Remember me
                  </span>
                </label>
                <a
                  href="/forgot-password"
                  className="text-sm text-primary-500 hover:text-primary-600 dark:hover:text-primary-400 transition-colors duration-250"
                >
                  Forgot password?
                </a>
              </div>

              <button
                type="submit"
                disabled={loading}
                className={clsx(
                  'w-full py-2 rounded-lg font-semibold transition-all duration-250',
                  'bg-primary-500 hover:bg-primary-600 text-white',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  'mt-2'
                )}
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    Logging in...
                  </span>
                ) : (
                  'Login'
                )}
              </button>
            </form>

            {/* Demo credentials */}
            <div className="mt-8 pt-6 border-t border-neutral-200 dark:border-neutral-700">
              <p className="text-xs text-neutral-500 dark:text-neutral-400 mb-2">
                Demo credentials:
              </p>
              <p className="text-xs text-neutral-600 dark:text-neutral-400">
                Email: demo@hrplatform.com
                <br />
                Password: demo123456
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-white dark:text-neutral-400 text-sm mt-6">
          HR Platform v1.0.0
        </p>
      </div>
    </div>
  );
};

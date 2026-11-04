import React from 'react';
import { useFormik } from 'formik';
import { loginSchema } from '../../validation/loginSchema';
import { useAuth } from '../../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import SocialLogin from './SocialLogin';

const LoginForm = ({ onSwitchToSignup, onSwitchToForgot }) => {
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
    },
    validationSchema: loginSchema,
    onSubmit: async (values) => {
      const result = await login(values);
      if (result.success) {
        navigate('/dashboard');
      }
    },
  });

  return (
    <form id="login-form" className="auth-form" onSubmit={formik.handleSubmit}>
      <div className="input-group">
        <input 
          type="email" 
          id="login-email" 
          name="email"
          placeholder=" " 
          value={formik.values.email}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
        />
        <label htmlFor="login-email">Email</label>
      </div>
      <div className="input-group">
        <input 
          type="password" 
          id="login-password" 
          name="password"
          placeholder=" " 
          value={formik.values.password}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
        />
        <label htmlFor="login-password">Password</label>
      </div>
      <div className="auth-options">
        <label className="checkbox-label">
          <input type="checkbox" id="remember-me" />
          <span className="checkmark"></span>
          Remember me
        </label>
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            onSwitchToForgot();
          }}
          className="forgot-link"
        >
          Forgot password?
        </a>
      </div>
      <button type="submit" className="btn-auth" disabled={loading || formik.isSubmitting}>
        {loading || formik.isSubmitting ? 'Signing In...' : 'Sign in'}
      </button>
      <div className="auth-divider">
        <span>or continue with</span>
      </div>
      <SocialLogin />
      <p className="auth-switch">
        Don't have an account?{' '}
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            onSwitchToSignup();
          }}
        >
          Sign up
        </a>
      </p>
    </form>
  );
};

export default LoginForm;

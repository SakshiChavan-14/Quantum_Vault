import React from 'react';
import { useFormik } from 'formik';
import { signupSchema } from '../../validation/signupSchema';
import { useAuth } from '../../hooks/useAuth';

const SignupForm = ({ onSwitchToLogin }) => {
  const { register, loading } = useAuth();

  const formik = useFormik({
    initialValues: {
      full_name: '',
      email: '',
      password: '',
      confirm_password: '',
      terms: false,
    },
    validationSchema: signupSchema,
    onSubmit: async (values) => {
      const result = await register({
        full_name: values.full_name,
        email: values.email,
        password: values.password,
        confirm_password: values.confirm_password,
      });
      if (result.success) {
        onSwitchToLogin();
      }
    },
  });

  return (
    <form id="signup-form" className="auth-form" onSubmit={formik.handleSubmit}>
      <div className="input-group">
        <input 
          type="text" 
          id="signup-name" 
          name="full_name"
          placeholder=" " 
          value={formik.values.full_name}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
        />
        <label htmlFor="signup-name">Full Name</label>
        {formik.touched.full_name && formik.errors.full_name && (
          <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '2px' }}>{formik.errors.full_name}</div>
        )}
      </div>

      <div className="input-group">
        <input 
          type="email" 
          id="signup-email" 
          name="email"
          placeholder=" " 
          value={formik.values.email}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
        />
        <label htmlFor="signup-email">Email</label>
        {formik.touched.email && formik.errors.email && (
          <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '2px' }}>{formik.errors.email}</div>
        )}
      </div>

      <div className="input-group">
        <input 
          type="password" 
          id="signup-password" 
          name="password"
          placeholder=" " 
          value={formik.values.password}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
        />
        <label htmlFor="signup-password">Password</label>
        {formik.touched.password && formik.errors.password && (
          <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '2px' }}>{formik.errors.password}</div>
        )}
      </div>

      <div className="input-group">
        <input 
          type="password" 
          id="signup-confirm" 
          name="confirm_password"
          placeholder=" " 
          value={formik.values.confirm_password}
          onChange={formik.handleChange}
          onBlur={formik.handleBlur}
        />
        <label htmlFor="signup-confirm">Confirm Password</label>
        {formik.touched.confirm_password && formik.errors.confirm_password && (
          <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '2px' }}>{formik.errors.confirm_password}</div>
        )}
      </div>

      <div>
        <label className="checkbox-label">
          <input 
            type="checkbox" 
            id="terms" 
            name="terms"
            checked={formik.values.terms}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
          />
          <span className="checkmark"></span>
          I agree to the Terms and Privacy Policy
        </label>
        {formik.touched.terms && formik.errors.terms && (
          <div style={{ color: '#ef4444', fontSize: '11px', marginTop: '2px' }}>{formik.errors.terms}</div>
        )}
      </div>

      <button type="submit" className="btn-auth" disabled={loading || formik.isSubmitting}>
        {loading || formik.isSubmitting ? 'Creating Account...' : 'Create account'}
      </button>

      <p className="auth-switch">
        Already have an account?{' '}
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            onSwitchToLogin();
          }}
        >
          Sign in
        </a>
      </p>
    </form>
  );
};

export default SignupForm;

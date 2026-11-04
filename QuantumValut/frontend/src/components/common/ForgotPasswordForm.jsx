import React from 'react';

const ForgotPasswordForm = ({ onSwitchToLogin }) => {
  return (
    <form id="forgot-form" className="auth-form" onSubmit={(e) => e.preventDefault()}>
      <div className="input-group">
        <input type="email" id="forgot-email" required placeholder=" " />
        <label htmlFor="forgot-email">Email</label>
      </div>
      <button type="submit" className="btn-auth">
        Send reset link
      </button>
      <p className="auth-back">
        <a
          href="#"
          onClick={(e) => {
            e.preventDefault();
            onSwitchToLogin();
          }}
        >
          Back to sign in
        </a>
      </p>
    </form>
  );
};

export default ForgotPasswordForm;

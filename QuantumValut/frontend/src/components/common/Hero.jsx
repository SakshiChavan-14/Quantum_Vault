import React from 'react';

const Hero = () => {
  return (
    <section className="hero">
      <div className="hero-background">
        <div className="floating-shape shape-1"></div>
        <div className="floating-shape shape-2"></div>
        <div className="floating-shape shape-3"></div>
      </div>
      <div className="hero-content">
        <h1>
          Your Files, <span className="gradient-text">Anywhere</span>
        </h1>
        <p>
          Store, share, and collaborate on files with anyone, anywhere. Create
          and edit documents with our powerful cloud editor.
        </p>
        <div className="hero-buttons">
          <a href="#" onClick={(e) => e.preventDefault()} className="btn-hero-primary">
            Start Free
          </a>
          <a href="#features" className="btn-hero-secondary">
            Learn More
          </a>
        </div>
        <div className="hero-stats">
          <div className="stat">
            <span className="stat-number">Unlimited</span>
            <span className="stat-label">Free Storage</span>
          </div>
          <div className="stat">
            <span className="stat-number">500K+</span>
            <span className="stat-label">Users</span>
          </div>
          <div className="stat">
            <span className="stat-number">99.9%</span>
            <span className="stat-label">Uptime</span>
          </div>
        </div>
      </div>
      <div className="hero-visual">
        <div className="floating-card card-1">
          <div className="card-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="#1a73e8">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z" />
            </svg>
          </div>
          <span>Documents</span>
        </div>
        <div className="floating-card card-2">
          <div className="card-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="#34a853">
              <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z" />
            </svg>
          </div>
          <span>Photos</span>
        </div>
        <div className="floating-card card-3">
          <div className="card-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="#fbbc04">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
            </svg>
          </div>
          <span>Secure</span>
        </div>
      </div>
    </section>
  );
};

export default Hero;
